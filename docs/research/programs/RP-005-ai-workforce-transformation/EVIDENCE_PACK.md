# EVIDENCE-PACK-RP-005 — AI Workforce Transformation

**Research ID:** NRI-RP-005-EVID  
**Program:** RP-005 AI Workforce Transformation  
**Version:** 1.0  
**Status:** Defined (Research)  
**Objective:** Define evidence schema, claim map, role-inventory protocol, and White Paper freeze gate for ANRF — without opening Runtime grants or legal self-certification  
**Scope:** In: evidence pack definition, inventory protocol / Out: Kernel/Runtime/Const/BP/Implementation edits; live role-inventory capture (planned)  
**Author:** NRI  
**Reviewer:** 包锦昱（legal peer Pass — WP Draft Allowed）  
**Approval:** Pending — WP content Accepted；AR Candidate awaiting Board  
**Dependencies:** [ANRF](AI_NATIVE_ROLE_FRAMEWORK.md); [RP-005](README.md); RP-001 Evidence Pack pattern  
**Related Capability:** AI Workforce · Robot Workforce · Autonomous Devices  
**Related Blueprint:** BP-AI, BP-SMART-TERMINAL *(candidates)*  
**Related Constitution:** BOOK03 *(constraint + candidate)*  
**Related ADR:** ADR-0021 *(read-only)* · ADR-0162 · ADR-0169  
**Promotion Status:** Research Library — AR Candidate opened（Awaiting Board）  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Inventories:** [inventories/](inventories/) (RI-01…02 Synthetic Complete)  
**Architecture Review Candidate:** [ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md)（NRI-ARC-RP-005）  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Purpose

Make ANRF White Paper freeze **schedulable** by fixing claim↔tier maps, V-AW coverage, inventory protocol (≥2), and legal-peer gate — reusing RP-001 pack discipline under Dual-Track.

## 2. Evidence Pack Contents

| Slot | Artifact | Required for WP freeze | Notes |
|------|----------|------------------------|-------|
| E1 | Claim Register | Yes | §3 |
| E2 | Actor / Duty Coverage Matrix | Yes | V-AW-01 |
| E3 | Risk Separation Proof Map | Yes | ANRF §7 → claims |
| E4 | Role Inventory Protocol (×2 min) | Yes (protocol); instances planned | §5 |
| E5 | BOOK03 Alignment Checklist | Yes | V-AW-03 |
| E6 | Downstream Usability (RP-001/007) | Yes (draft) | No execute / no grant mint |
| E7 | Legal Peer Review Record | Yes before WP Approval | Counsel or legal-designated peer |
| E8 | Deliverables Checklist | Yes | [DELIVERABLES-RP-005.md](DELIVERABLES-RP-005.md) |

**WP evidence floor:** T1 + planned T2/T3; legal peer ≠ author.

## 3. Claim Register

| Claim ID | Claim | Current Tier | Target for WP | Source |
|----------|-------|--------------|---------------|--------|
| C-AW-01 | Human/AI/Robot/Device duties must be separated | T1 | T1 + planned T2 | ANRF §2–3; V-AW-01 |
| C-AW-02 | Humans retain legal/business residual responsibility (R1/R2) | T1 | T1 + legal peer | ANRF §1, §8; V-AW-02 |
| C-AW-03 | ANRF aligns to BOOK03 taxonomy without Const edit | T1 | T1 | ANRF §9; V-AW-03 |
| C-AW-04 | Fusion requires risk separation + legal constraints | T1 | T1 + planned T2 | ANRF §6–8; V-AW-04 |
| C-AW-05 | Org title ≠ permission grant | T1 | T1 + planned T3 | ANRF invariants; V-AW-05 |
| C-AW-06 | Risk classes RC0–RC7 are usable for autonomy bounds | T1 | planned T2 | ANRF §7 |
| C-AW-07 | Role families generalize across ≥2 industries | T0–T1 | planned T2/T3 | ANRF §5; falsifier #2 |
| C-AW-08 | Fusion does not raise incident rates vs baseline when controls held | T0 | planned T3/T4 | falsifier #3 |
| C-AW-09 | Outputs consumable by RP-007 without auto-mutation | T1 | T1 | ANRF §10 |
| C-AW-10 | AI is not a legal person in this framework | T1 | legal peer | ANRF §8 |

## 4. Actor / Duty Coverage (V-AW-01)

| Actor | Must Appear in Inventories | Forbidden Assignment |
|-------|---------------------------|----------------------|
| Human | Residual R1/R2 on material actions | “AI owns liability” |
| AI Employee / Agent / Assistant | Duties within RC controls | Final RC6 acts |
| Robot | Physical/safety-path duties only with certified controls | Uncertified RC5 autonomy |
| Device / Edge | Sensing/actuation with declared scope | Silent permission changes (RC7) |

## 5. Role Inventory Protocol (≥2)

| ID | Enterprise Flavor | Must Stress |
|----|-------------------|-------------|
| RI-01 | Office-heavy / knowledge services | License theater; RC3 external commit Holds |
| RI-02 | Operations-heavy / manufacturing | Robot/device duties; Cap≠title; RC5 safety |

Per inventory minimum record:

```text
inventory_id:
enterprise_flavor:
mode: synthetic | live
as_of:
role_classes_count: (target ≥30 for live; ≥12 for synthetic)
actor_separation_ok: yes | no
title_neq_grant_ok: yes | no
fusion_candidates: []
fusion_vetoes: []
risk_class_samples: [{role, rc, control}]
book03_alignment_notes:
legal_flags: []
rp001_dossier_refs: []
rp007_consumable: yes | no | partial
auto_grant_minted: never
```

| Inventory | Path | Status |
|-----------|------|--------|
| RI-01 | [inventories/RI-01-office-synthetic.md](inventories/RI-01-office-synthetic.md) | **Synthetic Complete** |
| RI-02 | [inventories/RI-02-ops-synthetic.md](inventories/RI-02-ops-synthetic.md) | **Synthetic Complete** |

Index: [inventories/README.md](inventories/README.md). Live T3 inventories remain planned.

## 6. Falsifier Test Plan

| Falsifier (ANRF §11) | Observation | WP Expectation |
|----------------------|-------------|----------------|
| Demand AI legal ownership | Legal peer + RI notes | Hold C-AW-02/10 if demanded as design |
| Families collapse to abstraction | RI-01/02 coverage | Document industry overlays |
| Fusion raises incidents | Pilot metrics later | Do not claim safety improvement yet |
| Title≠grant breaks in pilots | Permission mapping check | Hold C-AW-05 |
| Irremediable BOOK03 conflict | Legal/const peer | Hold promotion path |

## 7. Downstream Usability

| Consumer | Required Outputs | Non-negotiable |
|----------|------------------|----------------|
| RP-001 | Role classes consume Org Map / Cap Graph | Discovery first where missing |
| RP-007 | Hold/Assist/Agentize/Robotize/Refuse | No automatic mutations |
| Eng / Permission | — | **No** grant mint from ANRF |

## 8. White Paper Freeze Gate

| Gate Item | Ready? |
|-----------|--------|
| Evidence pack defined | **Yes** |
| Deliverables checklist instantiated | **Yes** |
| Claim register | **Yes** |
| ≥2 role inventories completed | **Yes** — RI-01…02 synthetic (T1) |
| Legal peer review | **Pass — 包锦昱** (WP Draft Allowed; 2026-07-21) |
| White Paper draft | **Yes** — [WHITE_PAPER-RP-005.md](WHITE_PAPER-RP-005.md) （**Accepted**） |
| Architecture Review Candidate | **Opened** — [ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md)（NRI-ARC-RP-005；Awaiting Board） |
| V-AW-01…05 covered in ANRF text | **Yes** (framework + synthetic inventory proof) |

**Decision:** Peer Pass + WP content Accepted recorded. Architecture Review Candidate Package opened（NRI-ARC-RP-005）— **Awaiting Board**；do **not** self-certify Board outcome；no Eng ingest；**Role→grant mint NOT opened**；Title≠Permission；Cap≠grant；AI not legal person；`auto_grant_minted: never`.

## 9. Hard Boundaries

No Constitution / Blueprint / Kernel / Runtime / DB / product changes.  
No Twin authorize / Brain execute / payment clearing / Role→grant auto-write.  
Do not self-certify Architecture Review Board Promote/Hold/Reject.

## 10. Next Research Track Steps

1. ~~Author RI-01 / RI-02 synthetic inventories~~ **Done.**  
2. ~~Industry/Risk Draft~~ **Done.**  
3. ~~Legal peer Pass~~ **Done — 包锦昱** ([PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md)).  
4. ~~Open White Paper draft + content Acceptance~~ **Done** — [WHITE_PAPER-RP-005.md](WHITE_PAPER-RP-005.md) Accepted.  
5. ~~Open Architecture Review Candidate Package~~ **Done** — [NRI-ARC-RP-005](ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md)；Board decision pending.  
6. Optional：live T2/T3 evidence deepenings（honest tiers）.

## Related Documents

- [ANRF](AI_NATIVE_ROLE_FRAMEWORK.md)  
- [Architecture Review Candidate](ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md)（NRI-ARC-RP-005）  
- [DELIVERABLES-RP-005](DELIVERABLES-RP-005.md)  
- [Inventory Index](inventories/README.md)  
- [RP-001 Evidence Pack](../RP-001-enterprise-discovery/EVIDENCE_PACK.md)  
- [Dual-Track Playbook](../../../project/DUAL_TRACK_GOVERNANCE.md)  
- [AED v1.1](../../../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
