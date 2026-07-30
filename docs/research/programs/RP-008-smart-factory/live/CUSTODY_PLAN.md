# RP-008 Custody Plan

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Controls:** [DATA_MINIMIZATION_PACK](../../../templates/DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY](../../../templates/CHAIN_OF_CUSTODY.md)

## Scope

Controls walkthrough records, SF/risk assessments, process/event maps, safety approvals/vetoes, OT/MES/historian handles, operational metrics, and degraded-mode evidence under the [SITE_PLAN](SITE_PLAN.md) and [FIELD_KIT](FIELD_KIT.md).

## Custody nodes

1. **Plant/OT source:** plant, safety, MES, historian, quality, and maintenance owners retain original records.
2. **Escorted collection:** observer/collector registers minimum approved notes, extracts, timestamps, and source handles.
3. **Safety/security intake:** custodian validates zone/shift/product context, classification, integrity, and no-control boundary.
4. **Analysis workspace:** redacted event/process/risk/metric derivatives link to source/export IDs and formulas.
5. **Plant review/redaction:** safety/OT/data reviewers validate sensitive topology, worker, recipe, incident, and metric handling.
6. **Registrar/disposition:** registrar uses controlled retrieval; temporary OT/production extracts are returned/deleted promptly.

## Responsibility roles

1. Plant/source owners authorize systems, shift/cell scope, and source exports.
2. Escorted collector records observations without operating equipment or distracting workers.
3. Evidence custodian controls OT/production artifact storage, access, transfer, and retention.
4. Safety/OT/privacy reviewer validates redaction, context, calculations, and incident routing.
5. Registrar reviews tier evidence without treating custody as machine/MES approval.

## Retention rules

1. Raw OT/MES/historian, recipe, worker, incident, and safety records remain in plant-controlled stores.
2. Temporary redacted event/metric extracts expire after source validation and registrar review or site access expiry.
3. Safe assessments, formulas, export IDs, manifests, approvals, and provenance follow the research record schedule.
4. Safety incident/security investigation or legal hold preserves only scoped evidence under plant authority.

## Leakage response

1. Stop collection/sharing; exit/secure the area if directed and isolate devices, accounts, and exports.
2. Notify plant stop authority, source owner, custodian, safety, OT security, privacy/legal contacts.
3. Identify exposed workers, incidents, topology, recipes, production metrics, vulnerabilities, recipients, and copies.
4. Revoke access, follow plant incident process, verify return/deletion, preserve required logs, and exclude evidence.

## Cross-reference and non-claim

- Plant access/safety plan: [SITE_PLAN](SITE_PLAN.md)
- Minimum field/OT permissions: [FIELD_KIT](FIELD_KIT.md)
- Open gaps: [GAP](GAP.md)

No plant/safety observer is assigned. RP-008 remains Open; custody does not authorize machine/MES action, Complete, floor change, Promote, Eng work, or Const/BP change.
