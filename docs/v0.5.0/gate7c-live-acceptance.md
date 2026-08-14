# Gate 7C — Live Acceptance Evidence

## Automated acceptance

The isolated live services used the compatible Gate 6B Elasticsearch
projection. The browser suite `tests/gate7c.integration.spec.ts` passed 8/8.
It exercised free-query C0, supported C1 constraints, explicit exclusion,
multi-constraint conjunction, unsupported deferred input, strict shortfall,
and C1 provenance. Gate 7D additionally asserts strict final Top-K and
human-readable per-result constraint evidence for years and seniority cases.

The focused existing Workbench regression suite plus Gate 7C passed 11/11.
Frontend unit tests, production build, Gate 7C backend tests, C1 productization
tests, Elasticsearch integration tests, import smoke, package build, Markdown
link checks, and `git diff --check` were also run during this task.

## Manual founder review remains required

Automated browser evidence does not mark visual acceptance. The founder should
inspect the checklist for:

- Dense versus Constraint-aware Dense distinction;
- contract and exclusion readability;
- unsupported and strict-shortfall messaging;
- provenance usefulness without overclaiming;
- local latency feel and visual regressions;
- capability wording and deferred-scope boundaries.

Gate 7C is ready for final manual acceptance review. Gate 8 and release work
remain out of scope.
