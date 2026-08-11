# Architecture Decisions

## Dataset v2 pilot boundary

Dataset v2 is a separate, versioned controlled-synthetic relevance benchmark
pilot. It cannot modify or replace the immutable v1 corpus. Profile, query and
judgement generation are separate pipelines; only canonical ontology IDs and
structured truth may be shared. Gold judgements are an independent structured
audit, while Silver remains explicitly rule-assisted. This pilot does not claim
validated real-world expert-search quality.

1. **Runtime remains shared:** benchmark profiles bind providers through existing registry/runtime contracts.
2. **Control/data planes stay separate:** ARMIE plans, evaluates, explains, and governs; Elasticsearch/FAISS retrieve.
3. **Judgements are independent:** generated drafts are explicitly reviewable and never treated as truth without review.
4. **Optional dependencies fail clearly:** Docker, Elasticsearch, and model weights are prerequisites, not automatic downloads.
5. **Score semantics remain stage-specific:** BM25, dense, RRF, metadata, and Cross-Encoder scores retain their own labels.

## Gate 5 measured decisions

6. **Use BM25 for exact lexical constraints.** Gold results show H1 is strong
   on exact skill, delivery and semantic-paraphrase queries, but fails
   organization and negative/temporal constraints when those facts are not
   represented as strict structured filters.
7. **Use Dense for paraphrase and metadata-supported discovery.** H2 improved
   Gold NDCG over H1 (0.754 vs 0.686) and covered organization queries, at a
   measured 163.8 ms p50 versus 91.6 ms for H1.
8. **Use Hybrid RRF when lexical and semantic evidence should be combined.**
   H3 delivered the highest Gold MRR (0.914) and slightly higher NDCG than H2
   (0.762 vs 0.754), but added latency (242.5 ms p50) and did not solve
   negative/temporal constraint failures.
9. **Use BGE Cross-Encoder selectively.** H4 raised Gold NDCG to 0.818 and
   required-constraint satisfaction to 0.811, but Gold warm inference was
   851.4 ms p50 and end-to-end p50 was 1,976.7 ms; hard-negative intrusion rose
   to 0.200. It is worth the latency for
   high-value, small candidate pools, not as an unconditional default.
10. **Keep Elasticsearch Dense as the measured online dense backend for Gate
    5.** FAISS remains a validated persistent offline/low-latency alternative
    from Gate 3; backend choice should be workload-specific rather than hidden
    behind a relevance claim.
11. **Prioritize Knowledge Graph work for relationship, employer/client and
    delivery provenance failures.** Gate 5 exposed organization, temporal,
    negative and delivery/mention ambiguity that cannot be reliably resolved
    from flat lexical or embedding scores alone. This is a remediation finding,
    not a Gate 5 implementation.
