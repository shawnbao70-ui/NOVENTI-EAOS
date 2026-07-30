# Phoenix Gate Framework — Legacy Package Migration Register

**System-generated governance artifact**  
**Authority:** [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)  
**Status:** Accepted migration interpretation  
**Coding Authorization:** None

## Migration rule

Existing Gate/Acceptance/ADR documents remain immutable historical evidence.
They are not bulk rewritten, re-approved, or converted into coding authority.
From 2026-07-28 onward, every new or amended Gate uses the sole Phoenix Gate
Framework and its Decision Summary → PO Decision → Generator workflow.

Legacy manual OD, RC, Approval Table, Signature, Evidence, and long-form
PO-edit workflows are retired. Existing populated tables remain evidence only.

Legacy headings such as `Authorization Summary`, `Gate In`, `Gate Out`,
`Decisions`, and `Major architectural decisions` are interpreted as historical
aliases only. They do not define a second schema. A new or amended Gate must
use the exact ADR-0321 field names and must not merge design approval with
Coding Authorization.

## Package register

| Package | Migration status | Historical evidence treatment | Coding Authorization |
|---|---|---|---|
| CRM | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |
| Inventory | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |
| Purchase | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |
| Finance | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |
| Workflow | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |
| Marketplace | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |
| Enterprise Brain | Migrated to ADR-0321 interpretation | Preserve original ADR/Gate/Acceptance links | Independent; no change |

Approval Package documents are governed by the same Workflow/Package standard;
they do not create a separate Gate framework.

## State preservation

Migration does not change:

- Accepted Knowledge
- Architecture Gate Accepted
- Coding Authorization

These states remain independent and retain their original evidence dates.

## Future amendments

Any future Package Gate change starts with the exact nine-field Decision
Summary. Product Owner input is limited to Approve, Amend, or Reject.
Generated artifacts must use
`templates/GENERATED_ARCHITECTURE_GATE.md` and
`templates/GENERATED_ACCEPTANCE.md`, under
`PHOENIX_GATE_GENERATOR_RULES.md`.

## Scope boundary

This register changes governance interpretation only. It does not modify
Repository implementation, CRUD, Database, API, Runtime, Frontend, Business
Logic, Alembic, or Runtime Manifest.
