# v0.5.1 Gate 3B — Model Coverage Closure

**Status:** `ACTIVE / BLOCKED`; Gate 4 remains inactive.

Gate 3B preserved the frozen 120-item benchmark and all Gate 3 promotion
thresholds. It did not modify the benchmark, prompt semantics, gold labels, or
architecture.

## Root-cause diagnosis

A minimal structured request against local Ollama `qwen3:4b` produced valid JSON:

- cold request: **6069.6 ms**;
- observed model load: **4756.5 ms**;
- warm request: **1387.4 ms**;
- response: 407 characters, valid JSON;
- environment: macOS 26.5.2 arm64, local Ollama daemon;
- device/Metal detail: not exposed by the Ollama API.

This rules out schema incompatibility and malformed JSON as the primary cause.
The blocker is operational: per-request generation throughput remains too slow
or variable for a bounded 120-item serial run. The existing client now exposes
timeouts distinctly; Gate 3B freezes a 15-second timeout and one retry for
timeout/model-call failures only.

## Coverage closure attempt

The model and hybrid identities were frozen as:

- `ollama-structured-qwen3-4b-v1-gate3b-warm-persistent-v1`;
- `hybrid-rule-plus-structured-qwen3-4b-v1-gate3b-warm-persistent-v1`.

The model full-set attempt was started with one warm-up, 15s timeout, and one
retry. It exceeded the bounded execution window before a complete result file
could be emitted; no semantic metrics are reported. Hybrid was not started
after this upstream blocker. The machine-readable record therefore reports
coverage and failure state explicitly rather than treating missing outputs as
semantic errors.

## Decision

Gate 3B does **not** close Gate 3. qwen3:4b is operationally unsuitable for
this Gate under the available local execution boundary. Gate 3 remains
`ACTIVE / BLOCKED`, no architecture is promoted, and Gate 4 is not
recommended.

The frozen Gate 3 rule result remains unchanged: complete coverage but False
HARD 9.17%, below the 0% threshold. The Gate 3B diagnostic does not overwrite
that historical result.

Evidence: [Gate 3 frozen evaluation](gate3-frozen-extraction-evaluation.md),
[Gate 3B machine results](gate3b-coverage-results.json), and the existing
[Gate 3 manifest](gate3-evaluation-manifest.json).
