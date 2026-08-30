"""Lightweight pre-review Company OS consistency check.

This is a documentation/governance check, not a runtime or state-management
service. It intentionally fails closed on duplicate active work, missing
contracts, obvious stale current-state claims, or release-label ambiguity.
"""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
COMPANY = ROOT / "company-os"


def main() -> int:
    errors: list[str] = []
    state = (COMPANY / "PROJECT_STATE.md").read_text()
    current = (COMPANY / "CURRENT_WORK.md").read_text()
    readme = (COMPANY / "README.md").read_text()
    evaluations = (COMPANY / "EVALUATIONS.md").read_text()
    decisions = (COMPANY / "DECISIONS.md").read_text()
    post_release = (COMPANY / "POST_RELEASE_REVIEW.md").read_text()

    active_headings = re.findall(r"^# Current Work Object", current, re.MULTILINE)
    closed_headings = re.findall(r"^# Latest Closed Work Object", current, re.MULTILINE)
    match = re.search(r"\*\*Active Work Object:\*\* `([^`]+)`", state)
    no_active = "**Active Work Object:** none." in state
    if no_active:
        if active_headings or len(closed_headings) != 1:
            errors.append("closed project state must have one Latest Closed Work Object and no active heading")
    elif len(active_headings) != 1:
        errors.append(f"expected exactly one active Work Object heading, found {len(active_headings)}")
    if not no_active and not match:
        errors.append("PROJECT_STATE.md has no active Work Object")
    elif match and f"**Work Object:** `{match.group(1)}`" not in current:
        errors.append("active Work Object ID does not match CURRENT_WORK.md")

    active_id = match.group(1) if match else ""
    current_work = current.split("## Historical Work Object Archive", 1)[0]
    if not no_active:
        contract_match = re.search(
            r"\*\*Task Contract / Start Gate:\*\*\s*\n?\[.*?\]\(([^)]+)\)",
            current_work,
        )
        if not contract_match:
            errors.append("active Work Object has no linked Task Contract/Start Gate")
        else:
            contract = COMPANY / contract_match.group(1)
            if not contract.exists():
                errors.append("active Task Contract/Start Gate is missing")
            else:
                contract_text = contract.read_text()
                for token in ("Objective", "Scope", "Exclusions", "Evidence", "Stop"):
                    if token not in contract_text:
                        errors.append(f"Task Contract missing required section: {token}")
        result_match = re.search(
            r"\*\*Result Package:\*\*\s*\n?\[.*?\]\(([^)]+)\)",
            current_work,
        )
        if not result_match:
            errors.append("active Work Object has no linked Result Package")
        elif not (COMPANY / result_match.group(1)).exists():
            errors.append("active Result Package is missing")

    if "Gate 0 is active" in readme:
        errors.append("current v0.5.1 README still claims Gate 0 is active")
    current_state = state.split("## Gate map", 1)[0]
    if "Gate 4 remains inactive" in current_state or "Founder decision pending" in current_state:
        errors.append("PROJECT_STATE.md contains stale current Gate 3J/Gate 4 status")
    if "Gate 4 remains inactive" in current_work:
        errors.append("active CURRENT_WORK section contains stale Gate 4 status")
    if "No v0.6 work is authorized." not in current_state:
        errors.append("PROJECT_STATE.md does not explicitly keep v0.6 inactive")
    if "Current-state precedence" not in evaluations:
        errors.append("EVALUATIONS.md has no current-state precedence marker")
    if "historical shell" not in post_release:
        errors.append("post-release shell is not explicitly archived/superseded")
    if "GitHub Release object" not in state or "Git tag" not in readme:
        errors.append("release tag and GitHub Release-object distinction is not documented")
    surface_path = COMPANY / "GOVERNANCE_SURFACE.md"
    if not surface_path.exists():
        errors.append("Governance Surface is missing")
    else:
        surface = surface_path.read_text()
        for token in (
            "schema_version: governance-surface/v0.1",
            "agent_entrypoint:",
            "adapter:",
            "truth_sources:",
            "latest_material_milestone:",
            "execution_readiness:",
            "alignment_state:",
        ):
            if token not in surface:
                errors.append(f"Governance Surface missing required field: {token}")
        if active_id and f"id: {active_id}" not in surface:
            errors.append("Governance Surface active Work Object does not match PROJECT_STATE.md")
        if "applicable: true" in surface and (
            "traceability_matrix: pending" in surface
            or "no_model_smoke: pending" in surface
        ):
            errors.append("executable Governance Surface has pending readiness control")
    if active_id == "armie-retrieval-v051-release-stabilization-closeout" or no_active:
        if "D-034 — Gate 5 closure and v0.5.1 release authorization" not in decisions:
            errors.append("DECISIONS.md does not record Gate 5 closure/release authorization")
        if "No v0.6 work is authorized." not in current_state:
            errors.append("PROJECT_STATE.md does not explicitly keep v0.6 inactive")
    if no_active:
        if "D-035 — v0.5.1 release closeout" not in decisions:
            errors.append("DECISIONS.md does not record v0.5.1 release closeout")
        if "released / closed" not in current:
            errors.append("latest closed Work Object does not record released/closed state")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Company OS consistency checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
