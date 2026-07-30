# RP-006 Custody Plan

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Controls:** [DATA_MINIMIZATION_PACK](../../../templates/DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY](../../../templates/CHAIN_OF_CUSTODY.md)

## Scope

Controls topology/service references, readiness traces, access/audit/isolation evidence, supply-chain records, observability extracts, degraded-mode artifacts, and security-sensitive handles under the [SITE_PLAN](SITE_PLAN.md) and [FIELD_KIT](FIELD_KIT.md).

## Custody nodes

1. **Environment source:** system/security owners retain original topology, logs, configuration, and vulnerability data.
2. **Supervised export:** collector receives minimum redacted exports/IDs through approved read-only methods.
3. **Security intake:** custodian validates classification, secrets scan, tenant scope, integrity, and disclosure route.
4. **Readiness workspace:** criterion/source traces reference stable versions without embedding credentials or exploitable detail.
5. **Security/redaction review:** reviewer approves derivatives and records limitations/withheld fields.
6. **Registrar/disposition:** registrar uses controlled retrieval; temporary exports expire and security findings follow owner procedures.

## Responsibility roles

1. Environment/source owner authorizes systems, methods, exports, and source versions.
2. Infrastructure collector records metadata without active probing or configuration change.
3. Evidence custodian controls restricted storage, secrets checks, access logs, transfer, and retention.
4. Security/OT reviewer validates redaction, disclosure, isolation, and degraded-mode handling.
5. Registrar reviews evidence without treating custody as operational approval.

## Retention rules

1. Credentials, keys, raw vulnerabilities, detailed topology, and full logs are not retained by Research; source owners retain originals.
2. Temporary redacted exports expire at access expiry or after registrar review, whichever is earlier.
3. Safe readiness traces, export IDs/hashes, manifests, review decisions, and provenance follow the research record schedule.
4. Security incident/dispute hold preserves only affected encrypted versions and access logs until authorized release.

## Leakage response

1. Stop collection/transfer; isolate accounts, exports, links, and affected evidence store.
2. Notify environment owner, custodian, security/incident/privacy and OT contacts through approved channels.
3. Identify exposed secrets, topology, tenants, vulnerabilities, logs, recipients, sessions, and backups.
4. Revoke/rotate access where authorized, verify containment/deletion, preserve incident logs, and exclude evidence.

## Cross-reference and non-claim

- Environment/access/stop rules: [SITE_PLAN](SITE_PLAN.md)
- Minimum system/artifact fields: [FIELD_KIT](FIELD_KIT.md)
- Open gaps: [GAP](GAP.md)

No infrastructure observer is assigned. RP-006 remains Open; custody does not authorize scanning/configuration, Complete, floor change, Promote, Eng work, package change, or Const/BP change.
