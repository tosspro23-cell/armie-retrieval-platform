"""Provider implementations that consume Elasticsearch indexes at query time."""

from __future__ import annotations

import time
import os
from typing import Any

from armie_retrieval.indexing.elasticsearch.client import ElasticsearchClient
from armie_retrieval.models import Query, ResultItem, RetrievalPlan, RetrievalResult
from armie_retrieval.constraints import ElasticsearchConstraintCompiler, registry_snapshot
from armie_retrieval.indexing.constraint_projection import PROJECTION_SCHEMA_VERSION
from armie_retrieval.indexing.elasticsearch.identity import configured_dense_index

PROJECTION_IMPLEMENTATION = "constraint-projection-0.2-gate6b"
EXPECTED_MAPPING_FINGERPRINT = "e7f3acf23f2d90964e4e771da14bb033b93d386a6e73c4d351a91a40cfba5a0d"
DATASET_LINEAGE = "v2-realism-full"
DATASET_CHECKSUM = "514ab2f7bd6378a51d1915f8f399506a61e6e9589a61eef674eccc1a8043d4bc"
EMBEDDING_MODEL = "BAAI/bge-m3"
PROVENANCE_SCHEMA_VERSION = "constraint-execution-provenance-v1"


class _BaseElasticsearchRetriever:
    capabilities = frozenset({"elasticsearch", "metadata_filter"})

    def __init__(self, client: ElasticsearchClient, *, index: str) -> None:
        self.client = client
        self.index = index

    def _result(self, query: Query, plan: RetrievalPlan, hits: list[dict[str, Any]], started: float, score_type: str) -> RetrievalResult:
        items = tuple(ResultItem(
            id=str(hit.get("_id")), object_type="expert", title=hit.get("_source", {}).get("display_name", str(hit.get("_id"))),
            content=hit.get("_source", {}).get("summary", ""), metadata=hit.get("_source", {}), score=float(hit.get("_score") or 0.0),
            signals={score_type: float(hit.get("_score") or 0.0)}, sources=(self.name,),
        ) for hit in hits)
        return RetrievalResult(items=items, plan_id=plan.plan_id, strategy=plan.strategy, latency_ms=(time.perf_counter() - started) * 1000,
                               provenance={"retrievers": [self.name], "provider": self.name, "index": self.index, "score_type": score_type}, trace=(f"retrieved:{self.name}",))


class ElasticsearchBM25Retriever(_BaseElasticsearchRetriever):
    name = "elasticsearch_bm25"
    capabilities = frozenset({"sparse", "elasticsearch", "bm25", "metadata_filter"})

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        should = [{"match": {field: {"query": query.text, "boost": boost}}} for field, boost in (
            ("skills", 4.0), ("technologies", 4.0), ("project_titles", 3.0), ("project_descriptions", 2.5),
            ("industries", 2.0), ("roles", 2.0), ("headline", 1.5), ("summary", 1.0),
        )]
        filters = [{"term": {key: value}} for key, value in query.filters.items()]
        payload = {"size": int(plan.parameters.get("retrieval_candidate_k", plan.top_k)), "query": {"bool": {"should": should, "minimum_should_match": 1, "filter": filters}}}
        hits = self.client.request("POST", f"{self.index}/_search", json=payload).json().get("hits", {}).get("hits", [])
        return self._result(query, plan, hits, started, "bm25_score")


class ElasticsearchDenseRetriever(_BaseElasticsearchRetriever):
    name = "elasticsearch_dense"
    capabilities = frozenset({"dense", "elasticsearch", "knn"})

    def __init__(self, client: ElasticsearchClient, *, index: str | None = None, embedding_provider, require_compatible_index: bool = True) -> None:
        super().__init__(client, index=index or configured_dense_index())
        self.embedding_provider = embedding_provider
        self.require_compatible_index = require_compatible_index

    def _index_compatibility(self) -> dict[str, Any]:
        """Validate the C1 projection before issuing a filtered kNN request.

        Test doubles and non-Elasticsearch adapters are intentionally exempt;
        a real ``ElasticsearchClient`` must prove the projection metadata.
        """
        if not self.require_compatible_index or not isinstance(self.client, ElasticsearchClient):
            return {"status": "not_checked", "reason": "non_elasticsearch_adapter"}
        try:
            alias_body = None
            try:
                alias_body = self.client.request("GET", f"_alias/{self.index}").json()
            except Exception:
                # A physical index override remains supported for local rebuilds.
                alias_body = None
            body = self.client.request("GET", f"{self.index}/_mapping").json()
            mappings = next(iter(body.values())).get("mappings", {}) if body else {}
            meta = mappings.get("_meta", {})
            props = mappings.get("properties", {})
            embedding = props.get("embedding", {})
            missing = [field for field in ("years_experience", "industries", "roles", "locations", "seniority_rank", "embedding") if field not in props]
            if meta.get("projection_schema_version") != PROJECTION_SCHEMA_VERSION:
                return {"status": "incompatible", "reason": "projection_schema_version_mismatch", "observed": meta.get("projection_schema_version"), "expected": PROJECTION_SCHEMA_VERSION}
            observed_fingerprint = meta.get("mapping_fingerprint")
            if missing or embedding.get("dims") != 1024 or (observed_fingerprint and observed_fingerprint != EXPECTED_MAPPING_FINGERPRINT):
                return {"status": "incompatible", "reason": "projection_fields_or_embedding_mismatch", "missing_fields": missing, "embedding_dimensions": embedding.get("dims"), "expected_dimensions": 1024}
            return {"status": "compatible", "logical_index": self.index, "resolved_indices": sorted(alias_body or body), "projection_schema_version": meta.get("projection_schema_version"), "projection_implementation_version": meta.get("projection_implementation_version"), "mapping_version": meta.get("mapping_version"), "embedding_model": meta.get("embedding_model"), "embedding_dimensions": embedding.get("dims"), "mapping_fingerprint": meta.get("mapping_fingerprint"), "mapping_fingerprint_status": "verified" if meta.get("mapping_fingerprint") else "unavailable_legacy_metadata"}
        except Exception as exc:
            return {"status": "incompatible", "reason": "index_metadata_unavailable", "error": str(exc)[:240]}

    @staticmethod
    def _semantic_trace(compiled) -> list[dict[str, Any]]:
        return [{"constraint_id": item.constraint_id, "canonical_field": item.canonical_field, "projection_field": item.projection_field, "operator": item.operation.value if item.operation else None, "normalized_value": item.value, "polarity": item.polarity.value, "scope": item.scope, "executable": item.executable, "reason": item.reason, "dsl_applied": item.dsl is not None} for item in compiled]

    def _empty_contract_result(self, query, plan, started, *, compiled, state: str, error_category: str, compatibility: dict[str, Any] | None = None, contract=None):
        contract = contract or query.retrieval_contract
        diagnostics = {"contract_id": getattr(contract, "contract_id", None), "contract_version": getattr(contract, "contract_version", None), "validation_state": state, "error_category": error_category, "supported_constraint_count": sum(item.executable for item in compiled), "excluded_constraint_count": sum(item.polarity.value == "EXCLUDED" for item in compiled), "unsupported_constraint_count": sum(not item.executable for item in compiled), "constraint_trace": self._semantic_trace(compiled), "unknown_policy": "UNKNOWN does not satisfy hard constraints", "candidate_pool_count": 0, "eligible_candidate_count": 0, "requested_k": plan.top_k, "returned_k": 0, "requested_top_k": plan.top_k, "returned_result_count": 0, "strict_shortfall_count": plan.top_k, "shortfall": {"requested": plan.top_k, "returned": 0, "count": plan.top_k, "reason": error_category}}
        provenance = {"provenance_schema_version": PROVENANCE_SCHEMA_VERSION, "retrievers": [self.name], "provider": self.name, "index": self.index, "index_identity": self.index, "strategy_identity": "C1", "runtime_strategy": "constraint_prefilter", "runtime_source": "elasticsearch_native_prefilter", "contract_state": state, "contract_schema_version": getattr(contract, "contract_version", None), "error_category": error_category, "requested_k": plan.top_k, "candidate_pool_count": 0, "eligible_candidate_count": 0, "returned_k": 0, "shortfall": diagnostics["shortfall"], "projection_identity": {"implementation": PROJECTION_IMPLEMENTATION, "schema_version": PROJECTION_SCHEMA_VERSION, "mapping_fingerprint": EXPECTED_MAPPING_FINGERPRINT, "dataset_lineage": DATASET_LINEAGE, "dataset_checksum": DATASET_CHECKSUM}, "embedding_identity": {"model": EMBEDDING_MODEL, "dimensions": 1024}, "ann_configuration": {"field": "embedding"}, "filter_applied": False, "constraint_diagnostics": diagnostics, "capability_registry": registry_snapshot(), "index_compatibility": compatibility or {"status": "not_checked"}, "latency_stages": {"contract_validation_ms": (time.perf_counter() - started) * 1000, "dense_filter_execution_ms": 0.0, "total_retrieval_ms": (time.perf_counter() - started) * 1000}}
        return RetrievalResult(items=(), plan_id=plan.plan_id, strategy=plan.strategy, latency_ms=(time.perf_counter() - started) * 1000, provenance=provenance, trace=(f"constraint:{error_category.lower()}",))

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        validation_started = time.perf_counter()
        contract = query.retrieval_contract or plan.parameters.get("retrieval_contract")
        compiled = ()
        if contract is not None:
            compiled = ElasticsearchConstraintCompiler().compile(contract)
            deferred = bool(getattr(contract, "temporal_constraints", ())) or bool(getattr(contract, "relationship_constraints", ()))
            if deferred or any(not item.executable for item in compiled):
                invalid = any(item.reason in {"INVALID_CONTRACT", "INVALID_OPERATOR", "TYPE_MISMATCH", "CONTRADICTION"} for item in compiled)
                return self._empty_contract_result(query, plan, started, compiled=compiled, contract=contract, state="INVALID_CONTRACT" if invalid else "NON_EXECUTABLE", error_category="INVALID_CONTRACT" if invalid else "UNSUPPORTED_CONSTRAINT", compatibility={"status": "not_checked"})
            compatibility = self._index_compatibility()
            if compatibility.get("status") == "incompatible":
                return self._empty_contract_result(query, plan, started, compiled=compiled, contract=contract, state="INDEX_INCOMPATIBLE", error_category="INDEX_INCOMPATIBLE", compatibility=compatibility)
        validation_latency_ms = (time.perf_counter() - validation_started) * 1000
        filter_started = time.perf_counter()
        vector = self.embedding_provider.embed([query.text])[0]
        candidate_k = int(plan.parameters.get("retrieval_candidate_k", plan.top_k))
        payload = {
            "size": candidate_k,
            "knn": {
                "field": "embedding",
                "query_vector": vector,
                "k": candidate_k,
                "num_candidates": candidate_k * 2,
            },
        }
        filters = [item.dsl for item in compiled if item.dsl]
        if filters:
            payload["knn"]["filter"] = {"bool": {"filter": filters}}
        filter_compile_latency_ms = (time.perf_counter() - filter_started) * 1000
        hits = self.client.request("POST", f"{self.index}/_search", json=payload).json().get("hits", {}).get("hits", [])
        # Elasticsearch returns the candidate pool. Product semantics are the
        # strict final Top-K and must never leak the pool into the response.
        candidate_pool_count = len(hits)
        eligible_candidate_count = len(hits)  # native C1 filter already applied
        returned_hits = hits[: plan.top_k]
        result = self._result(query, plan, returned_hits, started, "elasticsearch_dense_score")
        provenance = dict(result.provenance)
        provenance["provenance_schema_version"] = PROVENANCE_SCHEMA_VERSION
        provenance["strategy_identity"] = "C1" if contract is not None else "C0"
        provenance["runtime_strategy"] = "constraint_prefilter" if contract is not None else "dense"
        provenance["runtime_source"] = "elasticsearch_native_prefilter" if contract is not None else "elasticsearch_dense"
        shortfall = max(0, plan.top_k - eligible_candidate_count)
        diagnostics_error = "NO_RESULTS" if not returned_hits and contract is not None else ("STRICT_SHORTFALL" if shortfall else None)
        provenance["constraint_diagnostics"] = {"contract_id": getattr(contract, "contract_id", None), "contract_version": getattr(contract, "contract_version", None), "validation_state": "VALID" if contract is not None else "NOT_REQUESTED", "error_category": diagnostics_error, "hard_constraint_count": len(getattr(contract, "hard_constraints", ())), "executable_constraint_count": sum(item.executable for item in compiled), "excluded_constraint_count": sum(item.polarity.value == "EXCLUDED" for item in compiled), "unsupported_constraint_count": 0, "constraint_trace": self._semantic_trace(compiled), "unknown_policy": "UNKNOWN does not satisfy hard constraints", "candidate_count_before_filter": candidate_pool_count, "candidate_count_after_filter": eligible_candidate_count, "candidate_pool_count": candidate_pool_count, "eligible_candidate_count": eligible_candidate_count, "requested_k": plan.top_k, "returned_k": len(returned_hits), "requested_top_k": plan.top_k, "returned_result_count": len(returned_hits), "strict_shortfall_count": shortfall, "shortfall": {"requested": plan.top_k, "returned": len(returned_hits), "count": shortfall, "reason": "eligible_universe_or_retrieval_shortfall" if shortfall else None}}
        provenance["capability_registry"] = registry_snapshot()
        provenance["index_compatibility"] = compatibility if contract is not None else {"status": "not_checked"}
        provenance["index_identity"] = self.index
        provenance["projection_identity"] = {"implementation": PROJECTION_IMPLEMENTATION, "schema_version": PROJECTION_SCHEMA_VERSION, "mapping_fingerprint": EXPECTED_MAPPING_FINGERPRINT, "dataset_lineage": DATASET_LINEAGE, "dataset_checksum": DATASET_CHECKSUM}
        provenance["embedding_identity"] = {"model": getattr(self.embedding_provider, "model_name", EMBEDDING_MODEL), "dimensions": getattr(self.embedding_provider, "_dimension", None) or 1024}
        provenance["ann_configuration"] = {"field": "embedding", "k": candidate_k, "num_candidates": candidate_k * 2}
        provenance["filter_applied"] = bool(filters)
        provenance["contract_state"] = "VALID" if contract is not None else "NOT_REQUESTED"
        provenance["contract_schema_version"] = getattr(contract, "contract_version", None)
        provenance["error_category"] = diagnostics_error
        provenance["requested_k"] = plan.top_k
        provenance["candidate_pool_count"] = candidate_pool_count
        provenance["eligible_candidate_count"] = eligible_candidate_count
        provenance["returned_k"] = len(returned_hits)
        provenance["shortfall"] = {"requested": plan.top_k, "returned": len(returned_hits), "count": max(0, plan.top_k - len(returned_hits)), "reason": "eligible_universe_or_retrieval_shortfall" if shortfall else None}
        provenance["latency_stages"] = {"contract_validation_ms": validation_latency_ms, "filter_compile_ms": filter_compile_latency_ms, "dense_filter_execution_ms": result.latency_ms, "total_retrieval_ms": result.latency_ms}
        return RetrievalResult(items=result.items, plan_id=result.plan_id, strategy=result.strategy, latency_ms=result.latency_ms, provenance=provenance, trace=(*result.trace, "constraint:c1_prefilter" if contract is not None else "constraint:c0_unfiltered"))


class ElasticsearchHybridRetriever:
    """Real Elasticsearch BM25+dense retrieval with ARMIE RRF semantics.

    The component is registered as one runtime capability, while retaining
    both child providers so the shared trace collector can expose every source
    contribution and rank. Raw BM25 and dense scores are never normalized or
    compared; only source ranks participate in RRF.
    """

    name = "elasticsearch_hybrid"
    capabilities = frozenset({"hybrid", "elasticsearch", "rrf"})

    def __init__(self, dense: ElasticsearchDenseRetriever, sparse: ElasticsearchBM25Retriever, *, rrf_k: int = 60) -> None:
        self._dense = dense
        self._sparse = sparse
        self._rrf_k = rrf_k

    def retrieve(self, query: Query, plan: RetrievalPlan) -> RetrievalResult:
        started = time.perf_counter()
        dense_result = self._dense.retrieve(query, plan)
        sparse_result = self._sparse.retrieve(query, plan)
        fusion_started = time.perf_counter()
        scores: dict[str, float] = {}
        items: dict[str, ResultItem] = {}
        contributions: dict[str, dict[str, dict[str, float | int | str]]] = {}
        for source in (dense_result, sparse_result):
            source_name = source.provenance.get("provider", "unknown")
            score_semantic = source.provenance.get("score_type", "provider_score")
            for rank, item in enumerate(source.items, start=1):
                contribution = 1.0 / (self._rrf_k + rank)
                scores[item.id] = scores.get(item.id, 0.0) + contribution
                items.setdefault(item.id, item)
                contributions.setdefault(item.id, {})[str(source_name)] = {
                    "source_rank": rank,
                    "source_score": item.score,
                    "source_score_semantic": str(score_semantic),
                    "rrf_contribution": contribution,
                }
        ordered_ids = sorted(scores, key=lambda item_id: (-scores[item_id], item_id))
        fusion_limit = int(plan.parameters.get("fusion_candidate_k", plan.parameters.get("retrieval_candidate_k", plan.top_k)))
        fused = tuple(items[item_id].with_score(scores[item_id], signals={"rrf": scores[item_id]}) for item_id in ordered_ids[:fusion_limit])
        fusion_latency_ms = (time.perf_counter() - fusion_started) * 1000
        fusion_candidates = {
            item_id: {**values, "total_fused_score": scores[item_id], "fusion_rank": rank, "deduplicated": len(values) > 1}
            for rank, item_id in enumerate(ordered_ids[:fusion_limit], start=1)
            for values in [contributions[item_id]]
        }
        return RetrievalResult(
            items=fused,
            plan_id=plan.plan_id,
            strategy=plan.strategy,
            latency_ms=(time.perf_counter() - started) * 1000,
            provenance={
                "retrievers": [self._sparse.name, self._dense.name],
                "fusion": "reciprocal_rank_fusion",
                "rrf_k": self._rrf_k,
                "fusion_candidate_k": fusion_limit,
                "fusion_latency_ms": fusion_latency_ms,
                "fusion_candidates": fusion_candidates,
            },
            trace=(f"retrieved:{self._sparse.name}", f"retrieved:{self._dense.name}", "fused:rrf"),
        )
