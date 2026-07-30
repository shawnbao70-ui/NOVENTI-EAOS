# NRI Research Library

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-LIB  
**Version:** 1.0  
**Status:** Permanent Registry  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md)  
**Last Updated:** 2026-07-21

---

## Purpose

Permanent repository of NRI research assets. Research may remain here indefinitely; promotion to Blueprint / ADR / Constitution / Implementation / Product is optional and validation-gated.

## Library Rules

1. Every research document MUST carry Charter-required metadata.  
2. Superseded versions remain readable; status becomes `Archived` with successor pointer.  
3. Library membership does **not** authorize implementation.  
4. Assets marked `Research Asset (Permanent)` are first-class products of NOVENTI even if never promoted.

## Required Metadata Block

```text
Research ID:
Version:
Status:
Objective:
Scope:
Author:
Reviewer:
Approval:
Dependencies:
Related Capability:
Related Blueprint:
Related Constitution:
Related ADR:
Promotion Status:
```

## Governance Assets

| Research ID | Title | Version | Status | Promotion Status | Path |
|-------------|-------|---------|--------|------------------|------|
| NRI-GOV-CHARTER | Research Governance Charter | 1.0 | Permanent Governing Directive | Research Library (Normative) | [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md) |
| NRI-INDEX | Research Index | 1.0 | Active | Research Library | [RESEARCH_INDEX.md](RESEARCH_INDEX.md) |
| NRI-ROADMAP | Research Roadmap | 1.0 | Approved | Research Library | [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) |
| NRI-STD | Research Standards | 1.1 | Normative | Research Library | [RESEARCH_STANDARDS.md](RESEARCH_STANDARDS.md) |
| NRI-MET | Research Methodology | 1.0 | Normative | Research Library | [RESEARCH_METHODOLOGY.md](RESEARCH_METHODOLOGY.md) |
| NRI-VAL | Validation Rules | 1.1 | Normative | Research Library | [RESEARCH_VALIDATION_RULES.md](RESEARCH_VALIDATION_RULES.md) |
| NRI-PROMO | Promotion Rules | 1.1 | Normative | Research Library | [RESEARCH_PROMOTION_RULES.md](RESEARCH_PROMOTION_RULES.md) |
| NRI-LIB | Research Library Registry | 1.0 | Permanent Registry | Research Library | This document |

## Generation-1 Program Assets

| Research ID | Title | Version | Status | Author | Reviewer | Approval | Related Capability | Related Blueprint | Related Constitution | Related ADR | Promotion Status | Path |
|-------------|-------|---------|--------|--------|----------|----------|--------------------|-------------------|----------------------|-------------|------------------|------|
| NRI-RP-001 | Enterprise Discovery Program | 1.1 | Research | NRI | 臻宇 | Pending | Enterprise Discovery | BP-KNOWLEDGE / BP-SMART-TERMINAL / BP-AI (candidates) | BOOK02 / BOOK04 (candidates) | TBD | Research Library | [programs/RP-001-enterprise-discovery/](programs/RP-001-enterprise-discovery/) |
| NRI-RP-001-EDF | Enterprise Discovery Framework | 1.0 | Research Draft | NRI | 臻宇 | Pending | Enterprise Discovery | BP-KNOWLEDGE / BP-AI / BP-SMART-TERMINAL (candidates) | BOOK02 / BOOK04 (candidates) | TBD | Research Asset — not promoted | [ENTERPRISE_DISCOVERY_FRAMEWORK.md](programs/RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md) |
| NRI-RP-001-EVID | Enterprise Discovery Evidence Pack | 1.0 | Defined (Research) | NRI | Pending | Pending | Enterprise Discovery | BP-KNOWLEDGE / BP-AI / BP-SMART-TERMINAL (candidates) | BOOK02 / BOOK04 (candidates) | TBD | Research Library | [EVIDENCE_PACK.md](programs/RP-001-enterprise-discovery/EVIDENCE_PACK.md) |
| NRI-RP-001-DELIV | Enterprise Discovery Deliverables Checklist | 1.0 | Tracking | NRI | Pending | Pending | Enterprise Discovery | — | — | TBD | Research Library | [DELIVERABLES-RP-001.md](programs/RP-001-enterprise-discovery/DELIVERABLES-RP-001.md) |
| NRI-RP-001-WT-01 | Synthetic Walkthrough — Mid-Mfg | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise Discovery | — | — | TBD | Research Library | [WT-01](programs/RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md) |
| NRI-RP-001-WT-02 | Synthetic Walkthrough — Services | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise Discovery | — | — | TBD | Research Library | [WT-02](programs/RP-001-enterprise-discovery/walkthroughs/WT-02-services-synthetic.md) |
| NRI-RP-001-WT-03 | Synthetic Walkthrough — Stage Contrast | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise Discovery | — | — | TBD | Research Library | [WT-03](programs/RP-001-enterprise-discovery/walkthroughs/WT-03-stage-contrast-synthetic.md) |
| NRI-RP-001-IND | Enterprise Discovery Industry Analysis | 1.0 | Draft | NRI | Pending | Pending | Enterprise Discovery | BP-KNOWLEDGE / BP-AI (candidates) | BOOK02 / BOOK04 (candidates) | TBD | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-001-enterprise-discovery/INDUSTRY_ANALYSIS.md) |
| NRI-RP-001-RISK | Enterprise Discovery Risk Analysis | 1.0 | Draft | NRI | Pending | Pending | Enterprise Discovery | BP-KNOWLEDGE / BP-AI (candidates) | BOOK02 / BOOK03 / BOOK04 (candidates) | ADR-0030 / ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-001-enterprise-discovery/RISK_ANALYSIS.md) |
| NRI-RP-001-PEER | Enterprise Discovery Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Enterprise Discovery | — | — | TBD | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-001-enterprise-discovery/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-001 | Enterprise Discovery White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Enterprise Discovery | BP-KNOWLEDGE / BP-AI / BP-SMART-TERMINAL (candidates) | BOOK02 / BOOK04 (candidates) | ADR-0162 | Research Library | [WHITE_PAPER-RP-001.md](programs/RP-001-enterprise-discovery/WHITE_PAPER-RP-001.md) |
| NRI-ARC-RP-001 | Enterprise Discovery Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Enterprise Discovery | BP-KNOWLEDGE / BP-AI / BP-SMART-TERMINAL (candidates) | BOOK02 / BOOK04 (candidates) | ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md](programs/RP-001-enterprise-discovery/ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md) |
| NRI-RP-005-EVID | AI Workforce Evidence Pack | 1.0 | Defined (Research) | NRI | Pending | Pending | AI Workforce | BP-AI / BP-SMART-TERMINAL (candidates) | BOOK03 | ADR-0021 | Research Library | [EVIDENCE_PACK.md](programs/RP-005-ai-workforce-transformation/EVIDENCE_PACK.md) |
| NRI-RP-005-DELIV | AI Workforce Deliverables Checklist | 1.0 | Tracking | NRI | Pending | Pending | AI Workforce | — | — | TBD | Research Library | [DELIVERABLES-RP-005.md](programs/RP-005-ai-workforce-transformation/DELIVERABLES-RP-005.md) |
| NRI-RP-005-RI-01 | Role Inventory — Office Synthetic | 1.0 | Synthetic Complete | NRI | Pending | Pending | AI Workforce | — | BOOK03 | ADR-0021 | Research Library | [RI-01](programs/RP-005-ai-workforce-transformation/inventories/RI-01-office-synthetic.md) |
| NRI-RP-005-RI-02 | Role Inventory — Ops Synthetic | 1.0 | Synthetic Complete | NRI | Pending | Pending | AI Workforce | — | BOOK03 | ADR-0021 | Research Library | [RI-02](programs/RP-005-ai-workforce-transformation/inventories/RI-02-ops-synthetic.md) |
| NRI-RP-005-IND | AI Workforce Industry Analysis | 1.0 | Draft | NRI | Pending | Pending | AI Workforce | BP-AI (candidates) | BOOK03 | ADR-0021 | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-005-ai-workforce-transformation/INDUSTRY_ANALYSIS.md) |
| NRI-RP-005-RISK | AI Workforce Risk Analysis | 1.0 | Draft | NRI | Pending | Pending | AI Workforce | BP-AI (candidates) | BOOK03 | ADR-0021 / ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-005-ai-workforce-transformation/RISK_ANALYSIS.md) |
| NRI-RP-005-PEER | AI Workforce Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 包锦昱 | Pass | AI Workforce | — | BOOK03 | ADR-0021 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-005-ai-workforce-transformation/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-005 | AI-Native Role Framework White Paper | 0.1 | Accepted White Paper | NRI | 包锦昱 | Accepted | AI Workforce | BP-AI / BP-SMART-TERMINAL (candidates) | BOOK03 | ADR-0021 / ADR-0162 | Research Library | [WHITE_PAPER-RP-005.md](programs/RP-005-ai-workforce-transformation/WHITE_PAPER-RP-005.md) |
| NRI-ARC-RP-005 | AI Workforce Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | AI Workforce | BP-AI / BP-SMART-TERMINAL / BP-PACKAGE (candidates) | BOOK03 (constraint + candidate) | ADR-0021 / ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md](programs/RP-005-ai-workforce-transformation/ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md) |
| NRI-RP-002 | Enterprise DNA Program | 1.0 | Research | NRI | 臻宇 | Pending | Enterprise DNA | Twin/Brain candidates | BOOK02 candidate | TBD | Research Library | [programs/RP-002-enterprise-dna/](programs/RP-002-enterprise-dna/) |
| NRI-RP-002-EDNA | Enterprise DNA Model | 1.0 | Research Draft | NRI | 臻宇 | Pending | Enterprise DNA | Twin/Brain candidates | BOOK02 candidate | TBD | Research Asset — not promoted | [ENTERPRISE_DNA_MODEL.md](programs/RP-002-enterprise-dna/ENTERPRISE_DNA_MODEL.md) |
| NRI-RP-002-EVID | Enterprise DNA Evidence Pack | 1.0 | Defined (Research) | NRI | Pending | Pending | Enterprise DNA | — | — | TBD | Research Library | [EVIDENCE_PACK.md](programs/RP-002-enterprise-dna/EVIDENCE_PACK.md) |
| NRI-RP-002-DELIV | Enterprise DNA Deliverables Checklist | 1.0 | Tracking | NRI | Pending | Pending | Enterprise DNA | — | — | TBD | Research Library | [DELIVERABLES-RP-002.md](programs/RP-002-enterprise-dna/DELIVERABLES-RP-002.md) |
| NRI-RP-002-SC-01 | DNA Scorecard WT-01 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise DNA | — | — | TBD | Research Library | [SC-01](programs/RP-002-enterprise-dna/scorecards/SC-01-wt01-mfg.md) |
| NRI-RP-002-SC-02 | DNA Scorecard WT-02 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise DNA | — | — | TBD | Research Library | [SC-02](programs/RP-002-enterprise-dna/scorecards/SC-02-wt02-svc.md) |
| NRI-RP-002-SC-03 | DNA Scorecard WT-03 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise DNA | — | — | TBD | Research Library | [SC-03](programs/RP-002-enterprise-dna/scorecards/SC-03-wt03-contrast.md) |
| NRI-RP-002-IND | Enterprise DNA Industry Analysis | 1.0 | Draft | NRI | Pending | Pending | Enterprise DNA | Twin/Brain candidates | BOOK02 candidate | TBD | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-002-enterprise-dna/INDUSTRY_ANALYSIS.md) |
| NRI-RP-002-RISK | Enterprise DNA Risk Analysis | 1.0 | Draft | NRI | Pending | Pending | Enterprise DNA | Twin/Brain candidates | BOOK02 candidate | ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-002-enterprise-dna/RISK_ANALYSIS.md) |
| NRI-RP-002-PEER | Enterprise DNA Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Enterprise DNA | — | — | ADR-0162 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-002-enterprise-dna/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-002 | Enterprise DNA White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Enterprise DNA | Twin/Brain candidates | BOOK02 candidate | ADR-0162 | Research Library | [WHITE_PAPER-RP-002.md](programs/RP-002-enterprise-dna/WHITE_PAPER-RP-002.md) |
| NRI-ARC-RP-002 | Enterprise DNA Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Enterprise DNA | Twin/Brain (candidates) | BOOK02 (candidate) | ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md](programs/RP-002-enterprise-dna/ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md) |
| NRI-WAVE1-PEER-ASSIGN | Wave 1 Peer Assignment Instructions | 1.1 | All Pass — WP Draft Allowed | NRI | — | — | Governance | — | — | ADR-0162 | Research Library | [WAVE1_PEER_ASSIGNMENT.md](WAVE1_PEER_ASSIGNMENT.md) |
| NRI-WAVE2-PEER-ASSIGN | Wave 2 Peer Assignment Instructions | 1.8 | RP-002/003/004/009 Pass | NRI | — | — | Governance | — | — | ADR-0162 | Research Library | [WAVE2_PEER_ASSIGNMENT.md](WAVE2_PEER_ASSIGNMENT.md) |
| NRI-RP-003 | Capability First Program | 1.0 | Research | NRI | 臻宇 | Pending | Capability Model | BP-PACKAGE candidate | BOOK02 / BOOK08 candidates | TBD | Research Library | [programs/RP-003-capability-first/](programs/RP-003-capability-first/) |
| NRI-RP-003-CFM | Capability First Model | 1.0 | Research Draft | NRI | 臻宇 | Pending | Capability Model | BP-PACKAGE candidate | BOOK02 / BOOK08 candidates | TBD | Research Asset — not promoted | [CAPABILITY_FIRST_MODEL.md](programs/RP-003-capability-first/CAPABILITY_FIRST_MODEL.md) |
| NRI-RP-003-EVID | Capability First Evidence Pack | 1.0 | Defined (Research) | NRI | Pending | Pending | Capability Model | — | — | TBD | Research Library | [EVIDENCE_PACK.md](programs/RP-003-capability-first/EVIDENCE_PACK.md) |
| NRI-RP-003-DELIV | Capability First Deliverables Checklist | 1.0 | Tracking | NRI | Pending | Pending | Capability Model | — | — | TBD | Research Library | [DELIVERABLES-RP-003.md](programs/RP-003-capability-first/DELIVERABLES-RP-003.md) |
| NRI-RP-003-CG-01 | Capability Graph WT-01 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Capability Model | — | — | TBD | Research Library | [CG-01](programs/RP-003-capability-first/graphs/CG-01-wt01-mfg.md) |
| NRI-RP-003-CG-02 | Capability Graph WT-02 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Capability Model | — | — | TBD | Research Library | [CG-02](programs/RP-003-capability-first/graphs/CG-02-wt02-svc.md) |
| NRI-RP-003-IND | Capability First Industry Analysis | 1.0 | Draft | NRI | Pending | Pending | Capability Model | BP-PACKAGE candidate | BOOK02 / BOOK08 candidates | TBD | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-003-capability-first/INDUSTRY_ANALYSIS.md) |
| NRI-RP-003-RISK | Capability First Risk Analysis | 1.0 | Draft | NRI | Pending | Pending | Capability Model | BP-PACKAGE candidate | BOOK02 / BOOK08 candidates | ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-003-capability-first/RISK_ANALYSIS.md) |
| NRI-RP-003-PEER | Capability First Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Capability Model | — | — | ADR-0162 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-003-capability-first/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-003 | Capability First Model White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Capability Model | Package/Twin/Brain candidates | Cap/Org books | ADR-0162 | Research Library | [WHITE_PAPER-RP-003.md](programs/RP-003-capability-first/WHITE_PAPER-RP-003.md) |
| NRI-ARC-RP-003 | Capability First Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Capability Model | BP-PACKAGE / Twin/Brain (candidates) | BOOK02 / BOOK08 (candidates) | ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md](programs/RP-003-capability-first/ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md) |
| NRI-RP-004 | Organization Neutrality Program | 1.0 | Research | NRI | 臻宇 | Pending | Organization Models | Org-facing BP language | BOOK02 candidate | ADR-0019/0022 constraints | Research Library | [programs/RP-004-organization-neutrality/](programs/RP-004-organization-neutrality/) |
| NRI-RP-004-ONM | Organization Neutrality Model | 1.0 | Research Draft | NRI | 臻宇 | Pending | Organization Models | Org-facing BP language | BOOK02 candidate | ADR-0019/0022 | Research Asset — not promoted | [ORGANIZATION_NEUTRALITY_MODEL.md](programs/RP-004-organization-neutrality/ORGANIZATION_NEUTRALITY_MODEL.md) |
| NRI-RP-004-EVID | Organization Neutrality Evidence Pack | 1.0 | Defined (Research) | NRI | Pending | Pending | Organization Models | — | — | TBD | Research Library | [EVIDENCE_PACK.md](programs/RP-004-organization-neutrality/EVIDENCE_PACK.md) |
| NRI-RP-004-DELIV | Organization Neutrality Deliverables Checklist | 1.0 | Tracking | NRI | Pending | Pending | Organization Models | — | — | TBD | Research Library | [DELIVERABLES-RP-004.md](programs/RP-004-organization-neutrality/DELIVERABLES-RP-004.md) |
| NRI-RP-004-NA-01 | Neutrality Audit WT-01 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Organization Models | — | — | TBD | Research Library | [NA-01](programs/RP-004-organization-neutrality/audits/NA-01-wt01-mfg.md) |
| NRI-RP-004-NA-02 | Neutrality Audit WT-02 | 1.0 | Synthetic Complete | NRI | Pending | Pending | Organization Models | — | — | TBD | Research Library | [NA-02](programs/RP-004-organization-neutrality/audits/NA-02-wt02-svc.md) |
| NRI-RP-004-IND | Organization Neutrality Industry Analysis | 1.0 | Draft | NRI | Pending | Pending | Organization Models | Org-facing BP language | BOOK02 candidate | TBD | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-004-organization-neutrality/INDUSTRY_ANALYSIS.md) |
| NRI-RP-004-RISK | Organization Neutrality Risk Analysis | 1.0 | Draft | NRI | Pending | Pending | Organization Models | Org-facing BP language | BOOK02 candidate | ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-004-organization-neutrality/RISK_ANALYSIS.md) |
| NRI-RP-004-PEER | Organization Neutrality Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Organization Models | — | — | ADR-0162 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-004-organization-neutrality/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-004 | Organization Neutrality Model White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Organization Models | Org/Terminal/Package candidates | Org/Identity books | ADR-0019 / ADR-0022 / ADR-0162 | Research Library | [WHITE_PAPER-RP-004.md](programs/RP-004-organization-neutrality/WHITE_PAPER-RP-004.md) |
| NRI-ARC-RP-004 | Organization Neutrality Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Organization Models | Org/Terminal/Package (candidates) | BOOK02 (candidate) | ADR-0019 / ADR-0022 / ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md](programs/RP-004-organization-neutrality/ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md) |
| NRI-RP-005 | AI Workforce Transformation Program | 1.1 | Research | NRI | 包锦昱 | Pending | AI / Robot / Device Workforce | BP-AI / BP-SMART-TERMINAL (candidates) | BOOK03 (constraint + candidate) | ADR-0021 taxonomy constraint | Research Library | [programs/RP-005-ai-workforce-transformation/](programs/RP-005-ai-workforce-transformation/) |
| NRI-RP-005-ANRF | AI-Native Role Framework | 1.0 | Research Draft | NRI | 包锦昱 | Pending | AI-Native Roles | BP-AI candidate | BOOK03 | ADR-0021 | Research Asset — not promoted | [AI_NATIVE_ROLE_FRAMEWORK.md](programs/RP-005-ai-workforce-transformation/AI_NATIVE_ROLE_FRAMEWORK.md) |
| NRI-RP-006 | AI Infrastructure Platform Program | 1.0 | Research | NRI | 臻宇 | Pending | AI Infrastructure | BP-RUNTIME / BP-AI (candidates) | Security/AI governance books | ADR-0027 / ADR-0008 | Research Library | [programs/RP-006-ai-infrastructure-platform/](programs/RP-006-ai-infrastructure-platform/) |
| NRI-RP-006-AIRM | AI Infrastructure Reference Model | 1.0 | Research Draft | NRI | Pending | Pending | AI Infrastructure | BP-RUNTIME / BP-AI (candidates) | Security/AI governance books | ADR-0027 / ADR-0008 | Research Asset — not promoted | [AI_INFRASTRUCTURE_REFERENCE_MODEL.md](programs/RP-006-ai-infrastructure-platform/AI_INFRASTRUCTURE_REFERENCE_MODEL.md) |
| NRI-RP-006-EVID | AI Infrastructure Evidence Pack | 1.2 | Defined (Research) — Peer Pass; WP Draft open | NRI | 臻宇 | Pending | AI Infrastructure | — | — | ADR-0027 | Research Library | [EVIDENCE_PACK.md](programs/RP-006-ai-infrastructure-platform/EVIDENCE_PACK.md) |
| NRI-RP-006-DELIV | AI Infrastructure Deliverables Checklist | 1.2 | Tracking | NRI | 臻宇 | Pending | AI Infrastructure | — | — | TBD | Research Library | [DELIVERABLES-RP-006.md](programs/RP-006-ai-infrastructure-platform/DELIVERABLES-RP-006.md) |
| NRI-RP-006-GP-01 | Gap Profile GP-01 Cloud-Native | 1.0 | Synthetic Complete | NRI | Pending | Pending | AI Infrastructure | — | — | ADR-0027 | Research Library | [GP-01](programs/RP-006-ai-infrastructure-platform/gap-profiles/GP-01-cloud-native.md) |
| NRI-RP-006-GP-02 | Gap Profile GP-02 Hybrid OT | 1.0 | Synthetic Complete | NRI | Pending | Pending | AI Infrastructure | — | — | ADR-0027 | Research Library | [GP-02](programs/RP-006-ai-infrastructure-platform/gap-profiles/GP-02-hybrid-ot.md) |
| NRI-RP-006-IND | AI Infrastructure Industry Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | AI Infrastructure | BP-RUNTIME / BP-AI candidates | Security/AI books | ADR-0027 | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-006-ai-infrastructure-platform/INDUSTRY_ANALYSIS.md) |
| NRI-RP-006-RISK | AI Infrastructure Risk Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | AI Infrastructure | — | — | ADR-0027 / ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-006-ai-infrastructure-platform/RISK_ANALYSIS.md) |
| NRI-RP-006-PEER | AI Infrastructure Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | AI Infrastructure | — | — | ADR-0027 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-006-ai-infrastructure-platform/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-006 | AI Infrastructure Reference Model White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | AI Infrastructure | BP-RUNTIME / BP-AI (candidates) | Security/AI governance books | ADR-0027 / ADR-0162 | Research Library | [WHITE_PAPER-RP-006.md](programs/RP-006-ai-infrastructure-platform/WHITE_PAPER-RP-006.md) |
| NRI-ARC-RP-006 | AI Infrastructure Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | AI Infrastructure | BP-RUNTIME / BP-AI (candidates) | Security/AI governance books (candidates) | ADR-0027 / ADR-0008 / ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md](programs/RP-006-ai-infrastructure-platform/ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md) |
| NRI-WAVE3-PEER-ASSIGN | Wave 3 Peer Assignment Instructions | 1.5 | RP-006/008/010 Pass — WP Draft Allowed | NRI | — | — | Governance | — | — | ADR-0162 | Research Library | [WAVE3_PEER_ASSIGNMENT.md](WAVE3_PEER_ASSIGNMENT.md) |
| NRI-G1-PEER-GATE | Generation-1 Research Peer Gate Board | 1.0 | G1 models Research-complete; peer/WP gates closed | NRI | — | — | Governance | — | — | ADR-0162 | Research Library | [GENERATION1_PEER_GATE.md](GENERATION1_PEER_GATE.md) |
| NRI-G2-TIP | Generation-2 Research Tip Board | 1.0 | Active tip — optional deepenings after G1 complete | NRI | — | — | Governance | — | — | ADR-0162 | Research Library | [GENERATION2_TIP_BOARD.md](GENERATION2_TIP_BOARD.md) |
| NRI-AR-BOARD-QUEUE | Architecture Review Board Queue | 1.0 | Active standing queue — NRI-ARC-RP-001…010 Board Decision — Hold（PHX-G159） | NRI | — | — | Governance | — | — | ADR-0162 / ADR-0169 / ADR-0171 | Research Library | [ARCHITECTURE_REVIEW_BOARD_QUEUE.md](ARCHITECTURE_REVIEW_BOARD_QUEUE.md) |
| NRI-T2-T3-EVID | T2 / T3 Evidence Readiness Board | 1.1 | Active readiness — all RP-001…010 floors T1；0 live T2/T3 Complete；intake companion G163 | NRI | — | — | Governance | — | — | ADR-0162 / ADR-0169 / ADR-0174 / ADR-0180 | Research Library | [T2_T3_EVIDENCE_READINESS.md](T2_T3_EVIDENCE_READINESS.md) |
| NRI-T2-T3-INTAKE | T2 / T3 Evidence Intake & Live Capture Board | 1.0 | Active intake — 0 Complete；T2 vs T3 bars；checklist + template（PHX-G163） | NRI | — | — | Governance | — | — | ADR-0162 / ADR-0169 / ADR-0174 / ADR-0180 | Research Library | [T2_T3_EVIDENCE_INTAKE.md](T2_T3_EVIDENCE_INTAKE.md) |
| NRI-TPL-LIVE-EVID | Live Evidence Capture Template | 1.0 | Template — copy per live capture；not itself Complete | NRI | — | — | Governance | — | — | ADR-0180 | Research Library | [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) |
| NRI-RP-007 | Enterprise Evolution Engine Program | 1.1 | Research | NRI | 牟蓉 | Pending | Enterprise Evolution | Brain/Twin/AI/Terminal candidates | Twin/AI/workforce books | ADR-0030 Brain constraint | Research Library | [programs/RP-007-enterprise-evolution-engine/](programs/RP-007-enterprise-evolution-engine/) |
| NRI-RP-007-EEM | Enterprise Evolution Model | 1.0 | Research Draft | NRI | 牟蓉 | Pending | Evolution Recommendations | Brain/Twin candidates | Advisory invariants | ADR-0030 | Research Asset — not promoted | [ENTERPRISE_EVOLUTION_MODEL.md](programs/RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md) |
| NRI-RP-007-EVID | Evolution Engine Evidence Pack | 1.0 | Defined (Research) | NRI | Pending | Pending | Enterprise Evolution | Brain/Twin candidates | Advisory invariants | ADR-0030 / ADR-0162 | Research Library | [EVIDENCE_PACK.md](programs/RP-007-enterprise-evolution-engine/EVIDENCE_PACK.md) |
| NRI-RP-007-DELIV | Evolution Engine Deliverables Checklist | 1.0 | Tracking | NRI | Pending | Pending | Enterprise Evolution | — | — | TBD | Research Library | [DELIVERABLES-RP-007.md](programs/RP-007-enterprise-evolution-engine/DELIVERABLES-RP-007.md) |
| NRI-RP-007-IFRZ | Wave 1 Input Freeze | 1.0 | Frozen for Synthetic Tests | NRI | Pending | Pending | Enterprise Evolution | — | — | TBD | Research Library | [INPUT_FREEZE.md](programs/RP-007-enterprise-evolution-engine/INPUT_FREEZE.md) |
| NRI-RP-007-TT-01 | Trigger Test — HOLD Low Potential | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise Evolution | — | — | ADR-0030 | Research Library | [TT-01](programs/RP-007-enterprise-evolution-engine/trigger-tests/TT-01-hold-low-potential.md) |
| NRI-RP-007-TT-02 | Trigger Test — Assist Not Agentize | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise Evolution | — | — | ADR-0030 | Research Library | [TT-02](programs/RP-007-enterprise-evolution-engine/trigger-tests/TT-02-assist-not-agentize.md) |
| NRI-RP-007-TT-03 | Trigger Test — Robot Safety HOLD | 1.0 | Synthetic Complete | NRI | Pending | Pending | Enterprise Evolution | — | — | ADR-0030 | Research Library | [TT-03](programs/RP-007-enterprise-evolution-engine/trigger-tests/TT-03-robot-hold-safety.md) |
| NRI-RP-007-PEER | Evolution Engine Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 牟蓉 | Pass | Enterprise Evolution | — | — | ADR-0030 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-007-enterprise-evolution-engine/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-007 | Enterprise Evolution Model White Paper | 0.1 | Accepted White Paper | NRI | 牟蓉 | Accepted | Enterprise Evolution | Brain/Twin/AI/Terminal (candidates) | Advisory invariants | ADR-0030 / ADR-0162 | Research Library | [WHITE_PAPER-RP-007.md](programs/RP-007-enterprise-evolution-engine/WHITE_PAPER-RP-007.md) |
| NRI-ARC-RP-007 | Enterprise Evolution Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Enterprise Evolution | Brain/Twin/AI/Terminal (candidates) | Twin/AI/workforce books (candidates) | ADR-0030 / ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-007.md](programs/RP-007-enterprise-evolution-engine/ARCHITECTURE_REVIEW_CANDIDATE-RP-007.md) |
| NRI-RP-008 | Smart Factory Program | 1.0 | Research | NRI | 臻宇 | Pending | Industry / Smart Factory | Package/Terminal/Event candidates | Industry/safety books | ADR-0030 / ADR-0027 | Research Library | [programs/RP-008-smart-factory/](programs/RP-008-smart-factory/) |
| NRI-RP-008-SFSM | Smart Factory Specialization Model | 1.0 | Research Draft | NRI | Pending | Pending | Industry / Smart Factory | Package/Terminal/Event candidates | Industry/safety books | ADR-0030 / ADR-0027 | Research Asset — not promoted | [SMART_FACTORY_SPECIALIZATION_MODEL.md](programs/RP-008-smart-factory/SMART_FACTORY_SPECIALIZATION_MODEL.md) |
| NRI-RP-008-EVID | Smart Factory Evidence Pack | 1.2 | Defined (Research) — Peer Pass; WP Draft open | NRI | 臻宇 | Accepted | Industry / Smart Factory | — | — | ADR-0030 | Research Library | [EVIDENCE_PACK.md](programs/RP-008-smart-factory/EVIDENCE_PACK.md) |
| NRI-RP-008-DELIV | Smart Factory Deliverables Checklist | 1.2 | Tracking | NRI | 臻宇 | Pending | Industry / Smart Factory | — | — | TBD | Research Library | [DELIVERABLES-RP-008.md](programs/RP-008-smart-factory/DELIVERABLES-RP-008.md) |
| NRI-RP-008-PW-01 | Plant Overlay PW-01 Discrete Cell | 1.0 | Synthetic Complete | NRI | Pending | Pending | Industry / Smart Factory | — | — | ADR-0030 | Research Library | [PW-01](programs/RP-008-smart-factory/walkthroughs/PW-01-discrete-cell.md) |
| NRI-RP-008-PW-02 | Plant Overlay PW-02 Line Terminal OT | 1.0 | Synthetic Complete | NRI | Pending | Pending | Industry / Smart Factory | — | — | ADR-0030 | Research Library | [PW-02](programs/RP-008-smart-factory/walkthroughs/PW-02-line-terminal-ot.md) |
| NRI-RP-008-IND | Smart Factory Industry Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | Industry / Smart Factory | Package/Terminal candidates | Industry/safety books | ADR-0030 | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-008-smart-factory/INDUSTRY_ANALYSIS.md) |
| NRI-RP-008-RISK | Smart Factory Risk Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | Industry / Smart Factory | — | — | ADR-0030 / ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-008-smart-factory/RISK_ANALYSIS.md) |
| NRI-RP-008-PEER | Smart Factory Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Industry / Smart Factory | — | — | ADR-0030 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-008-smart-factory/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-008 | Smart Factory Specialization Model White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Industry / Smart Factory | Package/Terminal/Event candidates | Industry/safety books | ADR-0030 / ADR-0162 | Research Library | [WHITE_PAPER-RP-008.md](programs/RP-008-smart-factory/WHITE_PAPER-RP-008.md) |
| NRI-ARC-RP-008 | Smart Factory Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Industry / Smart Factory | Package/Terminal/Event (candidates) | Industry/safety books (candidates) | ADR-0030 / ADR-0027 / ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md](programs/RP-008-smart-factory/ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md) |
| NRI-RP-009 | Enterprise Brain Evolution Program | 1.0 | Research | NRI | 臻宇 | Pending | Enterprise Brain | Brain/Twin/AI candidates | Twin/Brain books | ADR-0030 | Research Library | [programs/RP-009-enterprise-brain-evolution/](programs/RP-009-enterprise-brain-evolution/) |
| NRI-RP-009-BEM | Brain Evolution Model | 1.0 | Research Draft | NRI | 臻宇 | Pending | Enterprise Brain | Brain/Twin/AI candidates | Twin/Brain books | ADR-0030 | Research Asset — not promoted | [BRAIN_EVOLUTION_MODEL.md](programs/RP-009-enterprise-brain-evolution/BRAIN_EVOLUTION_MODEL.md) |
| NRI-RP-009-EVID | Brain Evolution Evidence Pack | 1.2 | Defined (Research) — AE complete; Peer Assigned | NRI | 臻宇 | Pending | Enterprise Brain | — | — | ADR-0030 | Research Library | [EVIDENCE_PACK.md](programs/RP-009-enterprise-brain-evolution/EVIDENCE_PACK.md) |
| NRI-RP-009-DELIV | Brain Evolution Deliverables Checklist | 1.1 | Tracking | NRI | Pending | Pending | Enterprise Brain | — | — | TBD | Research Library | [DELIVERABLES-RP-009.md](programs/RP-009-enterprise-brain-evolution/DELIVERABLES-RP-009.md) |
| NRI-RP-009-AE-01 | Anti-Execution AE-01 Quiet Analytics Trigger | 1.0 | Synthetic Complete | NRI | 臻宇 | Pending | Enterprise Brain | — | — | ADR-0030 | Research Library | [AE-01](programs/RP-009-enterprise-brain-evolution/red-team/AE-01-quiet-analytics-trigger.md) |
| NRI-RP-009-AE-02 | Anti-Execution AE-02 Accept-on-Behalf | 1.0 | Synthetic Complete | NRI | 臻宇 | Pending | Enterprise Brain | — | — | ADR-0030 | Research Library | [AE-02](programs/RP-009-enterprise-brain-evolution/red-team/AE-02-accept-on-behalf.md) |
| NRI-RP-009-AE-03 | Anti-Execution AE-03 Twin Authorize Leak | 1.0 | Synthetic Complete | NRI | 臻宇 | Pending | Enterprise Brain | — | — | ADR-0030 | Research Library | [AE-03](programs/RP-009-enterprise-brain-evolution/red-team/AE-03-twin-authorize-leak.md) |
| NRI-RP-009-IND | Brain Evolution Industry Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | Enterprise Brain | Brain/Twin/AI candidates | Twin/Brain books | ADR-0030 | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-009-enterprise-brain-evolution/INDUSTRY_ANALYSIS.md) |
| NRI-RP-009-RISK | Brain Evolution Risk Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | Enterprise Brain | — | — | ADR-0030 / ADR-0162 | Research Library | [RISK_ANALYSIS.md](programs/RP-009-enterprise-brain-evolution/RISK_ANALYSIS.md) |
| NRI-RP-009-PEER | Brain Evolution Peer Review Package | 1.1 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Enterprise Brain | — | — | ADR-0030 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-009-enterprise-brain-evolution/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-009 | Brain Evolution Model White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Enterprise Brain | Brain/Twin/AI candidates | Twin/Brain books | ADR-0030 / ADR-0162 | Research Library | [WHITE_PAPER-RP-009.md](programs/RP-009-enterprise-brain-evolution/WHITE_PAPER-RP-009.md) |
| NRI-ARC-RP-009 | Brain Evolution Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Enterprise Brain | Brain/Twin/AI (candidates) | Twin/Brain books (candidates) | ADR-0030 / ADR-0162 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-009.md](programs/RP-009-enterprise-brain-evolution/ARCHITECTURE_REVIEW_CANDIDATE-RP-009.md) |
| NRI-RP-010 | Future Enterprise Operating Model Program | 1.0 | Research | NRI | 臻宇 | Pending | Future EOM | Cross-blueprint | Multi-BOOK synthesis | ADR-0162 / ADR-0030 | Research Library | [programs/RP-010-future-enterprise-operating-model/](programs/RP-010-future-enterprise-operating-model/) |
| NRI-RP-010-FEOM | Future Enterprise Operating Model | 1.0 | Research Draft | NRI | 臻宇 | Pending | Future EOM | Cross-blueprint | Multi-BOOK synthesis | ADR-0162 / ADR-0030 | Research Asset — not promoted | [FUTURE_ENTERPRISE_OPERATING_MODEL.md](programs/RP-010-future-enterprise-operating-model/FUTURE_ENTERPRISE_OPERATING_MODEL.md) |
| NRI-RP-010-EVID | Future EOM Evidence Pack | 1.2 | Defined (Research) — Peer Pass; WP Accepted | NRI | 臻宇 | Accepted | Future EOM | — | — | ADR-0162 | Research Library | [EVIDENCE_PACK.md](programs/RP-010-future-enterprise-operating-model/EVIDENCE_PACK.md) |
| NRI-RP-010-DELIV | Future EOM Deliverables Checklist | 1.2 | Tracking | NRI | 臻宇 | Pending | Future EOM | — | — | TBD | Research Library | [DELIVERABLES-RP-010.md](programs/RP-010-future-enterprise-operating-model/DELIVERABLES-RP-010.md) |
| NRI-RP-010-SA-01 | Synthesis Audit SA-01 Executive Narrative | 1.0 | Synthetic Complete | NRI | 臻宇 | Pending | Future EOM | — | — | ADR-0162 | Research Library | [SA-01](programs/RP-010-future-enterprise-operating-model/audits/SA-01-executive-narrative.md) |
| NRI-RP-010-SA-02 | Synthesis Audit SA-02 Plant/Services Contrast | 1.0 | Synthetic Complete | NRI | 臻宇 | Pending | Future EOM | — | — | ADR-0162 | Research Library | [SA-02](programs/RP-010-future-enterprise-operating-model/audits/SA-02-plant-services-contrast.md) |
| NRI-RP-010-IND | Future EOM Industry Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | Future EOM | Cross-blueprint | Multi-BOOK candidates | ADR-0162 | Research Library | [INDUSTRY_ANALYSIS.md](programs/RP-010-future-enterprise-operating-model/INDUSTRY_ANALYSIS.md) |
| NRI-RP-010-RISK | Future EOM Risk Analysis | 1.0 | Draft | NRI | 臻宇 | Pending | Future EOM | — | — | ADR-0162 / ADR-0030 | Research Library | [RISK_ANALYSIS.md](programs/RP-010-future-enterprise-operating-model/RISK_ANALYSIS.md) |
| NRI-RP-010-PEER | Future EOM Peer Review Package | 1.2 | Pass — WP Draft Allowed | NRI | 臻宇 | Pass | Future EOM | — | — | ADR-0162 | Research Library | [PEER_REVIEW_PACKAGE.md](programs/RP-010-future-enterprise-operating-model/PEER_REVIEW_PACKAGE.md) |
| NRI-WP-RP-010 | Future Enterprise Operating Model White Paper | 0.1 | Accepted White Paper | NRI | 臻宇 | Accepted | Future EOM | Cross-blueprint *(candidates)* | Multi-BOOK synthesis *(candidates)* | ADR-0162 / ADR-0030 / ADR-0027 | Research Library | [WHITE_PAPER-RP-010.md](programs/RP-010-future-enterprise-operating-model/WHITE_PAPER-RP-010.md) |
| NRI-ARC-RP-010 | Future EOM Architecture Review Candidate | 0.1 | Board Decision — Hold（PHX-G159 / DAL-G005） | NRI | — | — | Future EOM | Cross-blueprint (candidates) | Multi-BOOK synthesis (candidates) | ADR-0162 / ADR-0030 / ADR-0169 | Research Library | [ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md](programs/RP-010-future-enterprise-operating-model/ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md) |

## Deliverable Completeness (Program Level)

| Program | Research Report | Industry | Trends | Cap Map | Cap Maturity | Ent Maturity | AI Maturity | Arch Impact | BP Impact | Const Impact | Migration | Validation | Pilot | ROI | Risk | Long-term Evo |
|---------|-----------------|----------|--------|---------|--------------|--------------|-------------|-------------|-----------|--------------|-----------|------------|-------|-----|------|---------------|
| RP-001 | Draft (EDF) | Draft (IND) | Draft | Partial | Planned | Partial (Growth Stage) | Partial (AI Readiness) | Draft | Draft | Draft | Draft | Draft (Evidence Pack) | Planned | Planned | Draft (RISK) | Draft |
| RP-005 | Partial (ANRF) | Partial | Yes | Partial | Planned | Planned | Partial | Yes | Yes | Yes | Planned | Yes | Yes | Planned | Yes | Planned |
| RP-007 | Partial (EEM) | Partial | Yes | Via inputs | Planned | Via stage | Via readiness | Yes | Yes | Yes | Planned | Yes | Yes | Planned | Yes | Yes |
| RP-002 | Draft (EDNA) | Draft (IND) | Draft | Partial | Planned | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack) | Planned | Planned | Draft (RISK) | Draft |
| RP-003 | Draft (CFM) | Draft (IND) | Draft | Draft (CG-01…02) | Draft (L0–L4) | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack) | Planned | Planned | Draft (RISK) | Draft |
| RP-004 | Draft (ONM) | Draft (IND) | Draft | Draft (constraint) | Planned | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack) | Planned | Planned | Draft (RISK) | Draft |
| RP-009 | Draft (BEM) | Draft (IND) | Draft | Draft (advisory) | Planned | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack + AE) | Planned | Planned | Draft (RISK) | Draft |
| RP-006 | Draft (AIRM) | Draft (IND) | Draft | Draft (ID-01…08) | Draft (I0–I4) | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack + GP) | Planned | Planned | Draft (RISK) | Draft |
| RP-008 | Draft (SFSM) | Draft (IND) | Draft | Draft (SF-01…08) | Draft (PR0–PR4) | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack + PW) | Planned | Planned | Draft (RISK) | Draft |
| RP-010 | Draft (FEOM) | Draft (IND) | Draft | Draft (ES-01…07) | Draft (E0–E4) | Planned | Planned | Draft | Draft | Draft | Draft | Draft (Evidence Pack + SA) | Planned | Planned | Draft (RISK) | Draft |

`Planned` = required by Charter; must exist before White Paper freeze unless waived.

## Change Log

| Date | Change |
|------|--------|
| 2026-07-21 | RP-006/008/010 Architecture Review Candidates registered（NRI-ARC-RP-006/008/010；DAL-U020/U021/U022）；Wave 3 AR set complete |
| 2026-07-21 | T2/T3 Evidence Readiness Board registered（NRI-T2-T3-EVID；PHX-G155 / DAL-U027） |
| 2026-07-21 | Architecture Review Board Queue registered（NRI-AR-BOARD-QUEUE；PHX-G152 / DAL-U024） |
| 2026-07-21 | RP-004 Architecture Review Candidate registered（NRI-ARC-RP-004；DAL-U019） |
| 2026-07-21 | RP-003 Architecture Review Candidate registered（NRI-ARC-RP-003；DAL-U018） |
| 2026-07-21 | RP-009 Architecture Review Candidate registered（NRI-ARC-RP-009；DAL-U017） |
| 2026-07-21 | RP-002 Architecture Review Candidate registered（NRI-ARC-RP-002；DAL-U016）；Wave 2 AR set start |
| 2026-07-21 | RP-005 Architecture Review Candidate registered（NRI-ARC-RP-005；DAL-U015）；Wave 1 AR set complete |
| 2026-07-21 | RP-007 Architecture Review Candidate registered（NRI-ARC-RP-007；DAL-U014） |
| 2026-07-21 | RP-001 Architecture Review Candidate registered（NRI-ARC-RP-001；DAL-U013） |
| 2026-07-21 | Generation-2 Research Tip Board registered（NRI-G2-TIP；DAL-U011） |
| 2026-07-21 | RP-008 peer Pass (臻宇); NRI-WP-RP-008 Accepted（DAL-G003） |
| 2026-07-21 | RP-010 peer Pass (臻宇); NRI-WP-RP-010 Accepted（DAL-G003） |
| 2026-07-21 | WP-RP-001…007 / 009 content Accepted under CA delegation (2026-07-21…22) |
| 2026-07-21 | RP-006 peer Pass (臻宇); WP-RP-006 Draft registered |
| 2026-07-21 | Generation-1 Peer Gate Board registered |
| 2026-07-21 | RP-010 SA-01…02 + IND/RISK + PEER ready registered |
| 2026-07-21 | RP-010 FEOM Research Draft + Evidence Pack registered (Wave 3 early) |
| 2026-07-21 | RP-008 PW-01…02 + IND/RISK + PEER ready registered |
| 2026-07-21 | RP-008 SFSM Research Draft + Evidence Pack registered (Wave 3 early) |
| 2026-07-21 | RP-006 peer assigned: 臻宇 (decision Pending) |
| 2026-07-21 | RP-009 peer Pass (臻宇); WP-RP-009 Draft registered |
| 2026-07-21 | RP-006 GP-01…02 + IND/RISK + PEER + WAVE3 ledger registered |
| 2026-07-21 | RP-006 AIRM Research Draft + Evidence Pack registered (Wave 3 early) |
| 2026-07-21 | RP-009 AE-01…03 + IND/RISK + PEER Assigned 臻宇 registered |
| 2026-07-21 | RP-003/004 peer Pass (臻宇); WP-RP-003/004 Draft registered |
| 2026-07-21 | RP-003/004 peers + RP-009 designated: 臻宇 |
| 2026-07-21 | RP-009 Brain Evolution Model Research Draft + Evidence Pack registered |
| 2026-07-21 | RP-004 Industry/Risk Draft + Peer Review Package registered |
| 2026-07-21 | RP-004 NA-01…02 synthetic neutrality audits registered |
| 2026-07-21 | RP-004 Organization Neutrality Model Research Draft + Evidence Pack registered |
| 2026-07-21 | RP-003 Industry/Risk Draft + Peer Review Package registered |
| 2026-07-21 | RP-003 CG-01…02 synthetic capability graphs registered |
| 2026-07-21 | RP-002 peer Pass (臻宇); WHITE_PAPER-RP-002 Draft registered |
| 2026-07-21 | RP-002 peer assigned: 臻宇 (decision Pending) |
| 2026-07-21 | Wave 1 peers Pass; WP-RP-001/005/007 Drafts registered |
| 2026-07-21 | RP-003 Capability First Model Research Draft + Evidence Pack registered |
| 2026-07-21 | RP-002 Peer Review Package + WAVE2_PEER_ASSIGNMENT registered |
| 2026-07-21 | RP-002 Industry Analysis + Risk Analysis registered as Draft |
| 2026-07-21 | RP-001 peer 臻宇 + RP-007 peer 牟蓉 assigned; Wave 1 peers complete |
| 2026-07-21 | RP-005 peer assigned: 包锦昱 (legal 优先); decision Pending |
| 2026-07-21 | RP-002 SC-01…03 scorecards + WAVE1_PEER_ASSIGNMENT (reject `<name>` placeholders) |
| 2026-07-21 | RP-002 Enterprise DNA Model Research Draft + Evidence Pack registered |
| 2026-07-21 | RP-005 IND/RISK/PEER + RP-007 PEER registered |
| 2026-07-21 | RP-007 Evidence Pack, Input Freeze, TT-01…03 registered |
| 2026-07-21 | RP-005 RI-01…02 synthetic role inventories registered |
| 2026-07-21 | RP-001 Peer Review Package + RP-005 Evidence Pack / Deliverables registered |
| 2026-07-21 | RP-001 Industry Analysis + Risk Analysis registered as Draft |
| 2026-07-21 | RP-001 WT-01…03 synthetic walkthroughs registered |
| 2026-07-21 | RP-001 Evidence Pack + Deliverables Checklist registered (NRI-RP-001-EVID / DELIV) |
| 2026-07-20 | Research Library established under Governance Charter v1.0 |
