# v0.4.0 Gate 5.5B Architecture Decisions

Status: frozen release conclusions from Gate 5.5B; H1–H4 executed on Dataset
v2 Gold. These conclusions are distribution-specific and are not a
production-realism claim.

## Frozen release conclusions

- H1 BM25 is the lowest-cost lexical baseline.
- H2 Dense is the strongest practical default candidate on this controlled
  Dataset v2 distribution.
- H3 Hybrid RRF provides complementary lexical and semantic signals but only
  a small aggregate gain over H2.
- H4 Hybrid plus BGE reranking is a cost/benefit experiment, not an always-on
  default: warm local inference is approximately one second with negligible
  aggregate quality improvement over H3.
- Structured relationship, temporal, and prohibited constraints require
  deterministic handling; ranking alone is insufficient.
- Graph modelling remains targeted and evidence-driven for relationship
  failures, not a default expansion of every retrieval path.

## Evidence boundary

Dataset v2 is a controlled synthetic relevance benchmark. Gold is an
independent structured audit, not external human ground truth. The benchmark
uses 103 Gold queries and 17 Silver monitoring queries; the smaller categories
are directional only. No statistical significance test was run.

## Decisions from v2 evidence

- **BM25 remains a strong baseline.** H1 Gold NDCG@5 was 0.6054 and MRR
  0.6246, but H2/H3 were materially higher on this distribution.
- **Dense is materially useful for this corpus.** H2 NDCG@5 was 0.7569 and
  MRR 0.8252, outperforming H1 on paired mean NDCG delta (H1−H2 = −0.1515;
  16 wins, 57 ties, 30 losses).
- **Hybrid adds limited complementary value over dense.** H3 NDCG@5 was
  0.7594 versus H2 0.7569 (H2−H3 = −0.0025; 16/63/24).
- **BGE reranking does not yet justify its latency on this evidence.** H4
  NDCG@5 was 0.7596 versus H3 0.7594 (H3−H4 = −0.0002; 17/71/15), while
  warm inference was approximately 981 ms and total reranking approximately
  986 ms per query. This is a weak quality delta, not a production latency
  recommendation.
- **Deterministic constraints remain necessary.** Employer/client, delivery,
  temporal, role, and prohibited-condition semantics are structured in the
  judgement contract but are not fully enforced by lexical/dense retrieval.
- **Graph modelling is justified only for relationship-specific failures.**
  The benchmark supports investigating graph traversal for organization and
  relationship constraints; it does not justify adding graph complexity to
  ordinary skill retrieval.
- **ES dense vs FAISS is not resolved by this benchmark.** Both artifacts were
  built from the same BGE-M3 projection, but backend equivalence was not
  established by candidate or latency analysis.

## v1/v2 classification

The v1 Gate 5 ranking order must not be assumed stable: v2 strengthens the
case for dense retrieval, weakens any claim that reranking is automatically
worth its cost, and leaves graph/constraint architecture inconclusive pending
targeted evidence. These are distribution-specific observations, not general
expert-network claims.
