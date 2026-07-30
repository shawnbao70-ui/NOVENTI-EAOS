# Phoenix Gate Generator Rules

**System-generated governance standard**  
**Authority:** [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)  
**Status:** Accepted · sole generator contract  
**Coding Authorization:** None

## Input

The generator accepts only:

1. one approved Decision Summary using the exact nine-field schema;
2. the explicit Product Owner response `Approve`; and
3. immutable evidence links available at generation time.

`Amend` returns to Summary revision. `Reject` stops generation.

## Required outputs

After `Approve`, generate:

- Architecture Gate
- Gate Acceptance
- OD dispositions
- RC attestations
- Approval Record
- Signature
- Evidence

The Product Owner must not be asked to edit or complete any generated output.

## Required content in every generated Gate

1. ADR-0321 reference and Package ADR reference, if any
2. approved Decision Summary reference
3. Evidence reference
4. generated Approval Record
5. generated Signature
6. `Architecture Gate: Accepted (design boundary only)`
7. `Coding Authorization: None`
8. `Implementation Milestone: None`

## Projection rules

- OD rows are generated from `Open Decisions` and record Accepted, Deferred,
  or Amended dispositions without inventing a Product Owner choice.
- RC attestations are generated from Architecture Boundary, In Scope,
  Out of Scope, Risks, Constitution, Package/Kernel, Tenant, Permission,
  Audit, Event, privacy, and fail-closed evidence.
- Approval Record preserves the exact decision, actor, date, Summary link,
  and scope.
- Signature is a system projection of the explicit Product Owner decision,
  never a fabricated handwritten signature.
- Evidence contains links and truthful availability status; missing evidence
  is `Missing`, `Deferred`, or `Hold`, never silently treated as PASS.

## State isolation

```text
Accepted Knowledge          independent
Architecture Gate Accepted  independent
Coding Authorization        independent
```

No state transition triggers another. In particular, Gate Accepted never
creates CRUD, Alembic, API, runtime manifest, implementation milestone, or
business write authority.

## Validation and failure

Generation fails closed when:

- any Decision Summary field is missing or renamed;
- the PO response is not exactly Approve/Amend/Reject;
- evidence references are absent or misleading;
- a generated Gate implies coding authority; or
- a Package-specific workflow diverges from ADR-0321.

## Scope boundary

These rules generate governance documents only. They do not modify product
source, database, API, runtime, frontend, business logic, or host software.

This generator contract governs Business Package Product/Architecture Gates.
Historical Foundation engineering milestone Gates remain evidence under their
original format, but they cannot be used as a second Business Package Gate
framework or as a bypass around Decision Summary and independent Coding
Authorization.
