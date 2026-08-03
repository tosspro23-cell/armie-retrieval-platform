# Benchmark Protocol

Required profiles are Elasticsearch BM25, FAISS Dense, Elasticsearch Dense, BM25+FAISS, BM25+Elasticsearch Dense, and Hybrid+BGE Cross-Encoder. Every run records dataset checksum, query/judgement versions, candidate boundaries, backend/model identity, code commit, and fingerprint.

Primary metrics are NDCG@5, Recall@10, Precision@5, and MRR. Latency is reported separately and provider-specific scores are never compared as if they shared a scale.
