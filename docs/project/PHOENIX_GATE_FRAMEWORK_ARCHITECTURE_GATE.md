# Architecture Gate — Phoenix Gate Framework

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Approved Decision Summary:
  [PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md](PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md)
- Approval Record:
  [PHOENIX_GATE_FRAMEWORK_APPROVAL_RECORD.md](PHOENIX_GATE_FRAMEWORK_APPROVAL_RECORD.md)
- Gate Acceptance:
  [PHOENIX_GATE_FRAMEWORK_ACCEPTANCE.md](PHOENIX_GATE_FRAMEWORK_ACCEPTANCE.md)
- Evidence:
  [PHOENIX_GATE_FRAMEWORK.md](PHOENIX_GATE_FRAMEWORK.md) ·
  [PHOENIX_GATE_GENERATOR_RULES.md](PHOENIX_GATE_GENERATOR_RULES.md) ·
  [PHOENIX_GATE_LEGACY_MIGRATION.md](PHOENIX_GATE_LEGACY_MIGRATION.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design boundary only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Accepted architecture boundary

Phoenix Gate Framework is the sole Gate process. Every Package uses:

```text
Decision Summary
→ PO Decision
→ Generator
→ Gate Accepted
→ independent Coding Authorization
→ Implementation
```

Product Owner actions are limited to Approve, Amend, or Reject. The generator
owns all Gate document projection after approval.

## In Scope

- Governance Framework and ADR-0321 formal-standard status
- Exact nine-field Decision Summary
- Generated Gate/OD/RC/Approval/Signature/Evidence rules
- Three-state isolation
- Legacy Package interpretation migration

## Out of Scope

Repository product implementation, CRUD, Database, API, Runtime, Frontend,
Business Logic, Alembic, Runtime Manifest, and implementation milestones.

## OD dispositions

| OD | Decision | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | Sole Gate Framework | Accepted | ADR-0321 |
| OD-02 | Exact Decision Summary schema | Accepted | approved Summary + template |
| OD-03 | Product Owner interaction | Approve/Amend/Reject only | Framework standard |
| OD-04 | Legacy Package handling | Preserve evidence; migrate interpretation | migration register |
| OD-05 | Coding authority | Independent; defaults None | ADR-0321 |

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | One framework | PASS — no Package-specific workflow | ADR-0321 / rule |
| RC-02 | Summary-first | PASS — direct Gate submission forbidden | template / rule |
| RC-03 | PO form burden | PASS — manual OD/RC/etc. retired | Framework |
| RC-04 | Required generator output | PASS — all required sections specified | generator rules |
| RC-05 | State isolation | PASS — no automatic transitions | ADR-0321 |
| RC-06 | Implementation boundary | PASS — coding authorization None | Summary / Approval Record |
| RC-07 | Historical compatibility | PASS — evidence preserved | migration register |

## Risks

Historical documents may be mistaken for new approval or coding authority.
The migration register preserves their original dates and independent states.

## Approval Record

- Product Owner response: **Approve**
- Dates: 2026-07-28; **2026-07-29** (Framework Redesign review — Approve)
- Approved Summary:
  [PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md](PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md)
- Approval meaning: governance/design boundary only
- Coding Authorization: **None**
- Confirmed: Decision Summary mandatory; Approve/Amend/Reject only; generated
  artifacts after Approve; Gate Accept ≠ Coding Auth; one workflow for all
  Business Packages

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- ADR-0321 formal-standard text
- Phoenix Gate Framework operating standard
- Generator rules
- Decision Summary and generated Gate templates
- Legacy migration register
- Persistent Cursor workspace rule

## Implementation boundary

This Gate authorizes no product implementation or repository behavior change.
