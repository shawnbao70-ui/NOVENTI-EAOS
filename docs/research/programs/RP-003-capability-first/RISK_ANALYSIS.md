# RISK-ANALYSIS-RP-003 — Capability First

**Research ID:** NRI-RP-003-RISK  
**Program:** RP-003  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register Cap≠Org collapse, grant leakage, adoption, and architectural risks for Capability First before any White Paper path  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** 臻宇（PEER Assigned — decision Pending）  
**Approval:** Pending  
**Dependencies:** CFM §7; Evidence Pack; CG-01…02  
**Related ADR:** ADR-0162 Dual-Track  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) Cap≠Org collapses under workshop time pressure, (b) capability IDs leak into Permission/grants, (c) affinity bands used to auto-open Eng/Runtime paths, (d) Marketplace outcome claims without evidence tiers.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-CAP-01 | Method | Cap≠Org collapses; dept names become Cap IDs | H | High | Mandatory checklist; CG-01/02 method | Med |
| R-CAP-02 | Architectural | Capability becomes Permission/Twin input | M | Crit | `auto_grant_minted: never`; Dual-Track | Low |
| R-CAP-03 | Integrity | Synthetic graphs over-claimed as T3 live | M | High | Tier labels; live workshops planned | Low if honest |
| R-CAP-04 | Method | Flat list used; edges ignored in decisions | M | Med | Critical-path section required | Med |
| R-CAP-05 | Adoption | Affinity maximalism (“automate everything”) | H | High | A0 holds; V-CAP-03 | Med |
| R-CAP-06 | Downstream | RP-005 mints roles from org boxes via Cap labels | M | High | Cap≠title; ANRF constraints | Med |
| R-CAP-07 | Downstream | RP-007 Agentize despite A0 critical nodes | M | High | Export hints; TT linkage | Med |
| R-CAP-08 | Commercial | Marketplace Cap packs sold pre-validation | L | Med | Library-only until promote | Low |
| R-CAP-09 | Privacy | Graph workshops expose sensitive politics | M | High | Redaction; facilitator rules | Med |
| R-CAP-10 | Governance | Eng soft-queue Cap registry schema premature | L | Crit | No Eng ingest without Promote | Low |
| R-CAP-11 | Safety | A3 robot affinity without RC5 case | M | Crit | Affinity advisory; TT-03 | Med |
| R-CAP-12 | Const/BP | Silent BOOK Cap obligations | L | High | Promotion Rules only | Low |
| R-CAP-13 | Brain | Cap gaps used to justify execute | L | Crit | Fail-closed; advisory only | Low |
| R-CAP-14 | Org | CFM sold as reorg authority | M | High | Ownership = role class; RP-004 | Med |

## 3. Falsifier ↔ Risk Map

| CFM Falsifier | Risks | Hold |
|---------------|-------|------|
| Cannot name Cap without org language | R-CAP-01 | Hold C-CAP-02 |
| Graph adds no decision value | R-CAP-04 | Hold C-CAP-01/04 |
| Affinity opens Eng/Runtime | R-CAP-02/05/10 | Refuse productize path |
| Marketplace claims without tiers | R-CAP-08 | Hold commercial claims |
| Sold as HR/org redesign authority | R-CAP-14 | Refuse WP Acceptance |

## 4. WP Hold Triggers

1. Any artifact proposes Cap→grant/authorize.  
2. Cap≠Org checklist fails or skipped.  
3. Affinity presented as execution authority.  
4. Evidence tiers mislabeled (synthetic as T3).

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Twin authorize / Brain execute / Role→grant.

## Related Documents

- [CFM](CAPABILITY_FIRST_MODEL.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [RP-001 Risk Analysis](../RP-001-enterprise-discovery/RISK_ANALYSIS.md)  
