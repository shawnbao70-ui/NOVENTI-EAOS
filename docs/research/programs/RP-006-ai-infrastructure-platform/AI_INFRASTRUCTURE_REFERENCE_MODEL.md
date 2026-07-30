# AI Infrastructure Reference Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-006-AIRM  
**Program:** RP-006 AI Infrastructure Platform  
**Version:** 1.0  
**Status:** Research Draft  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Constraint ADRs (read-only):** ADR-0027 AI Runtime boundary; ADR-0008 approval; ADR-0007 tenant isolation; ADR-0030 Brain/Twin  
**Upstream:** [RP-001 EDF](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md) (Infrastructure Discovery)  
**Consumers:** RP-007 readiness gates; RP-008 OT coupling; RP-009 inference capacity (advisory)

---

## Abstract

The AI Infrastructure Reference Model (AIRM) defines governed landing zones for enterprise AI — identity landing, model hosting, tool fabrics, approval bridges, observability, edge/OT coupling, and supply-chain trust — aligned to EAOS Runtime/AI Runtime boundaries. AIRM is a **readiness and topology thesis**, not a product BOM and not a Kernel bypass. GPU/capacity without governance is treated as a defect. Dual-Track safe: research construct until promoted; no Eng Runtime schema openings from this draft alone.

## 1. Design Principles

1. **Governance before GPUs** — capacity without approval/audit/isolation fails AIRM.  
2. **AI Runtime is the control plane** — all enterprise AI lands via Runtime boundaries (ADR-0027 read-only).  
3. **No Kernel bypass** — infra shortcuts must not mint grants or skip Permission/Workflow.  
4. **Approval bridge truth** — high-impact paths use Workflow approval; no parallel approval state.  
5. **Tenant isolation first** — multi-tenant and multi-entity isolation are first-class.  
6. **Signed supply chain** — models/tools/packages need verification chains (Marketplace later).  
7. **Edge/OT as safety islands** — OT coupling is constrained, not unrestricted agent reach.  
8. **Dual-Track safe** — research readiness checklist; not Eng ticket generator.

## 2. Domain Catalog

| Domain ID | Name | Question | Failure mode |
|-----------|------|----------|--------------|
| ID-01 | Identity Landing | How do AI subjects / employees land in Identity? | Orphan agents without subject_id |
| ID-02 | Model Hosting | Where do models run; who owns keys/prompts? | Shadow SaaS; key sprawl |
| ID-03 | Tool Fabric | How are tools registered, sandboxed, invoked? | Unregistered high-impact tools |
| ID-04 | Approval Bridge | How do high-impact actions reach Workflow? | Parallel approval bots |
| ID-05 | Observability & Audit | Are runs/tools/commits correlatable? | Unauditable AI |
| ID-06 | Tenant / Data Isolation | Are tenancy and data planes enforced end-to-end? | Cross-tenant leakage |
| ID-07 | Edge / OT Coupling | How does OT/edge AI stay bounded? | Plant agents with open MES write |
| ID-08 | Supply-Chain Trust | Are models/tools/packages signed & verifiable? | Unsigned artifact install |

**Rule:** Claiming “AI-ready infra” without scoring all eight domains is a defect.

## 3. Readiness Bands (Research)

| Band | Name | Signal |
|------|------|--------|
| I0 | Absent | No governed landing; shadow AI dominant |
| I1 | Ad hoc | Some Runtime use; tools unregistered; weak audit |
| I2 | Defined | Landing zones documented; approval bridge present |
| I3 | Managed | Isolation + observability measured; supply-chain checks |
| I4 | Adaptive | Continuous infra evidence refresh; OT islands governed |

No single “infra IQ.” Portfolio readiness = domain distribution + critical-path gaps (e.g., ID-04/06 before scale).

## 4. Alignment to EAOS Boundaries (Read-Only)

| Layer | AIRM stance |
|-------|-------------|
| AI Runtime (`runtime/ai/`) | Primary landing; tool register/invoke; approval bridge |
| Core Kernel | Consumed for Identity/Permission/Workflow — never bypassed |
| Knowledge | Access via Shared Knowledge; Memory ≠ Knowledge |
| Brain / Twin | Capacity planning only; no Brain-execute / Twin-authorize from infra |
| Marketplace / Package | Signed distribution candidates post-promotion |
| Smart Terminal | Hosting / CSP / degraded modes — observational |

## 5. Validation Constructs

| ID | Construct |
|----|-----------|
| V-INF-01 | Eight domains ID-01…08 scored with evidence tiers |
| V-INF-02 | Approval bridge present for high-impact tools |
| V-INF-03 | No Kernel bypass / grant mint from infra topology |
| V-INF-04 | Tenant isolation asserted across model/tool/host paths |
| V-INF-05 | ≥2 synthetic gap profiles (cloud-native + hybrid OT) — GP-01…02 Synthetic Complete |

## 6. Falsifiers

1. GPU/capacity roadmap sold as AIRM-complete without ID-04/05/06.  
2. Infra diagram opens Kernel grant shortcut.  
3. Parallel approval system outside Workflow.  
4. OT agents with unrestricted mutating reach claimed “I3+.”  
5. Eng Runtime schema tickets opened from Research urgency alone.

## 7. Cross-Layer Impact (Potential)

| Layer | Impact |
|-------|--------|
| Architecture | Runtime/AI topology candidates |
| Kernel | Dependencies only — no schema from Research |
| Runtime / AI Runtime | Core subject — research readiness, not code rewrite |
| Smart Terminal | Hosting / degraded modes |
| Enterprise Brain | Inference/sim capacity — advisory path only |
| Marketplace | Artifact registry / verification chains later |
| Constitution / Blueprint | Security/AI infra obligations — candidates only |

## 8. Promotion Stance

Current: **Research Draft v1.0**  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Gap profiles: GP-01…02 **Synthetic Complete** → Industry/Risk Draft ready → peer assignment.  
No Eng Runtime openings; Explicit Defer items remain Eng-owned.

## Related Documents

- [RP-006 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables](DELIVERABLES-RP-006.md)  
- [ADR-0027](../../../decisions/ADR-0027-ai-runtime-boundary.md) *(read-only)*  
- [ADR-0008](../../../decisions/ADR-0008-ai-human-approval.md) *(read-only)*  
