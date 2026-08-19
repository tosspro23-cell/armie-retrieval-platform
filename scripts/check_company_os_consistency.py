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
    if len(active_headings) != 1:
        errors.append(f"expected exactly one active Work Object heading, found {len(active_headings)}")
    match = re.search(r"\*\*Active Work Object:\*\* `([^`]+)`", state)
    if not match:
        errors.append("PROJECT_STATE.md has no active Work Object")
    elif f"**Work Object:** `{match.group(1)}`" not in current:
        errors.append("active Work Object ID does not match CURRENT_WORK.md")

    active_id = match.group(1) if match else ""
    contract = COMPANY / (
        "V051_RELEASE_START_GATE.md"
        if active_id == "armie-retrieval-v051-release-stabilization-closeout"
        else "GATE5_F3_START_GATE.md"
    )
    required = ("Work Object ID", "Objective", "scope", "Stop")
    if not contract.exists():
        errors.append("active Task Contract/Start Gate is missing")
    else:
        contract_text = contract.read_text()
        for token in required:
            if token not in contract_text:
                errors.append(f"Task Contract missing required section: {token}")

    current_work = current.split("## Historical Work Object Archive", 1)[0]
    if "Gate 0 is active" in readme:
        errors.append("current v0.5.1 README still claims Gate 0 is active")
    current_state = state.split("## Gate map", 1)[0]
    if "Gate 4 remains inactive" in current_state or "Founder decision pending" in current_state:
        errors.append("PROJECT_STATE.md contains stale current Gate 3J/Gate 4 status")
    if "Gate 4 remains inactive" in current_work:
        errors.append("active CURRENT_WORK section contains stale Gate 4 status")
    if "Current-state precedence" not in evaluations:
        errors.append("EVALUATIONS.md has no current-state precedence marker")
    if "historical shell" not in post_release:
        errors.append("post-release shell is not explicitly archived/superseded")
    if "GitHub Release object" not in state or "Git tag" not in readme:
        errors.append("release tag and GitHub Release-object distinction is not documented")
    if active_id == "armie-retrieval-v051-release-stabilization-closeout":
        if "D-034 — Gate 5 closure and v0.5.1 release authorization" not in decisions:
            errors.append("DECISIONS.md does not record Gate 5 closure/release authorization")
        if "No v0.6 work is authorized." not in current_state:
            errors.append("PROJECT_STATE.md does not explicitly keep v0.6 inactive")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Company OS consistency checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
