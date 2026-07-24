# Release Notes — v0.2.0

## First public release

ARMIE Retrieval Platform v0.2.0 is the first public reference implementation of the frozen Architecture Freeze v1.0. It demonstrates a modular path from declarative planning to retrieval, result processing, evaluation, capability discovery, and offline adaptive policy publishing.

## Included

- Rule and LLM-compatible planning against one immutable `RetrievalPlan` contract.
- Sparse, dense-style, Hybrid/RRF, and NetworkX graph retrieval.
- Ordered result-processing plugins.
- Independent capability registries for retrievers, processors, and providers.
- Offline observation-to-policy learning MVP.
- Expert Discovery demo and automated tests.

## Installation

```bash
python3 -m pip install .
python3 examples/expert_discovery_demo.py
python3 -m unittest discover -s tests -v
```

## Known limitations

- The reference LLM planner client is intentionally injected rather than tied to a vendor. The example uses a deterministic fixture so public users can run it without credentials.
- NetworkX is required to execute the graph demonstration. The dependency is declared in `pyproject.toml`.
- The learning engine is deliberately offline and rule-based; it publishes policies but does not train a model or perform runtime historical lookup.
