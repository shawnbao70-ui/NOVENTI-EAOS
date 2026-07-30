# ADR-0324 — CRM Quote Product Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**归属：** `noventi.crm` Business Package

## Context

PHX-G296 delivered Requirement. Legacy knowledge proves a rich Quotation
domain but also exposes inconsistent states, bypassable approval, mixed
pricing semantics and best-effort conversion links. C4 must not imply those
capabilities are trustworthy or accepted.

## Decision

C4 introduces only a Quote draft shell under one active same-tenant
Requirement: opaque ID, system code, three-letter currency label, optional
notes, `draft` / `archived` status and optimistic versioning.

All access uses `pkg.crm.quote` Permission evaluation. Writes record intent and
result audits without storing notes. No owner field or authorization shortcut
is introduced.

## Explicitly Out

Lines, products, pricing, amounts, tax, discount, FX calculation, margin,
issuance, approval, conversion, Sales Order, Finance/PSP, Sample, documents,
templates, AI, Brain/Twin and runtime CRM events.

## Consequences

C4 can demonstrate secure quote-header creation and traceability to
Requirement, but must not be represented as a priced, issued or approved
commercial offer.

## Gate Semantics

Design boundary only. Coding requires one separate contiguous PHX-G milestone.
