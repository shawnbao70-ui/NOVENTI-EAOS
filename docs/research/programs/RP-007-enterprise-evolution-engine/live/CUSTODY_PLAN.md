# RP-007 Custody Plan

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Controls:** [DATA_MINIMIZATION_PACK](../../../templates/DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY](../../../templates/CHAIN_OF_CUSTODY.md)

## Scope

Controls frozen dossier inputs, trigger traces, recommendation/HOLD ledgers, simulations, usefulness scores, human decisions, side-effect audits, and dissent under the [SITE_PLAN](SITE_PLAN.md) and [FIELD_KIT](FIELD_KIT.md).

## Custody nodes

1. **Dossier source:** enterprise/source owners retain originals and provide a frozen controlled version/handle.
2. **Evaluation intake:** collector registers input/version/timestamp and trigger evidence before analysis.
3. **Recommendation workspace:** immutable ledger links recommendations/HOLD to sources, assumptions, and protocol versions.
4. **Decision capture:** independent scores and human accept/defer/reject records append without authorizing execution.
5. **Boundary review:** custodian/reviewer reconciles simulation, tool-call, and zero-side-effect audit artifacts.
6. **Registrar/disposition:** registrar resolves controlled records; temporary strategy/workforce extracts expire after review.

## Responsibility roles

1. Dossier/source owner validates input freeze and authorized decision-context use.
2. Evaluation collector records triggers/recommendations without operational action.
3. Evidence custodian controls immutable ledger versions, access, transfers, and retention.
4. Independent/boundary reviewer preserves blind scoring, HOLD, dissent, and side-effect evidence.
5. Registrar assesses the claimed tier and excludes altered or untraceable recommendations.

## Retention rules

1. Raw strategy/workforce/operational dossier sources remain with owners; frozen handles/versions support trace.
2. Simulation working files and temporary extracts expire after decision/registrar review unless dispute hold applies.
3. Recommendation/HOLD ledger, decision record, side-effect audit, manifest, and provenance follow the research record schedule.
4. Superseded recommendations remain linked and read-only; learning never overwrites prior evidence/decisions.

## Leakage response

1. Stop evaluation/sharing and isolate dossier, simulation, ledger, and decision workspaces.
2. Notify source owner, custodian, privacy/security/legal and accountable decision contacts.
3. Trace exposed strategy/workforce facts, recommendations, decisions, model inputs/outputs, and copies.
4. Revoke access, quarantine affected versions, rebuild safe derivatives, verify disposition, and preserve dissent/audit.

## Cross-reference and non-claim

- Advisory observation/exit rules: [SITE_PLAN](SITE_PLAN.md)
- Required inputs/permissions: [FIELD_KIT](FIELD_KIT.md)
- Open gaps: [GAP](GAP.md)

No decision representative or observer is assigned. RP-007 remains Open; custody never creates execution authority, Complete, floor change, Promote, Eng work, or Const/BP change.
