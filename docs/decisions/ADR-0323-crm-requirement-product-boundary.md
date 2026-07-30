# ADR-0323 — CRM Requirement Product Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**归属：** `noventi.crm` Business Package  
**授权源：** CRM Requirement Decision Summary

## Context

PHX-G295 delivered Opportunity. Accepted Legacy knowledge proves a Requirement
concept and an Opportunity 1:N relation, but also exposes optional parent links,
weak customer consistency, cache drift, unguarded lifecycle vocabulary, and
downstream Sample/Quote/Order coupling. Those defects are evidence, not product
law.

## Decision

C3 defines Requirement as an independently identified child aggregate that
must reference one active same-tenant Opportunity. It has a system-assigned
code, required title and optional description, plus `active` / `archived`
lifecycle and optimistic versioning.

All access uses trusted `ExecutionContext` and Permission Evaluate against
`pkg.crm.requirement`. C3 has no owner/salesperson field; any future owner must
never authorize. Write intents and outcomes are audited without storing title
or description in audit details.

## Explicitly Out

- Analysis, product matching, Sample, Quote, Convert, Sales Order, Finance
- Legacy requirement_count caches and downstream shortcut/link tables
- Legacy stage machine and AI analysis status
- Brain/Twin, runtime CRM events, hard delete, Customer360

## Gate Semantics

This ADR accepts the C3 design boundary only. Coding requires a separate
authorization and one assigned PHX-G milestone.

## Consequences

- C3 strengthens the parent relation from Legacy optionality to mandatory
  same-tenant Opportunity membership.
- No C4 Quote capability is implied or implemented.
