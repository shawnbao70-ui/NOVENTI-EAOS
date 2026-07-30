# Capability First Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-003-CFM  
**Program:** RP-003 Capability First  
**Version:** 1.0  
**Status:** Research Draft  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Upstream:** [RP-001 EDF](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md) (Cap≠Org)  
**Constrained by:** [RP-004 Organization Neutrality](../RP-004-organization-neutrality/README.md)  
**Consumers:** RP-005 (capability→role mapping); RP-007 (T-CAP-*); Marketplace indexing (later)

---

## Abstract

The Capability First Model (CFM) defines enterprises as **capability graphs** first and organization charts second. Capabilities are the primary lens for AI staffing, automation affinity, package adoption, and evolution recommendations. CFM never replaces Permission, never mints grants, and never treats a department name as a capability.

## 1. Design Principles

1. **Capability ≠ Organization** — org boxes are structure; capabilities are what the enterprise can do.  
2. **Capability ≠ Permission** — capability presence does not grant Runtime authority.  
3. **Graph over list** — dependencies and critical paths matter more than flat catalogs.  
4. **Ownership is a role class** — accountable human R1/R2 patterns, not “person-as-truth.”  
5. **Automation affinity is advisory** — scores guide REC-*, never auto-execute.  
6. **Evidence-linked** — each node cites Discovery dossier tiers (T1–T3).  
7. **Falsifiable** — Cap≠Org collapse invalidates CFM claims.  
8. **Dual-Track safe** — research construct until promoted.

## 2. Metamodel Catalog

### 2.1 Node: Capability

| Field | Meaning | Notes |
|-------|---------|-------|
| `capability_id` | Stable ID | Cross-dossier key |
| `name` | Human label | Not a dept name |
| `outcome` | Observable enterprise outcome | Measurable where possible |
| `level` | Maturity band L0–L4 | Research construct (see §3) |
| `automation_affinity` | A0–A4 | Advisory only |
| `knowledge_authority` | Who may assert truth | Links RP-001 knowledge domain |
| `evidence_refs` | Dossier citations | Tier-labeled |
| `confidence` | Low / Med / High | Facilitator judgment |

### 2.2 Edge: Dependency

| Edge Type | Meaning |
|-----------|---------|
| `requires` | Hard precondition capability |
| `amplifies` | Soft synergy (not blocking) |
| `conflicts` | Mutual exclusion / contention |
| `feeds` | Output of A is input to B |

### 2.3 Ownership Binding (non-person truth)

| Binding | Meaning |
|---------|---------|
| `owner_role_class` | Accountable role class (e.g., Quality Lead class) |
| `org_anchors` | Optional org units that *currently* house work — descriptive only |
| `ai_staffing_candidates` | Later RP-005 maps — no grant minting |

**Rule:** If facilitators cannot state a capability without naming a department, Cap≠Org has collapsed — HOLD claims C-CAP-02/03.

## 3. Capability Maturity Bands (Research)

| Level | Name | Signal |
|-------|------|--------|
| L0 | Absent / Unknown | No evidence of outcome delivery |
| L1 | Ad hoc | Heroics; undocumented |
| L2 | Defined | Documented process; uneven adherence |
| L3 | Managed | Measured; exceptions governed |
| L4 | Adaptive | Improves under change; evidence refresh |

No single enterprise “capability IQ.” Portfolio health = distribution + critical-path risk, not a composite score sold as truth.

## 4. Automation Affinity Bands (Research)

| Band | Meaning | Constraint Hint to RP-007 |
|------|---------|---------------------------|
| A0 | Human-only for now | Prefer REC-HOLD / Assist |
| A1 | Assistive AI OK | REC-ASSIST |
| A2 | Agentize candidate | REC-AGENTIZE only with supervision model |
| A3 | Robot / physical loop candidate | Requires RC5-class safety case |
| A4 | Device / edge candidate | Device governance required |

Affinity ≠ authorization. A2 does not open Role→grant or Brain execute.

## 5. Operating Method (Wave 2 Research)

| Step | Activity | Output |
|------|----------|--------|
| 1 | Seed from RP-001 capability catalog | Node draft list |
| 2 | Cap≠Org session (mandatory) | Strip dept-as-capability |
| 3 | Dependency mapping | Graph edges |
| 4 | Level + affinity scoring | Banded nodes |
| 5 | Critical-path & gap view | Portfolio risks |
| 6 | Export for RP-005 / RP-007 | Constraint + staffing inputs |

## 6. Validation Constructs

| ID | Construct |
|----|-----------|
| V-CAP-01 | Facilitators can separate Cap vs Org in ≤2 sessions (teachable) |
| V-CAP-02 | Graph edges change package/AI priorities vs flat list |
| V-CAP-03 | Affinity bands do not collapse to “automate everything” |
| V-CAP-04 | Ownership bindings never mint Permission |
| V-CAP-05 | Falsifiers include Cap≠Org collapse and dept-label theater |

## 7. Falsifiers

1. Workshops cannot name capabilities without org-chart language.  
2. Graphs add no decision value over departmental roadmaps.  
3. Affinity scores are used to auto-open Eng / Runtime paths.  
4. Marketplace indexing claims outcomes without evidence tiers.  
5. CFM is sold as HR/org redesign authority.

## 8. Cross-Layer Impact (Potential)

| Layer | Impact |
|-------|--------|
| Package / Marketplace | Capability-indexed packages later |
| Twin / Brain | Capability views & gap insights — advisory |
| Kernel | Descriptive registry candidate only — never authz |
| Terminal | Capability mapping canvases |
| Constitution / Blueprint | Candidates only; no edits now |

## 9. Promotion Stance

Current: **Research Draft v1.0**  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Graphs: **CG-01…02 Synthetic Complete** — [graphs/](graphs/)  
Industry/Risk: **Draft** — [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
Peer package: [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) — Assigned: **臻宇**（decision Pending）.  
Next: Pass → White Paper path.  
Architecture Review after Marketplace/Package thesis path. Remain Asset OK.

## Related Documents

- [RP-003 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables](DELIVERABLES-RP-003.md)  
- [Synthetic Graphs](graphs/README.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Risk Analysis](RISK_ANALYSIS.md)  
- [Peer Review Package](PEER_REVIEW_PACKAGE.md)  
- [EDF](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [ANRF](../RP-005-ai-workforce-transformation/AI_NATIVE_ROLE_FRAMEWORK.md)  
- [EEM](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  
