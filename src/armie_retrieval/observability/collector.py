"""Optional trace collection at runtime boundaries; no terminal rendering lives here."""

from __future__ import annotations

import re
import time
from dataclasses import replace
from typing import Any, Mapping

from armie_retrieval.models import Query, RetrievalPlan, RetrievalResult, ResultItem

from .models import CandidateTrace, FusionTrace, PlannerTrace, ProcessorStageTrace, RankingTrace, RerankerTrace, RetrievalTrace, RetrieverTrace

TOKEN = re.compile(r"[a-z0-9]+")


class TraceCollector:
    """Per-request mutable collector. It is never global runtime state."""

    def __init__(self, query: Query, plan: RetrievalPlan, planner_trace: PlannerTrace, *, query_id: str | None = None) -> None:
        self.query = query
        self.plan = plan
        self.planner_trace = planner_trace
        self.query_id = query_id or query.request_id
        self.retrievers: list[RetrieverTrace] = []
        self.fusion: FusionTrace | None = None
        self._processor_names: list[str] = []
        self._processor_stages: list[ProcessorStageTrace] = []
        self._reranking: RerankerTrace | None = None
        self._final_result: RetrievalResult | None = None
        self.warnings: list[str] = []

    def record_retrieval(self, retriever: Any, result: RetrievalResult) -> None:
        if getattr(retriever, "name", "") == "hybrid":
            self._record_hybrid(retriever, result)
            return
        self.retrievers.append(self._retriever_trace(retriever, result))

    def record_processor(self, processor: Any, before: RetrievalResult, after: RetrievalResult) -> None:
        name = getattr(processor, "name", type(processor).__name__)
        self._processor_names.append(name)
        before_ids, after_ids = tuple(item.id for item in before.items), tuple(item.id for item in after.items)
        before_scores = {item.id: item.score for item in before.items}
        after_scores = {item.id: item.score for item in after.items}
        before_rank = {item_id: rank for rank, item_id in enumerate(before_ids, 1)}
        after_rank = {item_id: rank for rank, item_id in enumerate(after_ids, 1)}
        rank_changes = {item_id: after_rank[item_id] - before_rank[item_id] for item_id in after_ids if item_id in before_rank and after_rank[item_id] != before_rank[item_id]}
        rerank_result = getattr(processor, "last_rerank_result", None)
        # Reranking has three distinct, externally meaningful boundaries.  Do
        # not collapse them into the generic processor mutation record.
        if rerank_result is None:
            self._processor_stages.append(ProcessorStageTrace(
            processor_name=name, candidate_count_before=len(before.items), candidate_count_after=len(after.items),
            order_before=before_ids, order_after=after_ids, scores_before=before_scores, scores_after=after_scores,
            removed_ids=tuple(item_id for item_id in before_ids if item_id not in after_rank), rank_changes=rank_changes,
            changed_scores=any(before_scores.get(item_id) != after_scores.get(item_id) for item_id in set(before_scores) & set(after_scores)),
            changed_order=before_ids != after_ids, truncated=len(after.items) < len(before.items),
            ))
        if rerank_result is not None:
            selection = getattr(processor, "selection", None)
            requested = getattr(selection, "requested", getattr(rerank_result, "provider", name))
            actual = getattr(rerank_result, "provider", getattr(selection, "actual", name))
            scored_items = getattr(rerank_result, "scored_items", getattr(rerank_result, "items", ()))
            pre_rerank_ids = tuple(item.id for item in getattr(processor, "last_input_items", before.items))
            selected_items = tuple(getattr(processor, "last_input_items", before.items))
            scored_result_items = tuple(row.item.with_score(row.raw_relevance_score) for row in scored_items)
            self._processor_stages.extend((
                self._stage("rerank_candidate_selection", before.items, selected_items),
                self._stage("reranker_processing", selected_items, scored_result_items),
                self._stage("final_top_k_selection", scored_result_items, after.items),
            ))
            final_ids = set(after_rank)
            initial_top_k = set(pre_rerank_ids[:len(after.items)])
            self._reranking = RerankerTrace(
                requested_provider=requested, actual_provider=actual, model=getattr(rerank_result, "model", None),
                candidate_count_in=len(getattr(processor, "last_input_items", before.items)),
                candidate_count_after_rerank=len(scored_items), final_candidate_count=len(after.items),
                candidates=tuple(
                    {
                        "expert_id": row.item.id,
                        "pre_rerank_rank": row.input_rank,
                        "pre_rerank_score": before_scores.get(row.item.id),
                        "reranker_raw_score": row.raw_relevance_score,
                        "reranker_rank": row.output_rank,
                        "final_rank": after_rank.get(row.item.id),
                        "rank_change": row.output_rank - row.input_rank,
                        "rank_improvement": row.input_rank - row.output_rank,
                        "entered_final_top_k": row.item.id in final_ids and row.item.id not in initial_top_k,
                        "exited_final_top_k": row.item.id in initial_top_k and row.item.id not in final_ids,
                    }
                    for row in scored_items
                ),
                model_available=getattr(rerank_result, "model_available", True),
                fallback_reason=getattr(selection, "fallback_reason", None), device=getattr(rerank_result, "device", None),
                batch_size=getattr(rerank_result, "batch_size", None), model_load_latency_ms=getattr(rerank_result, "model_load_latency_ms", 0.0),
                inference_latency_ms=getattr(rerank_result, "inference_latency_ms", 0.0), warnings=getattr(rerank_result, "warnings", ()),
                post_rerank_top_k=len(getattr(rerank_result, "items", ())), final_processor_output_count=len(after.items),
                fusion_output_candidates=len(before.items), rerank_input_candidates=len(selected_items),
                reranker_processed_candidates=len(scored_items), post_rerank_candidates=len(scored_items),
                final_top_k_candidates=len(after.items), scoring_method=getattr(rerank_result, "scoring_method", "none"),
                fallback_diagnostic=getattr(rerank_result, "fallback_diagnostic", None),
            )
        if rerank_result is None and len(before.items) != len(after.items):
            self.warnings.append(
                f"{getattr(processor, 'name', type(processor).__name__)} changed candidate count "
                f"from {len(before.items)} to {len(after.items)}"
            )
        if rerank_result is not None:
            if len(before.items) > len(selected_items):
                self.warnings.append(f"Rerank candidate selection truncated {len(before.items)} candidates to {len(selected_items)}.")
            if len(scored_items) > len(after.items):
                self.warnings.append(f"Final Top-K selection truncated {len(scored_items)} candidates to {len(after.items)}.")

    @staticmethod
    def _stage(name: str, before_items: tuple[ResultItem, ...], after_items: tuple[ResultItem, ...]) -> ProcessorStageTrace:
        before_ids, after_ids = tuple(item.id for item in before_items), tuple(item.id for item in after_items)
        before_scores, after_scores = ({item.id: item.score for item in before_items}, {item.id: item.score for item in after_items})
        before_rank, after_rank = ({item_id: rank for rank, item_id in enumerate(before_ids, 1)}, {item_id: rank for rank, item_id in enumerate(after_ids, 1)})
        return ProcessorStageTrace(name, len(before_items), len(after_items), before_ids, after_ids, before_scores, after_scores,
            removed_ids=tuple(item_id for item_id in before_ids if item_id not in after_rank),
            rank_changes={item_id: after_rank[item_id] - before_rank[item_id] for item_id in after_ids if item_id in before_rank and after_rank[item_id] != before_rank[item_id]},
            changed_scores=any(before_scores.get(item_id) != after_scores.get(item_id) for item_id in set(before_scores) & set(after_scores)),
            changed_order=before_ids != after_ids, truncated=len(after_items) < len(before_items))

    def record_final(self, result: RetrievalResult) -> None:
        self._final_result = result

    def build(self, *, ground_truth=None, evaluation=None) -> RetrievalTrace:
        if self._final_result is None:
            raise RuntimeError("Trace collection ended without a final RetrievalResult")
        final_candidates = self._candidate_traces(self._final_result.items, "final")
        fusion_contributions = {
            candidate.expert_id: candidate.contributions
            for candidate in self.fusion.candidates
        } if self.fusion else {}
        final_candidates = tuple(
            replace(candidate, contributions=fusion_contributions.get(candidate.expert_id, {}))
            for candidate in final_candidates
        )
        relevance = set(ground_truth.relevant_ids) if ground_truth else set()
        if ground_truth:
            final_candidates = tuple(
                replace(candidate, relevant=candidate.expert_id in relevance)
                for candidate in final_candidates
            )
        ranking = RankingTrace(final_candidates, tuple(self._processor_names))
        timing = {"planner": self.planner_trace.latency_ms, "retrieval": self._final_result.latency_ms}
        return RetrievalTrace(
            schema_version="0.2.3",
            query_id=self.query_id,
            planner=self.planner_trace,
            retrievers=tuple(self.retrievers),
            fusion=self.fusion,
            ranking=ranking,
            ground_truth=ground_truth,
            evaluation=evaluation,
            timing_ms=timing,
            warnings=tuple(self.warnings),
            processor_stages=tuple(self._processor_stages),
            reranking=self._reranking,
        )

    def _record_hybrid(self, retriever: Any, result: RetrievalResult) -> None:
        try:
            dense_result = retriever._dense.retrieve(self.query, self.plan)
            sparse_result = retriever._sparse.retrieve(self.query, self.plan)
            dense_trace = self._retriever_trace(retriever._dense, dense_result)
            sparse_trace = self._retriever_trace(retriever._sparse, sparse_result)
            self.retrievers.extend((dense_trace, sparse_trace))
            source_traces = (dense_trace, sparse_trace)
            contributions: dict[str, dict[str, dict[str, float]]] = {}
            for source in source_traces:
                for candidate in source.candidates:
                    contribution = 1 / (getattr(retriever, "_rrf_k", 60) + candidate.rank)
                    contributions.setdefault(candidate.expert_id, {})[source.name] = {
                        "rank": float(candidate.rank),
                        "raw_score": candidate.raw_score,
                        "normalized_score": candidate.normalized_score,
                        "fusion_contribution": contribution,
                    }
            fused = []
            for candidate in self._candidate_traces(result.items, "hybrid"):
                fused.append(replace(candidate, contributions=contributions.get(candidate.expert_id, {})))
            self.fusion = FusionTrace(
                method="reciprocal_rank_fusion",
                candidates=tuple(fused),
                deduplicated_ids=tuple(sorted(candidate_id for candidate_id, values in contributions.items() if len(values) > 1)),
                rrf_k=getattr(retriever, "_rrf_k", 60),
            )
        except Exception as exc:  # tracing must never break retrieval execution
            self.warnings.append(f"Hybrid source trace unavailable: {exc}")
            self.retrievers.append(self._retriever_trace(retriever, result))

    def _retriever_trace(self, retriever: Any, result: RetrievalResult) -> RetrieverTrace:
        items = result.items
        candidate_limit = int(self.plan.parameters.get("retrieval_candidate_k", self.plan.top_k * int(self.plan.parameters.get("candidate_multiplier", 1))))
        return RetrieverTrace(
            name=getattr(retriever, "name", type(retriever).__name__),
            strategy=self.plan.strategy,
            latency_ms=result.latency_ms,
            candidate_count_before_truncation=len(items),
            candidate_limit=candidate_limit,
            candidates=self._candidate_traces(items, getattr(retriever, "name", type(retriever).__name__), retriever),
        )

    def _candidate_traces(self, items: tuple[ResultItem, ...], retriever_name: str, retriever: Any | None = None) -> tuple[CandidateTrace, ...]:
        maximum = max((item.score for item in items), default=0.0) or 1.0
        candidates = []
        for rank, item in enumerate(items, 1):
            evidence = _evidence(self.query.text, item, retriever_name, retriever)
            graph = _graph_coverage(self.query, item, retriever_name, retriever, evidence)
            candidates.append(CandidateTrace(
                expert_id=item.id,
                title=item.title,
                retriever=retriever_name,
                rank=rank,
                raw_score=item.score,
                normalized_score=item.score / maximum,
                matched_terms=_matched_terms(self.query.text, item),
                matched_fields=_matched_fields(self.query.text, item),
                evidence=evidence,
                scoring_components=_scoring_components(self.query.text, item, retriever_name),
                final_score=item.score if retriever_name == "final" else None,
                final_rank=rank if retriever_name == "final" else None,
                **graph,
            ))
        return tuple(candidates)


def _matched_terms(query: str, item: ResultItem) -> tuple[str, ...]:
    query_terms = set(TOKEN.findall(query.lower()))
    return tuple(sorted(query_terms & set(TOKEN.findall(_all_text(item).lower()))))


def _matched_fields(query: str, item: ResultItem) -> tuple[str, ...]:
    query_terms = set(TOKEN.findall(query.lower()))
    fields = {"title": item.title, "content": item.content, **{str(key): str(value) for key, value in item.metadata.items()}}
    return tuple(sorted(name for name, value in fields.items() if query_terms & set(TOKEN.findall(value.lower()))))


def _evidence(query: str, item: ResultItem, retriever_name: str, retriever: Any | None) -> tuple[str, ...]:
    if "graph" in retriever_name and retriever is not None:
        provider = getattr(retriever, "_provider", None)
        graph = getattr(provider, "graph", None)
        if graph is not None:
            evidence: list[str] = []
            terms = set(TOKEN.findall(query.lower()))
            for node_id, attributes in graph.nodes(data=True):
                if not (terms & set(TOKEN.findall(str(attributes.get("label", "")).lower()))):
                    continue
                for edge in graph.get_edge_data(node_id, item.id, default={}).values():
                    evidence.append(f"{attributes.get('label')} --{edge.get('relation')}--> {item.id}")
            return tuple(sorted(set(evidence)))
    fields = _matched_fields(query, item)
    if not fields:
        return ()
    return (f"Query terms appear in indexed fields: {', '.join(fields)}",)


def _scoring_components(query: str, item: ResultItem, retriever_name: str) -> dict[str, float]:
    components = dict(item.signals)
    if "sparse" in retriever_name or "keyword" in retriever_name:
        terms = TOKEN.findall(_all_text(item).lower())
        for term in _matched_terms(query, item):
            components[f"term_frequency:{term}"] = float(terms.count(term))
    return components


def _all_text(item: ResultItem) -> str:
    return " ".join((item.title, item.content, *(str(value) for value in item.metadata.values())))


def _graph_coverage(query: Query, item: ResultItem, retriever_name: str, retriever: Any | None, evidence: tuple[str, ...]) -> dict[str, Any]:
    if "graph" not in retriever_name or retriever is None:
        return {}
    provider = getattr(retriever, "_provider", None)
    graph = getattr(provider, "graph", None)
    if graph is None:
        return {}
    query_terms = set(TOKEN.findall(query.text.lower()))
    expected = []
    matched_nodes = []
    for _, attributes in graph.nodes(data=True):
        label = str(attributes.get("label", ""))
        label_terms = set(TOKEN.findall(label.lower()))
        if label_terms and label_terms <= query_terms:
            expected.append(label)
            if any(label in edge for edge in evidence):
                matched_nodes.append(label)
    for key, value in query.filters.items():
        constraint = f"{key} = {value}"
        expected.append(constraint)
        if str(item.metadata.get(key, "")).lower() == str(value).lower():
            matched_nodes.append(constraint)
    expected = tuple(dict.fromkeys(expected))
    matched = tuple(dict.fromkeys(matched_nodes))
    missing = tuple(item for item in expected if item not in matched)
    return {
        "expected_constraints": expected,
        "matched_constraints": matched,
        "missing_constraints": missing,
        "constraint_coverage_ratio": (len(matched) / len(expected)) if expected else None,
        "matched_graph_nodes": matched,
        "matched_graph_edges": evidence,
    }
