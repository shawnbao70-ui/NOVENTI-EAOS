# RISK-ANALYSIS-RP-001 — Enterprise Discovery

**Research ID:** NRI-RP-001-RISK  
**Program:** RP-001 Enterprise Discovery  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register legal, operational, adoption, architectural, and research-integrity risks for Enterprise Discovery before White Paper freeze  
**Scope:** In: risk register, residual risk posture, hold conditions / Out: product SLOs, security certifications, Constitution/Blueprint edits, Runtime privilege design  
**Author:** NRI  
**Reviewer:** 臻宇（via PEER package；peer Pass recorded）  
**Approval:** Pending — Architecture Review Candidate awaiting Board（WP content Accepted）  
**Dependencies:** [EDF](ENTERPRISE_DISCOVERY_FRAMEWORK.md); [EVIDENCE_PACK](EVIDENCE_PACK.md); [INDUSTRY_ANALYSIS](INDUSTRY_ANALYSIS.md); WT-01…03  
**Related Capability:** Enterprise Discovery  
**Related Blueprint:** BP-KNOWLEDGE, BP-AI, BP-SMART-TERMINAL *(candidates)*  
**Related Constitution:** BOOK02, BOOK03, BOOK04 *(candidates / constraints)*  
**Related ADR:** ADR-0030 Brain advisory constraint *(read-only)*; Dual-Track ADR-0162 *(governance)*  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Risk Posture Summary

Enterprise Discovery is **advisory process research**. Highest residual risks are (a) discovery outputs being mistaken for execution authority, (b) sensitive org/knowledge data mishandled in pilots, and (c) maturity theater contaminating Evolution Engine inputs. Dual-Track fail-closed production invariants (Brain execute, Twin authorize) are **non-negotiable mitigations**.

## 2. Risk Register

| Risk ID | Category | Description | Likelihood | Impact | Mitigation | Residual | Owner |
|---------|----------|-------------|------------|--------|------------|----------|-------|
| R-ED-01 | Architectural | Dossier treated as Runtime grant / execute authority | Med | Critical | Advisory-only language; V-ED-03; Dual-Track no Eng ingest | Low if gates hold | NRI + Arch |
| R-ED-02 | Constitutional | Premature BOOK/BP edits from research drafts | Low–Med | High | Promotion Rules; Research hard write ban | Low | NRI |
| R-ED-03 | Legal / Privacy | Pilot interviews expose PII, client IP, OT secrets | Med | High | Observational pilot data rules; minimize; no prod DB | Med until pilot plan | NRI + Legal (future) |
| R-ED-04 | Operational | Cap≠Org collapses under workshop time pressure | Med | Med | Mandatory separate sessions; WT checklists | Med | Facilitators |
| R-ED-05 | Adoption | License theater reasserts; EDF skipped | High | Med | Industry Analysis P1/P3; Terminal later must not score seats as readiness | Med | Product (post-promote) |
| R-ED-06 | Research integrity | Synthetic walkthroughs over-claimed as T3 | Med | High | Explicit T1 labeling; WP freeze requires honesty on tiers | Low if labeled | NRI |
| R-ED-07 | Method | AI Readiness bands fail predictive validity | Med | Med | Falsifier open; no Runtime coupling | Med | NRI |
| R-ED-08 | Method | DNA axes unstable across cycles | Med | Med | Two-pass protocol planned; don’t freeze DNA as product schema | Med | NRI / RP-002 |
| R-ED-09 | Operational | Discovery effort exceeds decision value | Med | Med | Time-to-dossier bounds; scope reduce | Med | Facilitators |
| R-ED-10 | Downstream | RP-007 consumes vanity stage labels | Med | High | WT-03 criterion hits; V-ED-04 | Med | RP-001/007 |
| R-ED-11 | Downstream | RP-005 mints roles from org boxes | Low–Med | High | Cap≠Org + ANRF constraints; no grant minting | Low if held | RP-005 |
| R-ED-12 | Safety / Compliance | Discovery advice implies bypass of safety controls | Low | Critical | Compliance Reflex DNA; Hold agentic actions in regulated contexts | Low | NRI |
| R-ED-13 | Commercial | Marketplace “assessment packs” sold before validation | Low | Med | Marketplace impact = later; fail-closed clearing unrelated | Low | Product |
| R-ED-14 | Governance | Research urgency opens Eng Explicit Defer | Low | Critical | Dual-Track sync; numbered Eng approvals only | Low | Phoenix Gov |

## 3. Falsifier ↔ Risk Map

| EDF Falsifier | Primary Risks | Hold Condition |
|---------------|---------------|----------------|
| Cap/Org collapse | R-ED-04, R-ED-11 | Hold WP claims C-ED-02/10 |
| AI bands ≤ coin-flip | R-ED-07 | Do not claim predictive validity |
| DNA instability | R-ED-08 | Keep DNA research-only; deepen via RP-002 |
| Roadmap ≈ vendor checklist | R-ED-05 | Rewrite roadmap method |
| Effort > decision value | R-ED-09 | Reduce domain depth / workshop count |

## 4. Legal & Data Handling (Wave 1)

| Topic | Rule (Research) |
|-------|-----------------|
| Synthetic dossiers | No real PII; codenames only |
| Live pilots (future) | Separate Pilot Plan + data processing record; opt-in |
| Shadow organization findings | Sensitive; restrict distribution |
| Client / OT secrets | Redact in Library artifacts |
| Cross-border data | Out of Wave 1 scope; flag if encountered |

## 5. Adoption Risks by Persona

| Persona | Risk | Counter |
|---------|------|---------|
| CIO / AI sponsor | Buys seats, skips discovery | Industry P1/P3 narrative |
| Plant / OT lead | Distrusts IT-led discovery | Separate Knowledge authority capture |
| HR / workforce | Fears AI role replacement framing | RP-005 residual human accountability |
| Risk / Legal | Blocks all AI | Assistive-first roadmap + Hold classes |
| Architecture | Wants schema now | Dual-Track; no Kernel edits |

## 6. Residual Risk Acceptance (Research Stage)

Accepted for **Research Draft → White Paper scheduling**:

- T1 synthetic evidence only (R-ED-06 mitigated by labeling)  
- Predictive validity of bands open (R-ED-07)  
- DNA stability open (R-ED-08)  

**Not accepted** at any stage:

- Auto-execution implication (R-ED-01)  
- Silent Constitution/Blueprint edits (R-ED-02)  
- Eng ingest without Promote + ADR (R-ED-14)

## 7. White Paper Hold Triggers

Escalate to **Hold** (do not Approve WP) if:

1. Peer review finds Cap≠Org method unteachable.  
2. Evidence tiers are mislabeled as T3/T4.  
3. Any artifact proposes Runtime execute/authorize openings.  
4. Industry Analysis patterns contradicted without register update.

## 8. Hard Boundaries

No Constitution / Blueprint / Kernel / Runtime / DB / product source changes. No payment clearing / Twin authorize / Brain execute openings.

## Related Documents

- [EDF §7 Falsifiers](ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [Evidence Pack §6](EVIDENCE_PACK.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Deliverables Checklist](DELIVERABLES-RP-001.md)  
- [Dual-Track Playbook](../../../project/DUAL_TRACK_GOVERNANCE.md)  
