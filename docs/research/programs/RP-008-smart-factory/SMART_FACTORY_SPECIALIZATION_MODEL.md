# Smart Factory Specialization Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-008-SFSM  
**Program:** RP-008 Smart Factory  
**Version:** 1.0  
**Status:** Research Draft  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Constraint ADRs (read-only):** ADR-0030 Brain/Twin; ADR-0027 AI Runtime; ADR-0008 approval  
**Upstream:** [EEM](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md); [CFM](../RP-003-capability-first/CAPABILITY_FIRST_MODEL.md); [AIRM](../RP-006-ai-infrastructure-platform/AI_INFRASTRUCTURE_REFERENCE_MODEL.md) ID-07  
**Consumers:** RP-010 EOM; Marketplace industry packages (later)

---

## Abstract

The Smart Factory Specialization Model (SFSM) specializes EERP discovery, capability, workforce, infrastructure, and evolution constructs for discrete/process plants — **without forking EAOS into an MES**. Plants compose Human / AI / Robot / Device under safety and approval discipline. Brain remains advisory (never direct machine control). Robotization follows EEM HOLD / RC safety cases. Dual-Track safe: research overlay until promoted; no Eng Kernel/Runtime industry openings from this draft alone.

## 1. Design Principles

1. **Overlay, not fork** — reuse Cap/DNA/EEM/AIRM; add plant specialization only.  
2. **No MES kernelization** — sites/units + Workflow approvals; MES stays integration.  
3. **Safety before smart** — “smart pilot” without safety case fails SFSM.  
4. **Physical risk explicit** — robot/device paths carry risk bands and HOLD pressure.  
5. **Line-side Terminal honesty** — glanceable approvals; offline/degraded rules.  
6. **OT as safety island** — aligns AIRM ID-07; unrestricted MES write forbidden.  
7. **Brain advisory only** — OEE/quality insights; never Act on machines.  
8. **Dual-Track safe** — research thesis; not Eng ticket generator.

## 2. Specialization Domain Catalog

| Domain ID | Name | Question | Failure mode |
|-----------|------|----------|--------------|
| SF-01 | Plant Capability Overlay | Which Cap IDs map to line/cell outcomes? | Dept-as-Cap on shop floor |
| SF-02 | Human/AI/Robot/Device Mix | Who executes which step class? | Role theater without R1/R2 |
| SF-03 | Physical Risk & Safety Case | What RC/safety evidence exists? | Smart pilot skips safety |
| SF-04 | Line-side Terminal UX | How are approvals/exceptions presented? | HQ-only UX forced on line |
| SF-05 | OT Event / Historian Coupling | How do OT facts become governed knowledge? | Historian = Knowledge truth |
| SF-06 | Robot / Cell Readiness | When may REC-ROBOT leave HOLD? | Agentize without RC case |
| SF-07 | Degraded / Offline Mode | What happens when cloud/OT link fails? | Silent fail-open mutate |
| SF-08 | Industry Package Scope | What OT scopes must packages declare? | Unsigned plant packs |

**Rule:** Claiming “smart factory ready” without SF-03/06 scored is a defect.

## 3. Physical Risk Bands (Research)

| Band | Name | Signal | EEM constraint hint |
|------|------|--------|---------------------|
| PR0 | Unknown | No safety case | Mandatory HOLD |
| PR1 | Desk / sim only | Simulation; no contact | Prefer Assist |
| PR2 | Guarded cell | Certified enclosure | Robot candidate w/ case |
| PR3 | Collaborative | Shared space; certified | Strict approval + HOLD easy |
| PR4 | Open / high energy | High hazard | HOLD unless exceptional case |

No composite “factory IQ.” Portfolio = Cap critical path + PR distribution + OT island readiness.

## 4. Coupling to Upstream Models

| Upstream | SFSM use |
|----------|----------|
| RP-001 / WT-01 | Plant dossier seed |
| RP-003 CFM | Cap overlay SF-01; Cap≠Org on shop floor |
| RP-005 ANRF | AI/Robot/Device role classes; Refuse unsafe Agentize |
| RP-006 AIRM | ID-07 OT island; approval bridge |
| RP-007 EEM | REC-ROBOT / HOLD; `execution_authority: none` |
| RP-009 BEM | Advisory OEE/quality; never machine Act |

## 5. Validation Constructs

| ID | Construct |
|----|-----------|
| V-SF-01 | Eight domains SF-01…08 scored with evidence tiers |
| V-SF-02 | Safety case present before PR2+ robot claims |
| V-SF-03 | No MES Kernel fork proposed |
| V-SF-04 | Brain/Twin never direct machine control |
| V-SF-05 | ≥2 synthetic plant walkthrough overlays — PW-01…02 Synthetic Complete |

## 6. Falsifiers

1. Smart pilot without SF-03 safety case.  
2. MES logic moved into Core Kernel.  
3. Brain/Twin authorize machine write.  
4. REC-ROBOT without PR band / RC case.  
5. Eng industry schema tickets from Research urgency alone.

## 7. Cross-Layer Impact (Potential)

| Layer | Impact |
|-------|--------|
| Architecture | Industry overlay packages / OT integration patterns |
| Kernel | Sites/units consumed — no MES kernelization |
| Runtime / AI Runtime | Edge constraints; OT tools high_impact |
| Smart Terminal | Line-side UX; offline rules |
| Enterprise Brain | Advisory OEE/risk only |
| Marketplace | Industry packs with declared OT scopes |
| Constitution / Blueprint | Safety/industry obligations — candidates only |

## 8. Promotion Stance

Current: **Research Draft v1.0**  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Plant overlays: PW-01…02 **Synthetic Complete** → Industry/Risk Draft ready → peer assignment.  
No Eng openings; robot paths remain HOLD-default until safety evidence.

## Related Documents

- [RP-008 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables](DELIVERABLES-RP-008.md)  
- [EEM](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  
- [AIRM ID-07](../RP-006-ai-infrastructure-platform/AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
