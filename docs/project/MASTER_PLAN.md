# Master Plan

**Program:** Project Phoenix  
**Product:** NOVENTI Enterprise AI Operating System (EAOS)  
**Version:** 3.0  
**Repository:** `NOVENTI-EAOS`  
**Document ID:** PHX-MASTER-PLAN

---

## Title

NOVENTI EAOS Master Plan

## Purpose

Define the permanent mission, principles, repository boundary, and phase sequence for building EAOS as a new platform — not an ERP upgrade, refactor, or legacy modernization.

## Scope

In scope:

- Platform mission and non-goals
- Development principles
- Repository separation rules
- Phoenix phase sequence
- Source-of-truth priority

Out of scope:

- Legacy code modification
- Premature business module implementation

## Project Name

**NOVENTI Enterprise AI Operating System (EAOS)**

## Mission

Transform enterprise operations through a next-generation Enterprise AI Operating System via progressive architectural evolution inside `NOVENTI-EAOS`, using Legacy only as a read-only business knowledge repository.

## Development Principles

1. Constitution First  
2. Architecture First  
3. Kernel First  
4. AI Native  
5. Knowledge Driven  
6. Backward Compatible (tenant evolution — not Legacy architecture inheritance)
7. Dual-Track Governance — Engineering Track + Research Track (NRI); research never bypasses promotion ([ADR-0162](../decisions/ADR-0162-dual-track-governance.md)); autonomous execution per [AED v1.1](AUTONOMOUS_EXECUTION_DIRECTIVE.md) / [ADR-0169](../decisions/ADR-0169-autonomous-execution-directive.md)
8. Sole Gate Framework — every Business Package uses the nine-field Decision
   Summary and generated Phoenix Gate workflow
   ([ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)); Gate Accepted
   never implies Coding Authorization.

## Development Order

Constitution → Ownership Classification → Blueprint → Standards → ADR → Interfaces → Data Models → Implementation → Testing → Documentation → Review → Release / Optimization

## Governance Model (Dual-Track)

| Track | Role | Writable home |
|-------|------|---------------|
| **Engineering** | Foundation stability, Explicit Defer openings, release trains, ADR → Implementation | Product source + `docs/project` / `docs/decisions` (Eng) |
| **Research (NRI)** | Permanent research product; validated future models | `docs/research/**` only |

**Legal bridge:** Research Library → Architecture Review → Blueprint → Constitution Review → ADR/Gate → Implementation → Release (promotion optional).  
**Playbook:** [DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md)

## 当前阶段

**已完成：** PHX-000–PHX-006、PHX-G01～G02、PHX-A03、PHX-K07～K10、PHX-P11、PHX-A12、PHX-T13、PHX-B14、PHX-E15、PHX-M16（技术）、PHX-R17、PHX-G18、PHX-E19～E21、PHX-G20～G32、PHX-G34～G142、**PHX-G143 Dual-Track Governance Formalization**、**PHX-G150 Autonomous Execution Directive**  
**当前基线：** EAOS Phoenix Foundation `0.2.3`（prior `0.2.2` / PHX-G376；`0.2.1` / G144；`0.2.0` / R17）；Dual-Track Accepted（ADR-0162）；AED v1.1 Accepted（ADR-0169）；PHX-G404 Fully Accepted；外部 PSP / ENABLE_*_NETWORK 默认 OFF  

## Repository Boundary

| Repository | Role |
|------------|------|
| `H:\Workspace\NOVENTI-EAOS` | Sole writable development repository |
| Legacy `EZAM_CRM-9.0` / `EZAM_CRM - 9.0` | Permanently read-only |

## Platform Capabilities (Target)

Enterprise · Digital Employees · AI Workforce · Knowledge Graph · Enterprise Brain · Digital Twin · Workflow Engine · Event Driven Architecture · Plugin Ecosystem · Marketplace · Industry Packages · Global Multi-Tenant Platform

## Future Expansion

- Engineering Track: optional deepening after thin postures（`0.2.1` train done as PHX-G144；WebAuthn/MFA thin posture done as PHX-G145；Role→grant thin posture done as PHX-G146；OIDC login product surface done as PHX-G147 / T-0189；OpenAPI inventory posture done as PHX-G148 / T-0188 partial；Eng tip hygiene done as PHX-G149 / [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)；AED v1.1 done as PHX-G150 / [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md)；payment clearing still 暂缓）
- Research Track: NRI Wave 1 frameworks → Architecture Review only when validated
- Selective promotion into Blueprint / Constitution (never research-direct)
- EAOS Version 2.0 release train only after promoted constitutional readiness

## Related Documents

- [PROJECT_STATUS.md](PROJECT_STATUS.md)
- [ROADMAP.md](ROADMAP.md)
- [DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md)
- [PHOENIX_ROADMAP_V3.md](PHOENIX_ROADMAP_V3.md)
- [MIGRATION_STATUS.md](MIGRATION_STATUS.md)
- [../research/README.md](../research/README.md)
- [../blueprint/BLUEPRINT_INDEX.md](../blueprint/BLUEPRINT_INDEX.md)
