# NOVENTI Research Institute (NRI)

**Program:** Project Phoenix  
**Institute:** NOVENTI Research Institute (NRI)  
**Research Program Family:** Enterprise Evolution Research Program (EERP)  
**Status:** PERMANENT — governed by Research Governance Charter v1.0  
**Repository Path:** `docs/research/`  
**Last Updated:** 2026-07-21

---

## Supreme Directive

**[Research Governance Charter v1.0](RESEARCH_GOVERNANCE_CHARTER.md)** is the permanent governing directive for all NRI activity.

On conflict with any other NRI document, the Charter prevails.

## Mission

Continuously discover, study, validate and model the future evolution of intelligent enterprises.

Research is a permanent product of NOVENTI.  
Every validated research result becomes a long-term strategic asset.

## Position in EAOS Governance

```text
EAOS Constitution
        ↓
Phoenix Governance  (Dual-Track — ADR-0162)
        ├── Engineering Track
        └── NRI Research Governance
                ↓
            Research Programs
                ↓
        (optional Promote)
                ↓
Blueprint → Architecture Decision → Constitution → Implementation
```

**Phoenix Dual-Track playbook:** [../project/DUAL_TRACK_GOVERNANCE.md](../project/DUAL_TRACK_GOVERNANCE.md) · [ADR-0162](../decisions/ADR-0162-dual-track-governance.md)

Research never bypasses this governance hierarchy.

## Core Principles

Research First · Capability First · Organization Neutrality · Enterprise Discovery First  
Architecture Before Blueprint · Blueprint Before Constitution · Constitution Before Implementation  
Research Is A Product · Knowledge Is A Product · Enterprise Evolution Is Continuous  
EAOS Adapts To Enterprises · Enterprises Shall Not Adapt To Software

## Mandatory Lifecycle

```text
Idea → Research → White Paper → Capability Model → Prototype → Enterprise Pilot
  → Architecture Review → Blueprint → Constitution Review → Implementation
  → Product Release → Continuous Evolution
```

No capability may directly enter Blueprint, Constitution, or Implementation without validation.

## Hard Boundaries

| Allowed | Forbidden |
|---------|-----------|
| Research documents & models | Runtime / Kernel / Source Code / Database modification |
| Impact & migration recommendations | Constitution / Blueprint / Implementation edits |
| Prototypes (research-scoped) | Production shortcuts |
| Permanent Research Library assets | Bypass of Phoenix / NRI governance |

Research produces recommendations only. Implementation requires separate approval.

## Directory Map

```text
docs/research/
├── RESEARCH_GOVERNANCE_CHARTER.md    # Permanent governing directive
├── README.md                         # This overview
├── RESEARCH_LIBRARY.md               # Permanent asset registry
├── RESEARCH_INDEX.md
├── RESEARCH_ROADMAP.md
├── RESEARCH_STANDARDS.md
├── RESEARCH_METHODOLOGY.md
├── RESEARCH_VALIDATION_RULES.md
├── RESEARCH_PROMOTION_RULES.md
├── templates/
└── programs/RP-001 … RP-010/
```

## Generation-1 Programs

| ID | Program | Priority |
|----|---------|----------|
| RP-001 | Enterprise Discovery | P0 |
| RP-002 | Enterprise DNA | P1 |
| RP-003 | Capability First | P1 |
| RP-004 | Organization Neutrality | P2 |
| RP-005 | AI Workforce Transformation | P0 |
| RP-006 | AI Infrastructure Platform | P2 |
| RP-007 | Enterprise Evolution Engine | P0 |
| RP-008 | Smart Factory | P2 |
| RP-009 | Enterprise Brain Evolution | P1 |
| RP-010 | Future Enterprise Operating Model | P1 |

Additional programs may be created when justified under the Charter.

## First-Wave Frameworks

1. [Enterprise Discovery Framework](programs/RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
2. [AI-Native Role Framework](programs/RP-005-ai-workforce-transformation/AI_NATIVE_ROLE_FRAMEWORK.md)  
3. [Enterprise Evolution Model](programs/RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  

## Related Documents

- [Governance Charter](RESEARCH_GOVERNANCE_CHARTER.md)  
- [Research Library](RESEARCH_LIBRARY.md)  
- [Research Index](RESEARCH_INDEX.md)  
- [Promotion Rules](RESEARCH_PROMOTION_RULES.md)  
- [Validation Rules](RESEARCH_VALIDATION_RULES.md)  
- [Phoenix Dual-Track Playbook](../project/DUAL_TRACK_GOVERNANCE.md) · [ADR-0162](../decisions/ADR-0162-dual-track-governance.md)  
- [Wave 1 Peer Assignment](WAVE1_PEER_ASSIGNMENT.md) *(real human names required)*  
- EAOS Constitution / Blueprint *(read-only references)*  
