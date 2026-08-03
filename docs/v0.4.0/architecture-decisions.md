# Architecture Decisions

1. **Runtime remains shared:** benchmark profiles bind providers through existing registry/runtime contracts.
2. **Control/data planes stay separate:** ARMIE plans, evaluates, explains, and governs; Elasticsearch/FAISS retrieve.
3. **Judgements are independent:** generated drafts are explicitly reviewable and never treated as truth without review.
4. **Optional dependencies fail clearly:** Docker, Elasticsearch, and model weights are prerequisites, not automatic downloads.
5. **Score semantics remain stage-specific:** BM25, dense, RRF, metadata, and Cross-Encoder scores retain their own labels.
