# RP-004 Authorization Exception Card

**Program:** Organization Neutrality  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD where authorization depends on organization-specific titles, hierarchy, teams, or shortcuts. Separate legitimate context from hard-coded organization assumptions without changing roles or access.

## Authorization / bypass observation points

1. Compare formal permission roles with job titles, departments, reporting lines, and informal delegation.
2. Observe owner, manager, tenant, site, legal-entity, and business-unit scope on the same action.
3. Trace whether role aliases or default roles silently broaden access across organizational contexts.
4. Record administrator, support, acting-role, emergency, and shared-account bypass practices.
5. Compare approval/confirmation labels with specified-approver and segregation-of-duty enforcement.
6. Observe joiner, mover, leaver, temporary delegation, expiry, and access-review exception handling.
7. Capture denials or workarounds caused by reorganizations, vacant roles, cross-team work, and matrix reporting.

## Scoring / HOLD

- Score organizational coupling, scope precision, delegation custody, expiry, review, and audit.
- Dossier local vocabulary and exceptions without treating one org chart as canonical.
- HOLD when a title, manager relationship, or hidden button is the only evidence of authority.

## Required live evidence

1. Authorized redacted role-to-responsibility and scope mappings.
2. Allow/deny traces across at least two relevant organizational contexts.
3. Delegation, acting-role, joiner/mover/leaver, expiry, and review artifacts.
4. Privileged/shared-account exception procedure and audit records, or documented absence.
5. Specified-approver and segregation-of-duty evidence for high-impact actions.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-004 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, org model, role catalog, Identity, API/UI, or code modification.
3. No Brain execute, Twin authorize, CRUD, account sharing, impersonation, role assumption, or access probing.
4. No synthetic organization scenario relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no organizational, identity, role, or delegation change.
