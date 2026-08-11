# Benchmark Stability Plan

This plan keeps Dataset v1 immutable while Dataset v2 evolves through measured
pilot gates.

1. Pin every dataset identity and generator seed in a manifest.
2. Keep document, query and judgement generation as separate pipelines.
3. Compare duplicate, near-duplicate, lexical-diversity and shared-phrase
   diagnostics at every pilot revision.
4. Keep Gold (independent structured audit) and Silver (rule-assisted) contracts
   and denominators separate.
5. Require deterministic checksums, temporal validation and evidence references.
6. Inspect at least 20 profiles and 20 queries, including positive, partial,
   negative, ambiguous and hard-negative examples.
7. Do not run or publish full H1–H4 metrics until the v2 pilot passes this gate.

The benchmark remains a **controlled synthetic relevance benchmark**. It is not
validated real-world expert-search quality and must not be generalized to
natural expert-network data.
