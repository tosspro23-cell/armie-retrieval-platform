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
