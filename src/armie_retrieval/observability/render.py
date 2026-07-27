"""Compact terminal rendering for structured retrieval traces."""

from __future__ import annotations

from .models import RetrievalTrace


def render_terminal(trace: RetrievalTrace, *, verbose: bool = False) -> str:
    lines = [
        "ARMIE Retrieval Trace",
        "=" * 72,
        f"1. Query\n   id={trace.query_id}\n   text={trace.planner.raw_query}",
        "2. Planner\n"
        f"   requested={trace.planner.requested_provider or trace.planner.provider} actual={trace.planner.actual_provider or trace.planner.provider} model={trace.planner.requested_model or trace.planner.model or 'n/a'} "
        f"strategy={trace.planner.selected_strategy} planner_requested_top_k={trace.planner.planner_requested_top_k or trace.planner.requested_top_k}\n"
        f"   retrievers={', '.join(trace.planner.selected_retrievers)} "
        f"processors={', '.join(trace.planner.parsed_plan.get('processor_names', ())) or 'none'}\n"
        f"   skills={', '.join(trace.planner.extracted_skills) or 'n/a'} "
        f"industries={', '.join(trace.planner.extracted_industries) or 'n/a'}\n"
        f"   constraint_types={', '.join(trace.planner.constraint_types) or 'n/a'} "
        f"reason_codes={', '.join(trace.planner.reason_codes) or 'n/a'} latency={trace.planner.latency_ms:.2f}ms\n"
        f"   retrieval_candidate_k={trace.planner.retrieval_candidate_k} rerank_candidate_k={trace.planner.rerank_candidate_k} "
        f"effective_final_top_k={trace.planner.effective_final_top_k} effective_top_k_source={trace.planner.effective_top_k_source}",
    ]
    if verbose:
        capabilities = "\n".join(f"   - {name}: {description}" for name, description in trace.planner.available_capabilities.items())
        lines[-1] += f"\n   available capabilities:\n{capabilities or '   - unavailable'}"
    if trace.planner.warnings:
        lines[-1] += "\n   routing warnings:\n   - " + "\n   - ".join(trace.planner.warnings)
    sections = (("Dense", ("dense",)), ("Keyword", ("sparse", "keyword")), ("Graph", ("graph",)))
    for index, (label, identifiers) in enumerate(sections, 3):
        matching = next((item for item in trace.retrievers if any(identifier in item.name for identifier in identifiers)), None)
        lines.append(_retriever_section(index, label, matching, verbose))
    next_section = 6
    if trace.fusion:
        lines.append(_fusion_section(next_section, trace, verbose))
        next_section += 1
    if trace.reranking:
        lines.append(_reranking_section(next_section, trace, verbose))
        next_section += 1
    lines.append(_ranking_section(next_section, trace, verbose))
    next_section += 1
    if trace.ground_truth:
        lines.append(_ground_truth_section(next_section, trace))
        next_section += 1
    if trace.evaluation:
        lines.append(_evaluation_section(next_section, trace))
        next_section += 1
    lines.append(f"{next_section}. Timing Summary\n   planner={trace.timing_ms['planner']:.2f}ms retrieval={trace.timing_ms['retrieval']:.2f}ms")
    if trace.warnings or trace.planner.warnings:
        lines.append(f"{next_section + 1}. Warnings\n   " + "\n   ".join((*trace.planner.warnings, *trace.warnings)))
    return "\n\n".join(lines)


def _reranking_section(number: int, trace: RetrievalTrace, verbose: bool) -> str:
    rerank = trace.reranking
    assert rerank is not None
    header = (
        f"{number}. Reranking\n   requested={rerank.requested_provider} actual={rerank.actual_provider} model={rerank.model or 'n/a'}\n"
        f"   fusion_output_candidates={rerank.fusion_output_candidates}\n"
        f"   rerank_input_candidates={rerank.rerank_input_candidates}\n"
        f"   reranker_processed_candidates={rerank.reranker_processed_candidates}\n"
        f"   post_rerank_candidates={rerank.post_rerank_candidates}\n"
        f"   final_top_k_candidates={rerank.final_top_k_candidates} final_results={rerank.final_processor_output_count}\n"
        f"   input_candidates={rerank.rerank_input_candidates} processed_candidates={rerank.reranker_processed_candidates} "
        f"post_rerank_candidates={rerank.post_rerank_candidates} final_results={rerank.final_processor_output_count}\n"
        f"   scoring_method={rerank.scoring_method}"
    )
    if rerank.scoring_method == "cross_encoder":
        header += (
            f" cross_encoder_scored={rerank.reranker_processed_candidates}\n"
            f"   device={rerank.device or 'n/a'} batch_size={rerank.batch_size or 'n/a'}\n"
            f"   model_load_latency={rerank.model_load_latency_ms:.2f}ms inference_latency={rerank.inference_latency_ms:.2f}ms"
        )
    elif rerank.scoring_method == "metadata_boost":
        header += f" metadata_candidates_processed={rerank.reranker_processed_candidates}"
    else:
        header += f" candidates_passed_through={rerank.reranker_processed_candidates}"
    candidates = list(rerank.candidates)
    changed = [row for row in candidates if row["rank_change"] != 0]
    final = [row for row in candidates if row["final_rank"] is not None]
    shown = candidates if verbose else _unique_rows(final + sorted(changed, key=lambda row: abs(row["rank_improvement"]), reverse=True)[:5])
    rows = [
        f"{row['expert_id']} {row['pre_rerank_rank']} -> {row['reranker_rank']} "
        f"improvement={row['rank_improvement']:+d} score={row['reranker_raw_score']:.4f} "
        f"final_rank={row['final_rank'] if row['final_rank'] is not None else 'out'}"
        for row in shown
    ]
    entered = [row["expert_id"] for row in candidates if row["entered_final_top_k"]]
    exited = [row["expert_id"] for row in candidates if row["exited_final_top_k"]]
    details = "\n   Rank changes:\n   " + "\n   ".join(rows) if rows else "\n   Rank changes: none"
    return header + details + f"\n   Entered final Top-K: {', '.join(entered) or 'none'}\n   Exited final Top-K: {', '.join(exited) or 'none'}"


def _unique_rows(rows):
    seen = set()
    return [row for row in rows if not (row["expert_id"] in seen or seen.add(row["expert_id"]))]


def _retriever_section(number: int, label: str, retriever, verbose: bool) -> str:
    if retriever is None:
        return f"{number}. {label} Retrieval\n   not selected by the retrieval plan"
    header = f"{number}. {label} Retrieval\n   candidates={retriever.candidate_count_before_truncation}/{retriever.candidate_limit} latency={retriever.latency_ms:.2f}ms"
    rows = [_candidate_row(candidate, verbose) for candidate in retriever.candidates]
    if label == "Graph" and rows:
        rows.append("semantics=relevance-scored matching (not strict logical AND)")
    return header + ("\n   " + "\n   ".join(rows) if rows else "\n   no candidates")


def _fusion_section(number: int, trace: RetrievalTrace, verbose: bool) -> str:
    assert trace.fusion is not None
    details = f"{number}. Fusion\n   method={trace.fusion.method} rrf_k={trace.fusion.rrf_k} deduplicated={', '.join(trace.fusion.deduplicated_ids) or 'none'}"
    rows = []
    for candidate in trace.fusion.candidates:
        contributors = ", ".join(
            f"{name}:rank={int(values['rank'])},contribution={values['fusion_contribution']:.4f}"
            for name, values in candidate.contributions.items()
        )
        rows.append(f"#{candidate.rank} {candidate.expert_id} fused={candidate.raw_score:.4f} [{contributors}]")
    return details + ("\n   " + "\n   ".join(rows) if rows else "")


def _ranking_section(number: int, trace: RetrievalTrace, verbose: bool) -> str:
    header = f"{number}. Final Ranking\n   processors={', '.join(trace.ranking.processors) or 'none'}"
    return header + "\n   " + "\n   ".join(_candidate_row(candidate, verbose) for candidate in trace.ranking.candidates)


def _ground_truth_section(number: int, trace: RetrievalTrace) -> str:
    truth = trace.ground_truth
    assert truth is not None
    return (
        f"{number}. Ground Truth\n   relevant={list(truth.relevant_ids)}\n"
        f"   hits={list(truth.relevant_retrieved_ids)} missed={list(truth.missed_relevant_ids)} "
        f"false_positives={list(truth.non_relevant_ids)} first_relevant_rank={truth.first_relevant_rank}"
    )


def _evaluation_section(number: int, trace: RetrievalTrace) -> str:
    evaluation = trace.evaluation
    assert evaluation is not None
    calculation = evaluation.calculation
    precision = calculation["precision"]
    recall = calculation["recall"]
    mrr = calculation["mrr"]
    ndcg = calculation["ndcg"]
    return (
        f"{number}. Evaluation\n"
        f"   Precision@K={precision['numerator']}/{precision['denominator']}={precision['value']:.4f}\n"
        f"   Recall@K={recall['numerator']}/{recall['denominator']}={recall['value']:.4f}\n"
        f"   MRR=1/{mrr['first_relevant_rank']}={mrr['value']:.4f}" if mrr["first_relevant_rank"] else
        f"{number}. Evaluation\n   Precision@K={precision['numerator']}/{precision['denominator']}={precision['value']:.4f}\n"
        f"   Recall@K={recall['numerator']}/{recall['denominator']}={recall['value']:.4f}\n   MRR=no relevant result (0.0000)"
    ) + f"\n   NDCG@K=DCG {ndcg['dcg']:.4f} / IDCG {ndcg['idcg']:.4f} = {ndcg['value']:.4f}\n   latency={calculation['latency_ms']:.2f}ms"


def _candidate_row(candidate, verbose: bool) -> str:
    base = f"#{candidate.rank} {candidate.expert_id} score={candidate.raw_score:.4f} normalized={candidate.normalized_score:.4f}"
    if candidate.relevant is not None:
        base += f" relevant={candidate.relevant}"
    if verbose:
        base += f" fields={list(candidate.matched_fields)} terms={list(candidate.matched_terms)} evidence={list(candidate.evidence)}"
    return base
