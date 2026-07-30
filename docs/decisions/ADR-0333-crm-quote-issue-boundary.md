# ADR-0333 — CRM Quote Issue Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G306

## Decision

C13 adds Quote status `issued` and `issue_quote` as a local publish command.
Issuance requires human confirmation and at least one active quote line, is
idempotent by issue key, and is authorized by default-deny action `issue` on
`pkg.crm.quote`.

After issue, header and line commercial edits fail closed. `convert_quote`
accepts only issued quotes. This is not an Approval Center or Workflow product
surface and does not send documents.

## Out

Email/PDF, Approval Center, Workflow authoring, Invoice issue/post, PSP, GL,
WMS/ship, Brain/Twin, and C14+.
