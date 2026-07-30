# RP-003 Custody Plan

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Controls:** [DATA_MINIMIZATION_PACK](../../../templates/DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY](../../../templates/CHAIN_OF_CUSTODY.md)

## Scope

Controls source catalogs, graph versions, node/outcome traces, maturity/automation rationale, roadmap comparisons, and dissent artifacts collected under the [SITE_PLAN](SITE_PLAN.md) and [FIELD_KIT](FIELD_KIT.md).

## Custody nodes

1. **Source catalogs:** process, service, portfolio, outcome, and organization owners retain original records.
2. **Authorized extract:** collector registers minimum source handles and records query/filter/version.
3. **Graph construction:** modeling workspace creates versioned nodes/edges with source IDs and no permission data.
4. **Comparison derivative:** capability and department-roadmap comparisons link to frozen graph/rubric versions.
5. **Review/redaction:** custodian/reviewer checks commercial, personal, and organization-sensitive content plus graph integrity.
6. **Registrar/disposition:** registrar resolves graph/source versions; temporary exports are returned/deleted and safe manifests retained.

## Responsibility roles

1. Source owners validate catalogs, outcomes, and authorized extract boundaries.
2. Graph collector/modeler records provenance and does not collapse capability into organization.
3. Evidence custodian controls workspace access, exports, integrity checks, and retention.
4. Capability/redaction reviewer verifies source-to-node trace, transformations, and confidentiality.
5. Registrar reviews evidence independently and records disputed mappings.

## Retention rules

1. Raw strategy/portfolio/organization sources remain with owners; controlled handles are preferred.
2. Working graph exports and comparison extracts expire after registrar review or access expiry, whichever is earlier.
3. Safe immutable graph versions, rubrics, manifests, dissent, and provenance follow the research record schedule.
4. Superseded graph versions remain linked for audit but lose active access; legal hold or dispute preserves only affected versions.

## Leakage response

1. Freeze graph sharing/export and isolate affected source handles/workspace versions.
2. Notify source owners, custodian, security/privacy contacts and preserve graph/access history.
3. Identify exposed nodes, strategies, organization links, personal labels, derivatives, and recipients.
4. Revoke access, redact/rebuild affected graph versions, verify deletion/return, and exclude disputed evidence.

## Cross-reference and non-claim

- Observation/system boundaries: [SITE_PLAN](SITE_PLAN.md)
- Field/artifact fields: [FIELD_KIT](FIELD_KIT.md)
- Open gaps: [GAP](GAP.md)

No observer is assigned. RP-003 remains Open; custody cannot create Capability→Permission/grant, Complete, floor change, Promote, Eng work, or Const/BP change.
