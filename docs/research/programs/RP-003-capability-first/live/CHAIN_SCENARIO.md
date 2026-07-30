# RP-003 Commercial Chain Scenario

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Live chain/observer assigned:** none / none  
**Protocol:** [COMMERCIAL_CHAIN_OBSERVATION](../../../templates/COMMERCIAL_CHAIN_OBSERVATION.md) · **Terminal lens:** [TERMINAL_SCENARIO_CARD](../../../templates/TERMINAL_SCENARIO_CARD.md)

## Research purpose

Use the commercial chain to test capability definitions, dependencies, maturity, and automation affinity independently of departments, titles, and Permission.

## Chain observation points

1. **Sample:** product knowledge, customer qualification, sample orchestration, and evidence capability.
2. **Quote:** pricing, configuration, risk/compliance, and approval capabilities.
3. **Order:** contract acceptance, credit/compliance, demand capture, and change-control capabilities.
4. **Shipment:** planning, inventory, fulfillment, logistics, trade, and exception capabilities.
5. **Receipt/invoice:** delivery assurance, dispute, billing, tax, and reconciliation capabilities.
6. **Payment:** collections, cash application, fraud/control, and settlement capabilities.
7. **Cross-stage:** capability dependencies, duplicated local work, manual bridges, and outcome ownership.
8. **Exception path:** maturity and automation-affinity evidence under hold/change/failure.

## RP model mapping

1. Stage outcomes become candidate capability nodes, not department labels.
2. Cross-stage handoffs become graph dependencies and failure edges.
3. Observable controls/consistency support L0–L4 maturity rationale.
4. Repetition, rules, exceptions, and risk support A0–A4 automation-affinity rationale.
5. Chain-level outcome clarity supports capability-versus-department roadmap comparison.

## HARD HOLD / prohibited zones

1. HARD HOLD if capability names merely copy departments, roles, systems, or transaction states.
2. HARD HOLD if graph ownership becomes Permission/grant or transaction approval.
3. HARD HOLD on Research performing any quote/order/shipment/invoice/payment action.
4. HARD HOLD on Brain execute, Twin authorize, Terminal product connection, Promote/Eng opening, or Const/BP change.

## Required artifacts

1. Dated/tokenized chain observation log.
2. Stage outcome/capability candidate inventory.
3. Versioned capability graph and glossary.
4. Stage-to-node/dependency/source trace.
5. Maturity and automation-affinity evidence/rationale.
6. Exception/contradiction/falsifier log.
7. Capability-versus-department roadmap comparison.

## Terminal research lens

A future read-only card may present chain state through capability outcomes/dependencies and HOLD evidence. Role labels never grant access; all actions remain simulated.

## Cross-reference and non-claim

- Mapping/site controls: [SITE_PLAN](SITE_PLAN.md)
- Capability interview guide: [INTERVIEW_PLAN](INTERVIEW_PLAN.md)
- Graph/source custody: [CUSTODY_PLAN](CUSTODY_PLAN.md)

RP-003 remains Open. This scenario does not mark Complete, flip a floor, Promote, open Eng work, mint grants, or change Const/BP.
