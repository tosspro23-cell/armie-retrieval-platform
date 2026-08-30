# Retrieval Platform Governance Surface

```yaml
schema_version: governance-surface/v0.1
last_reviewed: 2026-08-30
review_basis: "GOV-CONV-001 accepted governance alignment on verified origin/main bebc34d; no product-code or release change."

project:
  id: armie-retrieval-platform
  name: ARMIE Retrieval Platform
  lifecycle: maintenance
  strategic_role: "Retrieval, evaluation, provenance, and governed natural-language-to-contract reference infrastructure."
  public_maturity_boundary: "v0.5.1 is a controlled synthetic retrieval reference release; no unrestricted natural-language, real-world quality, or new-version claim."

governance:
  core_version: "ARMIE Company OS Core v0.1 plus Governance Convergence Standard v0.1"
  adapter: company-os/PROJECT_ADAPTER.md
  agent_entrypoint: AGENTS.md
  acceptance_authority: Founder
  active_work:
    id: none
    state: none
    task_contract: not_applicable

truth_sources:
  engineering: "GitHub repository and verified origin/main; see PROJECT_STATE.md for release pointers."
  ci_evidence: ".github/workflows/ci.yml and project-local tests; exact runs remain in GitHub."
  project_state: company-os/PROJECT_STATE.md
  release_or_deployment: "company-os/PROJECT_STATE.md and GitHub Release v0.5.1; no deployment state implied."

latest_material_milestone:
  description: "GOV-CONV-001 is Founder-accepted as the common governance-interface sample; v0.5.1 remains the separately recorded released capability boundary."
  capability_readiness: not_applicable
  transition_state: accepted
  evidence_refs:
    - company-os/GOVERNANCE_CONVERGENCE_PHASE1_START_GATE.md
    - company-os/GOVERNANCE_CONVERGENCE_PHASE1_RESULT_PACKAGE.md
    - company-os/PROJECT_ADAPTER.md

execution_readiness:
  applicable: false
  traceability_matrix: not_applicable
  no_model_smoke: not_applicable
  unit_evidence: not_applicable
  integration_evidence: not_applicable
  live_evidence: not_applicable

portfolio:
  company_writeback: "Founder-accepted 2026-08-30; registry records accepted branch-level alignment pending canonical repository merge."
  dependencies: [ARMIE_COMPANY_OS_CORE]
  material_risks:
    - "Future executable tasks must map their own traceability matrix and no-model smoke; this governance task does not retroactively certify historical capabilities."
    - "The accepted governance files must be merged into the repository's canonical branch before ordinary main-branch dispatches can rely on them."
  alignment_state: pending_canonical_merge
```
