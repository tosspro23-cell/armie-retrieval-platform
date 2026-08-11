# ARMIE Company OS v0.1

ARMIE Company OS v0.1 is a manual, state-governed operating protocol. It is
not a Python runtime or UI. Versioned local project files are the authoritative
operational state; chats are for reasoning and Git remains the source of code
truth.

## Operating contract

1. Read the current state.
2. Create or activate a Work Object.
3. Define the task contract.
4. Execute within scope.
5. Produce a Result Package with evidence and scope limits.
6. Verify the result independently where practical.
7. Propose a candidate state transition.
8. The founder accepts or rejects it.
9. Complete the structured write-back checklist.

Agents may propose changes and produce evidence. Agents do not directly change
accepted authoritative state, mark work accepted, or treat a result as founder
authorization. Consequential decisions remain with the founder.

## Result Package and write-back contract

Every Work Object completion must record:

- objective, scope, constraints and exclusions;
- actual result, evidence references, validation status and known limitations;
- candidate state transition and the founder decision required;
- a write-back checklist: update `PROJECT_STATE.md`, the active Work Object,
  `DECISIONS.md` and `EVALUATIONS.md` only after the founder accepts the
  transition, then record the acceptance evidence and date.

Before acceptance, a work object is `candidate-complete` or `awaiting-founder`
and the project state remains unchanged. An agent may prepare proposed
write-back text, but only the founder's explicit acceptance authorizes changing
accepted project state.

The Retrieval Platform is the first validation project. This protocol records
verified history, candidate work, and founder decisions without inferring one
from another.

See [PROJECT_STATE.md](PROJECT_STATE.md), [CURRENT_WORK.md](CURRENT_WORK.md),
[DECISIONS.md](DECISIONS.md), and [EVALUATIONS.md](EVALUATIONS.md).
