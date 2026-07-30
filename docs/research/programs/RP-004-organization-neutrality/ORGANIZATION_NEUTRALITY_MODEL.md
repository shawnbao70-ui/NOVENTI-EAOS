# Organization Neutrality Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-004-ONM  
**Program:** RP-004 Organization Neutrality  
**Version:** 1.0  
**Status:** Research Draft  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Constrains:** RP-001 / RP-003 / RP-005 / RP-007 / RP-010 language & advice templates  
**Related ADR (read-only):** ADR-0019; ADR-0022  
**Consumers:** Discovery facilitators; package authors; Evolution advice templates

---

## Abstract

The Organization Neutrality Model (ONM) ensures EAOS research and future enterprise-facing designs do **not** hard-code a single organizational ideology (e.g., classic manager hierarchy as the only truth). Organization is structure and decision-rights placement; it is never Capability, never Permission, and never a mandatory maturity ladder that punishes dual-control, matrix, multi-entity, council, or shop-floor forms. ONM is a **constraint thesis**: it gates language and advice templates; it does not redesign Kernel Organization schemas in this Research Draft.

## 1. Design Principles

1. **Pluralism** — multiple org forms are first-class; none is “immature” by default.  
2. **Structure ≠ Capability** — aligns with Cap≠Org (RP-001/003).  
3. **Structure ≠ Permission** — membership/unit shape never mints grants.  
4. **Decision-rights first** — advice templates parameterize by rights placement, not title metaphors.  
5. **Reorg resilience** — configs and advice must survive reshuffles without ideology lock-in.  
6. **Language audits** — “manager approves,” “report-to,” “dept head” as sole UX are defects unless parameterized.  
7. **Falsifiable** — forced-assumption defects in multi-form cases Hold claims.  
8. **Dual-Track safe** — research constraint until promoted.

## 2. Org Form Catalog (Research)

| Form ID | Name | Decision-rights sketch | Neutrality stress |
|---------|------|------------------------|-------------------|
| OF-01 | Classic hierarchy | Line manager gravity | Default bias risk |
| OF-02 | Matrix | Dual solid/dotted rights | Dual-approver UX |
| OF-03 | Multi-entity / federation | Entity-local + group policies | Tenant/Enterprise bands |
| OF-04 | Council / committee | Collective approval | Non-manager metaphors |
| OF-05 | Shop-floor / cell | Local exception rights | Plant≠HQ IT |
| OF-06 | Partnership / practice | Partner exceptions | Services WT-02 |
| OF-07 | Platform / product org | Product owners vs shared services | Capability ownership |

**Rule:** Research instruments and REC-* templates must declare which forms they were validated against; claiming universality without OF contrast is a defect.

## 3. Neutrality Checklist (Gate Construct)

| ID | Check | Fail means |
|----|-------|------------|
| N-01 | Advice works without assuming single manager approver | Hierarchy chauvinism |
| N-02 | Capability ownership uses role class, not dept name | Cap≠Org collapse |
| N-03 | No “Level N org = mature” ladder punishing OF-02…07 | Maturity theater |
| N-04 | Multi-entity cases have separate decision-rights maps | Federation blindness |
| N-05 | Terminal/UX copy offers non-manager metaphors | UX lock-in |
| N-06 | Packages declare org assumptions if any | Hidden dogma |
| N-07 | Permission/grants never derived from org chart shape | Authz leakage |
| N-08 | Reorg simulation does not require Cap ID renames | Brittleness |

## 4. Constraint Surface on Downstream RPs

| Program | ONM constraint |
|---------|----------------|
| RP-001 | Org domain descriptive; Cap workshop without org labels |
| RP-003 | owner_role_class; org_anchors descriptive only |
| RP-005 | Title ≠ grant; practice/plant boxes ≠ Cap |
| RP-007 | REC templates parameterized by decision-rights, not “ask your manager” only |
| RP-010 | Future EOM must keep pluralism |

## 5. Validation Constructs

| ID | Construct |
|----|-----------|
| V-ON-01 | ≥2 org forms yield usable dossiers with same Cap instruments |
| V-ON-02 | Neutrality checklist N-01…08 executable in desk review |
| V-ON-03 | No Permission mint from org shape in any artifact |
| V-ON-04 | Forced-assumption defects countable and remediable |
| V-ON-05 | Falsifiers include hierarchy-as-maturity and manager-only UX |

## 6. Falsifiers

1. Instruments cannot run on matrix/council without rewriting Cap IDs.  
2. Evolution advice always says “ask your manager” with no alternate rights path.  
3. Maturity models score OF-02…07 as immature by definition.  
4. Org chart shape proposed as grant source.  
5. Marketplace packages hide mandatory hierarchy assumptions.

## 7. Cross-Layer Impact (Potential)

| Layer | Impact |
|-------|--------|
| Kernel Organization | Reinforces structure≠permission (read-only alignment) |
| Permission | No shape→grant |
| Smart Terminal | Plural approval metaphors |
| Brain / Twin | Parameterized advice templates — advisory |
| Marketplace | Org-assumption declarations |
| Constitution / Blueprint | BOOK02 pluralism candidates only |

## 8. Promotion Stance

Current: **Research Draft v1.0**  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Audits: **NA-01…02 Synthetic Complete** — [audits/](audits/)  
Industry/Risk: **Draft** — [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
Peer package: [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) — Assigned: **臻宇**（decision Pending）.  
Next: Pass → White Paper path.  
May later promote as constraint White Paper without prototype if multi-case evidence sufficient. Remain Asset OK.

## Related Documents

- [RP-004 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables](DELIVERABLES-RP-004.md)  
- [Neutrality Audits](audits/README.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Risk Analysis](RISK_ANALYSIS.md)  
- [Peer Review Package](PEER_REVIEW_PACKAGE.md)  
- [EDF](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [CFM](../RP-003-capability-first/CAPABILITY_FIRST_MODEL.md)  
