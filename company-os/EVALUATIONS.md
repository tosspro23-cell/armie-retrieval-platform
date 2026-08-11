# ARMIE Company OS Evidence Index

## Gate 5

- `docs/v0.4.0/gate5-results.md` — relevance metrics, failure analysis and
  benchmark scope.
- `docs/v0.4.0/dataset-card.md` — v1 dataset limitations and provenance.
- `docs/v0.4.0/validation-report.md` — Gate 5 validation narrative and limits.

Gate 5 is a controlled synthetic relevance benchmark. Its metrics do not prove
validated real-world expert-network search quality.

## Gate 5.5A

- `docs/v0.4.0/dataset-v2-design.md` — versioned v2 design and pipeline
  separation.
- `docs/v0.4.0/dataset-v2-pilot-audit.md` — pilot audit summary.
- `docs/v0.4.0/dataset-v2-pilot-audit.json` — tracked machine-readable summary.
- `/tmp/armie-v040-dataset-v2-pilot/audit.json` — full generated audit,
  including manual inspection samples.
- `docs/v0.4.0/dataset-card-v2.md` — v2 provenance and limitations.
- `tests/test_v040_dataset_v2.py` — deterministic, separation, integrity and
  quality-gate tests.

Gate 5.5A evidence supports a pilot result only. Gold is an independent
structured audit, not external human ground truth; Silver remains explicitly
rule-assisted. The benchmark must not be generalized to natural expert-network
data.

## Gate 5.5B

- `docs/v0.4.0/gate55b-results.md` — completed v1/v2 benchmark results,
  boundaries, timing and limitations.
- `docs/v0.4.0/benchmark-stability-report.md` — stability comparison and
  interpretation limits.
- `docs/v0.4.0/dataset-v2-full-audit.md` — full Dataset v2 integrity audit.
- `58baad4` — dense-index resumability checkpoint.
- `9973367` — committed benchmark stability checkpoint.

Gate 5.5B is completed evidence, not external validation. The corpus remains a
controlled synthetic relevance benchmark with templated language and leakage
risk.

## Gate 6 — candidate Result Package

- `docs/v0.4.0/validation-report.md` — Gate 6 scope and verification summary.
- `README.md` — Workbench usage and artifact boundary.
- `apps/workbench/tests/gate6.acceptance.spec.ts` — ten browser acceptance
  checks.
- `tests/test_workbench_api.py` — backend benchmark-library and execution
  regression coverage.
- `CURRENT_WORK.md` — candidate-complete Result Package and write-back
  checklist.

Gate 6 evidence is verified but uncommitted and awaiting founder acceptance.
It validates the Workbench mechanics and preserves existing runtime semantics;
it does not authorize Gate 7 or release work.
