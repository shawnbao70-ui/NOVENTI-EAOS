# CRM Requirement Product Gate Acceptance

**状态：** Gate Accepted（design boundary only；system-generated）  
**日期：** 2026-07-24  
**规范源：** ADR-0323

## Product Owner authorization

Approve design boundary through the C3 conversation preauthorization.

## Accepted

- Requirement is a `noventi.crm` aggregate under one active same-tenant
  Opportunity.
- Opaque ID, system code, required title and optional description.
- Permission default-deny, audited writes, archive-first lifecycle.

## Deferred / Out

Analysis, matching, Sample, Quote, Convert, Sales Order, Finance, trace links,
Requirement360, AI fields, events, Brain/Twin and Legacy implementation.

## Outcome

**ACCEPTED — DESIGN BOUNDARY ONLY.** Coding is governed by the separate C3
Coding Authorization Summary.
