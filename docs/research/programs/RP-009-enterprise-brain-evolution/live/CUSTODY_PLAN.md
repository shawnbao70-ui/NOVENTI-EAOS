# RP-009 Custody Plan

**Program:** Enterprise Brain Evolution  
**Status:** **Open** · **0 Complete**  
**Controls:** [DATA_MINIMIZATION_PACK](../../../templates/DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY](../../../templates/CHAIN_OF_CUSTODY.md)

## Scope

Controls dossier/input manifests, model/protocol versions, insights, simulations, recommendations, claim-source provenance, reviewer scores, tool-call/side-effect audits, and anti-execution cases under the [SITE_PLAN](SITE_PLAN.md) and [FIELD_KIT](FIELD_KIT.md).

## Custody nodes

1. **Enterprise/model source:** source and model/tool owners retain original dossiers, logs, configurations, and restricted artifacts.
2. **Authorized input intake:** collector registers minimum frozen inputs/handles and model/protocol/tool-policy versions.
3. **Isolated analysis:** insights/simulations/recommendations are versioned with parent/source links.
4. **Provenance/boundary capture:** claim graph and tool-call/side-effect audit append without production mutation.
5. **Redaction/review:** custodian/reviewer removes personal, tenant, secret, model, and security content while preserving limitations.
6. **Registrar/disposition:** registrar resolves controlled evidence; prompts/logs/temporary outputs expire under source-owner rules.

## Responsibility roles

1. Enterprise/model/tool source owners authorize versions, logs, and controlled retrieval.
2. Advisory collector records outputs and challenges without invoking mutating tools.
3. Evidence custodian controls isolated stores, access, integrity, transfers, and retention.
4. Provenance/anti-execution reviewer validates parent links, redaction, and zero-side-effect audit.
5. Registrar assesses evidence independently and excludes disputed model/tool records.

## Retention rules

1. Raw enterprise prompts/logs, credentials, proprietary model artifacts, and sensitive tool data remain in controlled source stores.
2. Temporary analysis inputs/outputs expire after reviewer/registrar assessment or environment access expiry.
3. Safe provenance graph, protocol/model IDs, reviewer decisions, anti-execution audit, manifest, and limitations follow the research record schedule.
4. Tool/security incident or provenance dispute freezes only affected versions/logs; supersession remains append-only.

## Leakage response

1. Stop analysis/tool access and isolate prompts, outputs, logs, handles, and accounts.
2. Notify enterprise/model/tool owners, custodian, privacy/security/legal and boundary contacts.
3. Trace exposed tenant/personal data, secrets, model content, recommendations, tool endpoints, recipients, and backups.
4. Revoke/rotate access where authorized, quarantine versions, verify deletion/return, preserve audits, and exclude evidence.

## Cross-reference and non-claim

- Advisory/anti-execution plan: [SITE_PLAN](SITE_PLAN.md)
- Minimum model/tool fields: [FIELD_KIT](FIELD_KIT.md)
- Open gaps: [GAP](GAP.md)

No provenance or anti-execution observer is assigned. RP-009 remains Open; custody does not authorize Brain/Twin action, Complete, floor change, Promote, Eng work, or Const/BP change.
