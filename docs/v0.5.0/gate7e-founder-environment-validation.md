# Gate 7E — Founder Environment Reproduction and Acceptance Verification

**Status:** automated founder-environment verification complete; founder visual
acceptance remains a consequential decision. Gate 8 is not started.

## Scope and environment

This was a bounded live-integration check. It did not change retrieval
architecture, benchmark semantics, Dataset v2, or Gate 8 scope. The browser
used the founder's existing Workbench at `http://127.0.0.1:5173/` and the API
used `http://127.0.0.1:8000/api/v1`. Elasticsearch was the existing local
8.15.3 service on port 9200; no Elasticsearch process was stopped.

| Service | Verified identity |
|---|---|
| Backend | `python -m uvicorn services.api.app:app --host 127.0.0.1 --port 8000`, PID 91131, cwd is the repository checkout, listening on 127.0.0.1:8000 |
| Frontend | Vite on `localhost:5173`, PID 24222, cwd is `apps/workbench`, serving the repository source tree |
| API metadata | `/health` and `/capabilities` returned service `armie-retrieval-workbench`, Dataset v2 availability, and C1 native-prefilter capability |
| Elasticsearch | Existing compatible Gate 6B projection/index used by the backend; the live C1 response returned structured facts from the projection |

The health `git_commit` field is the committed repository HEAD
(`266bf5b8c4a81aee30231d486312b03c4eca96db`). Gate 7D/Gate 7E edits are
uncommitted, so this field is not a complete identity for the live source
overlay. Process cwd and browser-visible current behavior were recorded as the
source identity evidence.

## Reproduction and bounded fixes

The original founder backend process (PID 24165, started 2026-08-13) was
running the same checkout but an older process image. A structured request
returned 100 cards instead of final Top-K 5 and had no structured facts in the
response. The browser showed the same 100-card state. This reproduced the
reported issue as a stale backend process, not an Elasticsearch ranking defect.

After stopping only that identified ARMIE backend and restarting the repository
command, the live API returned final Top-K 5 and structured evidence. A second
integration defect was then reproducible when switching C1 back to free C0:
the frontend reused the structured request's session ID, received “Session was
not found”, and retained the previous C1 result list. The bounded fix clears
the prior response before execution and does not carry a structured session
into C1; it does not alter runtime retrieval semantics.

## API and DOM evidence

Direct live API C1 checks (`requested_k=5`, candidate pool 100):

| Constraint | Eligible | Returned | API result length | Observed years in returned results |
|---|---:|---:|---:|---|
| years >= 10 | 100 | 5 | 5 | 24, 24, 24, 23, 19 |
| years >= 20 | 100 | 5 | 5 | 24, 24, 24, 23, 24 |
| years >= 25 | 100 | 5 | 5 | 25, 25, 25, 25, 25 |

The browser DOM matched the API contract after each run: 5 `article.result`
nodes and 5 `.constraint-evidence` sections for supported C1 runs. The
repeated threshold sequence 10 → 20 → 25 produced DOM counts 5, 5, 5 with no
append or stale-result leak.

## Live scenarios

| Scenario | Live result |
|---|---|
| A. No contract | C0/H2 Dense; 5 result cards; 0 constraint-evidence blocks; no filter applied |
| B. years_experience | C1; 5 cards; all visible facts satisfy the selected threshold; evidence rendered per card |
| C. seniority | C1; seniority evidence is rendered and eligible results are returned |
| D. multi-constraint | C1; manufacturing + years >= 10 + seniority >= senior; 5 cards and all three required evidence rows visible |
| E. exclusion | C1; exclusion is rendered as “must not match”; returned industries are not manufacturing |
| F. unsupported/deferred | `UNSUPPORTED_CONSTRAINT`; 0 cards, `not_executed` trace, explicit “retrieval was not executed”; no C0 fallback |
| G. strict shortfall | years >= 1000; 0 cards; “returned 0 of 5” and strict-shortfall copy; no ineligible backfill |
| H. provenance | C1 trace identifies `constraint_prefilter` and `elasticsearch_dense`; evidence, candidate/eligible/returned semantics are exposed by the response and UI |

For the multi-constraint run, the first five cards all showed required years,
seniority, and Manufacturing facts. For the strict exclusion run, the API/UI
showed `Required: none`, `Exclusions: industry = manufacturing`, and five
eligible cards. For unsupported input, execution latency was 0 ms and the
trace state was `not_executed`.

## Playwright and regression validation

The existing Gate 7C live integration suite was run directly against the
founder services (`PLAYWRIGHT_FRONTEND=http://127.0.0.1:5173`,
`PLAYWRIGHT_BACKEND=http://127.0.0.1:8000`) rather than the isolated test
servers. **8/8 tests passed**, covering C0, years thresholds, seniority and
multi-constraint, exclusion, unsupported constraints, strict shortfall, and
provenance.

Additional browser checks above verified repeated threshold state and the
post-fix C1→C0 transition. The Playwright configuration now accepts explicit
founder URLs and skips its isolated web servers only when
`PLAYWRIGHT_FOUNDER_ENV=1`; the default isolated behavior is unchanged.

Previously verified regressions remain green: Python 131 passed/3 skipped,
Elasticsearch integration 2 passed, frontend unit tests 4 passed, frontend
build passed, isolated Playwright 29 passed, package build passed, import
smoke passed, Markdown links resolved, and `git diff --check` passed. The
frontend session-state fix was revalidated by the 8 live Playwright tests.

## Gate 7E conclusion

The founder environment reproduced two integration defects, both bounded and
resolved: a stale backend process and a frontend structured-session/stale
result transition. Current live C0/C1 behavior, unsupported handling, strict
shortfall, provenance, and DOM/API result counts are consistent. Automated
Gate 7E evidence is ready for founder/manual acceptance. Gate 8, release,
commit, tag, and push remain out of scope.
