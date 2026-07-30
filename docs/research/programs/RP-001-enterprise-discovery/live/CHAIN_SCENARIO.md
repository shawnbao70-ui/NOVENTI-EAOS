# RP-001 Commercial Chain Scenario

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Live chain/observer assigned:** none / none  
**Protocol:** [COMMERCIAL_CHAIN_OBSERVATION](../../../templates/COMMERCIAL_CHAIN_OBSERVATION.md) · **Terminal lens:** [TERMINAL_SCENARIO_CARD](../../../templates/TERMINAL_SCENARIO_CARD.md)

## Research purpose

Use an existing sample → quote → order → shipment → payment chain to test whether Discovery captures enterprise truth across commercial, operational, knowledge, organization, capability, automation, and infrastructure domains.

## Chain observation points

1. **Sample:** source/request channel, product/specification knowledge, ownership, and evidence generated.
2. **Quote:** customer/product inputs, pricing/terms approvals, versioning, and expired/rejected states.
3. **Order:** quote linkage, acceptance, compliance/credit checks, duplicate/change/cancel controls.
4. **Shipment:** inventory/fulfillment/logistics handoffs, safety/trade checks, and exception states.
5. **Receipt/invoice:** delivery evidence, discrepancy handling, billing trigger, and reconciliation.
6. **Payment:** authorized channel, settlement matching, partial/failed/unapplied paths, and audit trail.
7. **Cross-stage:** system IDs, clocks, manual bridges, source owners, and missing/contradictory evidence.
8. **Learning:** how exceptions update dossiers/roadmaps without self-executing change.

## RP model mapping

1. Chain source inventory maps to Discovery **Sense** and profile/system domains.
2. Actor/system/state correlation maps to **Structure** without collapsing Org into Capability.
3. Evidence quality and gaps map to **Score** with confidence, not invented maturity.
4. End-to-end findings map to a versioned **Dossier** and claim/source trace.
5. HOLD/readiness findings map to bounded **Advise**, never authorization.

## HARD HOLD / prohibited zones

1. HARD HOLD if Research is asked to create/approve a quote/order, release shipment, issue invoice, contact customer, or move funds.
2. HARD HOLD on missing access/consent, uncontrolled customer/payment data, secrets, or untraceable chain IDs.
3. HARD HOLD if Discovery scores are used as Permission/grant, Promote, or Eng instruction.
4. HARD HOLD on Brain execute, Twin authorize, Terminal production connection, or Const/BP rewrite.

## Required artifacts

1. Dated/tokenized end-to-end observation log.
2. Stage/system/owner/source inventory.
3. Controlled sample/quote/order/shipment/receipt/invoice/payment handles.
4. Approval/control/audit event map.
5. Chain ID/timestamp/version correlation matrix.
6. Discovery domain coverage, gap, contradiction, and falsifier log.
7. Versioned dossier derivative and claim/source trace.

## Terminal research lens

A future read-only Terminal card may show chain state, evidence freshness, gaps, and accountable next gate. It must use synthetic T1 or authorized redacted references, display HOLD, and perform no transaction.

## Cross-reference and non-claim

- Site/system/risks: [SITE_PLAN](SITE_PLAN.md)
- Role questions/artifact follow-up: [INTERVIEW_PLAN](INTERVIEW_PLAN.md)
- Custody: [CUSTODY_PLAN](CUSTODY_PLAN.md)

RP-001 remains Open. This scenario does not create live evidence, mark Complete, flip a floor, Promote, open Eng work, or change Const/BP.
