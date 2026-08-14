"""Execute the locked v0.5 C0/C1/C2 benchmark and write Gate 6 artifacts."""
from __future__ import annotations

import gzip
import json
import platform
import statistics
import time
from collections import Counter
from pathlib import Path

from armie_retrieval.contracts import Constraint, ConstraintCategory, ConstraintOperator, RetrievalContract
from armie_retrieval.embeddings import BGEEmbeddingProvider
from armie_retrieval.indexing.elasticsearch import ElasticsearchClient
from armie_retrieval.models import Query, RetrievalPlan
from armie_retrieval.providers.elasticsearch import ElasticsearchDenseRetriever
from armie_retrieval.retrievers.c2_postfilter import C2PostFilterRetriever

ROOT = Path(__import__("os").environ.get("ARMIE_GATE6_ROOT", "docs/v0.5.0/benchmark-extension-v1"))
OUT = Path(__import__("os").environ.get("ARMIE_GATE6_OUT", "/tmp/armie-v050-gate6"))
INDEX = __import__("os").environ.get("ARMIE_GATE6_INDEX", "armie-experts-v1-v2-gate55b-dense-10000")


def contract(query: dict) -> RetrievalContract:
    constraints = []
    category = {"years_experience": ConstraintCategory.NUMERIC, "industry": ConstraintCategory.CATEGORICAL, "role": ConstraintCategory.ROLE, "location": ConstraintCategory.CATEGORICAL, "seniority": ConstraintCategory.SENIORITY}
    for field, rule in query["expected_contract"]["hard_constraints"].items():
        op = ConstraintOperator(rule["operator"])
        constraints.append(Constraint(canonical_field=field, operator=op, expected_value=rule["value"], category=category[field], provenance="gate5b-manual-contract"))
    exclusions = []
    for field, rule in query.get("expected_contract", {}).get("exclusions", {}).items():
        exclusions.append(Constraint(canonical_field=field, operator=ConstraintOperator(rule["operator"]), expected_value=rule["value"], category=category[field], provenance="gate5c-manual-contract"))
    return RetrievalContract(semantic_query=query.get("execution_query_text", query["query_text"]), hard_constraints=tuple(constraints), exclusions=tuple(exclusions))


def metrics(ids: list[str], grades: dict[str, int], *, top5_ids: list[str], eligible: set[str], hard: set[str], supply: int, prohibited: set[str] | None = None, has_exclusions: bool = False) -> dict:
    top5 = top5_ids[:5]
    top10 = ids[:10]
    rel5 = [grades.get(x, 0) for x in top5]
    relevant = {x for x, g in grades.items() if g > 0}
    relevant_eligible = {x for x in grades if x in eligible and grades[x] > 0}
    import math
    dcg = sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(rel5))
    ideal = sorted(grades.values(), reverse=True)[:5]
    idcg = sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(ideal))
    returned_eligible = [x for x in top5 if x in eligible]
    hard_intrusions = [x for x in top5 if x in hard]
    prohibited_rate = (sum(x in (prohibited or set()) for x in top5) / len(top5)) if has_exclusions and top5 else None
    return {"ndcg_at_5": dcg / idcg if idcg else 0.0, "precision_at_5": sum(g > 0 for g in rel5) / 5, "recall_at_10": sum(grades.get(x, 0) > 0 for x in top10) / len(relevant) if relevant else 0.0, "mrr": next((1 / (i + 1) for i, x in enumerate(top10) if grades.get(x, 0) > 0), 0.0), "grade_3_hit_at_5": int(any(g == 3 for g in rel5)), "required_constraint_satisfaction_at_5": sum(x in eligible for x in top5) / len(top5) if top5 else 0.0, "constraint_violation_at_5": sum(x not in eligible for x in top5) / len(top5) if top5 else 0.0, "prohibited_constraint_violation_at_5": prohibited_rate, "true_hard_negative_intrusion_at_5": len(hard_intrusions) / len(top5) if top5 else 0.0, "unknown_constraint_rate_at_5": 0.0, "eligible_recall_at_10": sum(x in relevant_eligible for x in top10) / len(relevant_eligible) if relevant_eligible else None, "eligible_fill_at_5": sum(x in relevant_eligible for x in top5) / min(5, supply) if supply else None, "returned_count": len(top5), "returned_eligible_count": len(returned_eligible), "shortfall_magnitude": max(0, 5 - len(returned_eligible)), "eligible_supply": supply}


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    queries = json.loads((ROOT / "queries.json").read_text())
    audit = json.loads((ROOT / "audit.json").read_text())
    grades_by_query: dict[str, dict[str, int]] = {q["query_id"]: {} for q in queries}
    eligible_by_query: dict[str, set[str]] = {q["query_id"]: set() for q in queries}
    hard_by_query: dict[str, set[str]] = {q["query_id"]: set() for q in queries}
    statuses_by_query: dict[str, dict[str, dict]] = {q["query_id"]: {} for q in queries}
    with gzip.open(ROOT / "judgements.jsonl.gz", "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line); qid = row["query_id"]; eid = row["expert_id"]
            grades_by_query[qid][eid] = row["relevance_grade"]
            statuses_by_query[qid][eid] = row["constraint_status"]
            if row["eligible"]: eligible_by_query[qid].add(eid)
            if row["hard_negative_class"]: hard_by_query[qid].add(eid)
    client = ElasticsearchClient(timeout=120)
    health = client.health()
    if health.get("version") != "8.15.3" or health.get("cluster", {}).get("status") != "green": raise RuntimeError(f"identity mismatch: {health}")
    embedding = BGEEmbeddingProvider(model_name="BAAI/bge-m3")
    embedding.validate_model_available()
    dense = ElasticsearchDenseRetriever(client, index=INDEX, embedding_provider=embedding)
    cache: dict[str, list[float]] = {}
    original = embedding.embed
    def cached(texts):
        out=[]
        for text in texts:
            if text not in cache: cache[text] = original([text])[0]
            out.append(cache[text])
        return out
    embedding.embed = cached
    arms = [("C0", None), ("C1", None), ("C2-20", 20), ("C2-50", 50), ("C2-100", 100)]
    raw=[]
    for query_row in queries:
        qid = query_row["query_id"]; contract_obj = contract(query_row); supply = audit["eligible_supply"]["per_query"][qid]
        for arm, n in arms:
            query = Query(text=query_row.get("execution_query_text", query_row["query_text"]), top_k=5, request_id=f"gate6r-{arm}-{qid}", retrieval_contract=contract_obj if arm != "C0" else None)
            plan = RetrievalPlan(strategy="dense", top_k=5, parameters={"retrieval_candidate_k": n or 10, "retrieval_contract": contract_obj if arm != "C0" else None})
            started=time.perf_counter()
            retriever = dense if arm != "C2-20" and arm != "C2-50" and arm != "C2-100" else C2PostFilterRetriever(dense, candidate_pool_size=n)
            result = retriever.retrieve(query, plan)
            elapsed=(time.perf_counter()-started)*1000
            prov=dict(result.provenance); audit_rows=prov.get("verification_audit", [])
            if arm.startswith("C2"):
                raw_ids=[x["candidate_id"] for x in audit_rows]
                eligible_ids=[x["candidate_id"] for x in audit_rows if x.get("eligible")]
                decisions={x["candidate_id"]: x.get("constraints", []) for x in audit_rows}
                stage={"contract_validation_ms": None,"filter_compile_ms": None,"dense_retrieval_ms": None,"c2_verification_ms": prov.get("verification_latency_ms"),"eligible_top_k_assembly_ms": None,"e2e_ms": elapsed}
                original_ranks={eid:i+1 for i,eid in enumerate(raw_ids) if eid in eligible_by_query[qid]}
                exclusion_ids={c.constraint_id for c in contract_obj.exclusions}
                prohibited_ids={x["candidate_id"] for x in audit_rows if any(d.get("constraint_id") in exclusion_ids and d.get("status") == "VIOLATED" for d in x.get("constraints", []))}
            else:
                raw_ids=[x.id for x in result.items]
                eligible_ids=[x for x in raw_ids if x in eligible_by_query[qid]]
                decisions={}
                ls=prov.get("latency_stages", {})
                stage={"contract_validation_ms":ls.get("contract_validation_ms"),"filter_compile_ms":ls.get("filter_compile_ms"),"dense_retrieval_ms":ls.get("dense_filter_execution_ms", result.latency_ms),"c2_verification_ms":None,"eligible_top_k_assembly_ms":None,"e2e_ms":elapsed}
                original_ranks={eid:i+1 for i,eid in enumerate(raw_ids) if eid in eligible_by_query[qid]}
                prohibited_ids={eid for eid in raw_ids if any(k.startswith("exclusion:") and v == "VIOLATED" for k,v in statuses_by_query[qid].get(eid, {}).items())}
            top5=[x.id for x in result.items[:5]]
            has_exclusions=any(k.startswith("exclusion:") for eid in raw_ids for k in statuses_by_query[qid].get(eid, {}))
            row={"query_id":qid,"stratum":query_row["category"],"strategy":arm,"candidate_pool_n":n,"contract_id":contract_obj.contract_id,"returned_ids":top5,"retrieved_ids":raw_ids,"scores":[x.score for x in result.items[:5]],"original_dense_ranks":original_ranks,"eligibility":{eid:eid in eligible_by_query[qid] for eid in raw_ids},"constraint_status":decisions or {eid:statuses_by_query[qid].get(eid,{}) for eid in raw_ids},"hard_negative_ids":[eid for eid in raw_ids if eid in hard_by_query[qid]],"eligible_supply":supply,"legitimate_scarcity":supply < 5,"returned_eligible_count":len(eligible_ids[:5]),"latency_stages":stage,"metrics":metrics(raw_ids, grades_by_query[qid], top5_ids=top5, eligible=eligible_by_query[qid], hard=hard_by_query[qid], supply=supply, prohibited=prohibited_ids, has_exclusions=has_exclusions),"prohibited_violation_ids":[eid for eid in top5 if eid in prohibited_ids],"has_exclusions":has_exclusions}
            raw.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"gate6-per-query.json").write_text(json.dumps(raw, indent=2, sort_keys=True), encoding="utf-8")
    aggregate={}
    for arm,_ in arms:
        rows=[r for r in raw if r["strategy"]==arm]
        aggregate[arm]={k: statistics.mean([r["metrics"][k] for r in rows if r["metrics"][k] is not None]) for k in rows[0]["metrics"] if k not in {"returned_count","returned_eligible_count","shortfall_magnitude","eligible_supply"}}
        aggregate[arm]["query_count"]=len(rows); aggregate[arm]["latency_mean_ms"]=statistics.mean(r["latency_stages"]["e2e_ms"] for r in rows); aggregate[arm]["latency_p50_ms"]=statistics.median(r["latency_stages"]["e2e_ms"] for r in rows); aggregate[arm]["latency_p95_ms"]=sorted(r["latency_stages"]["e2e_ms"] for r in rows)[int(len(rows)*.95)-1]
        sufficient=[r for r in rows if not r["legitimate_scarcity"]]; aggregate[arm]["supply_sufficient_query_count"]=len(sufficient); aggregate[arm]["retrieval_shortfall_rate"]=sum(r["metrics"]["shortfall_magnitude"]>0 for r in sufficient)/len(sufficient) if sufficient else None; aggregate[arm]["total_shortfall_magnitude"]=sum(r["metrics"]["shortfall_magnitude"] for r in sufficient)
    (OUT/"gate6-aggregate.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True), encoding="utf-8")
    (OUT/"environment.json").write_text(json.dumps({"elasticsearch":health,"index":INDEX,"embedding_model":"BAAI/bge-m3","python":platform.python_version(),"machine":platform.platform(),"warmup":"first query per arm included; no separate cold exclusion","sample_count":len(raw)}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"rows":len(raw),"aggregate":aggregate}, indent=2))


if __name__ == "__main__": main()
