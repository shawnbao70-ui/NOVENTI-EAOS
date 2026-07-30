# Data Minimization Pack

**Template ID:** NRI-TPL-DATA-MIN  
**Version:** 1.0  
**Status:** Field-data planning and control — not live evidence  
**Last Updated:** 2026-07-23  
**Governing:** [SITE_ACCESS_PACK.md](SITE_ACCESS_PACK.md) · [FIELD_CAPTURE_KIT.md](FIELD_CAPTURE_KIT.md) · [CHAIN_OF_CUSTODY.md](CHAIN_OF_CUSTODY.md) · [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md)

> Collect the least data needed to answer the declared research question. Access, possession, convenience, or future usefulness is not a justification. Completing this pack does not verify evidence or mark Complete.

## 1. Purpose, scope, and necessity

| Field | Required value |
|-------|----------------|
| Proposed LC ID / RP | |
| Research question | |
| Named context and window | |
| Decision supported | Research assessment only |
| Data subjects / systems | |
| Explicitly excluded uses | |
| Minimization owner | Real accountable person |
| Review / expiry date | |

For each proposed field, document why it is necessary, why a less sensitive substitute is insufficient, and which claim cannot be assessed without it.

## 2. Classification model

| Class | Examples | Default handling |
|-------|----------|------------------|
| Public | Published specifications, public reports | May be referenced with source/version |
| Internal | Process summaries, non-public operating metadata | Controlled store; limited distribution |
| Confidential | Strategy, customer, financial, workforce, legal, source extracts | Named access, encryption, redaction, short retention |
| Restricted | Credentials, security findings, sensitive personal/health data, OT topology, raw tenant payloads | Do not collect by default; controlled source handle only |

The source owner’s stricter classification always wins.

## 3. Allowed field inventory

Allowed fields must be claim-linked and minimum-granularity.

| Field / category | Claim ID | Necessity | Minimum granularity | Source | Collection method | Class | Approved by |
|------------------|----------|-----------|---------------------|--------|-------------------|-------|-------------|
| | | | | | | | |

Preferred forms:

- Counts, bands, ranges, derived metrics, redacted excerpts, and sampled windows.
- Stable source/export identifiers instead of copied raw payloads.
- Role classes instead of person names unless observer identity is required.
- Site/tenant aliases in working notes, with identity retained only in controlled registration.
- Screenshots cropped to the necessary region with metadata separately captured.

## 4. Prohibited fields and content

Do not collect unless a separately documented legal/ethical necessity and approved exception exists:

1. Passwords, private keys, tokens, session cookies, MFA secrets, recovery codes, or connection strings.
2. Full raw tenant/customer exports when a scoped extract or controlled handle suffices.
3. Unrelated personal identifiers, contact details, health data, biometrics, compensation, discipline, or performance records.
4. Unredacted legal privilege, board material, trade secrets, security vulnerabilities, OT recipes, or critical-infrastructure topology.
5. Production prompts/logs containing unrelated user content or hidden system secrets.
6. Audio/video/photography outside explicit consent and site permission.
7. Data about non-participants or out-of-scope systems/processes.
8. Synthetic fixtures mixed into live evidence without explicit T1 fencing.

## 5. Collection design review

- [ ] Every field maps to a stated observation/claim.
- [ ] Sampling window and population are the smallest adequate.
- [ ] Read-only view, aggregate, or supervised export was considered before raw copy.
- [ ] Collection excludes unrelated columns, rows, attachments, and metadata.
- [ ] Search/query filters are fixed and recorded before export where practical.
- [ ] Observer notes distinguish direct evidence, statement, inference, and unknown.
- [ ] Stop conditions cover accidental overscope and sensitive-data discovery.

## 6. De-identification and redaction

| Technique | Use | Required record |
|-----------|-----|-----------------|
| Suppression | Remove unnecessary fields/rows/regions | Removed categories and reviewer |
| Masking | Partially obscure identifiers | Rule and residual re-identification risk |
| Generalization | Replace exact values with ranges/bands | Transformation and analytical impact |
| Tokenization/pseudonymization | Separate identity from research record | Token owner and mapping-store controls |
| Aggregation | Combine records to minimum adequate group | Group size and small-cell policy |
| Cropping/transcription | Retain only necessary screen/document content | Source handle and transcription reviewer |

- [ ] Redaction is performed before repository entry or broad transfer.
- [ ] Originals remain with the authorized custodian where possible.
- [ ] Re-identification key is separated, access-limited, and excluded from research Markdown.
- [ ] Transformations, quality loss, and residual risk are recorded.
- [ ] A second reviewer checks high-risk redaction before handoff.

## 7. Storage and access controls

| Store / handle | Data class | Owner | Allowed roles | Encryption / protection | Audit source | Backup | Region |
|----------------|------------|-------|---------------|-------------------------|--------------|--------|--------|
| | | | | | | | |

Requirements:

1. Restricted raw material stays in its approved source or evidence store.
2. Repository files contain safe metadata and controlled handles, not secrets/raw payloads.
3. Access is named, least-privilege, time-bounded, logged, and revoked on role/need change.
4. Copies, caches, downloads, email/chat transfers, and local temp files are prohibited unless explicitly listed.
5. Backup, replication, region, and legal-hold behavior are understood before collection.

## 8. Retention schedule

| Artifact category | Start event | Active retention | Review trigger | Maximum retention | Disposition |
|-------------------|-------------|------------------|----------------|-------------------|-------------|
| Raw restricted source | | | | | Return/delete/owner retained |
| Redacted working extract | | | | | Delete/archive |
| Observation notes | | | | | Redact/archive/delete |
| Manifest/provenance | | | | | Preserve per research record |
| Consent/access record | | | | | Preserve per policy |

Rules:

- Retention begins from explicit collection/closure events, not an undefined future milestone.
- Keep raw and working data no longer than necessary; retain safe provenance/decision metadata longer when required.
- Legal hold or incident preservation pauses deletion only for the specified scope.
- Re-review access and necessity at each trigger; silence is not renewal.

## 9. Destruction and return

Approved methods must match media/store and include verification:

- Controlled source: revoke handle/access; custodian confirms disposition.
- Encrypted logical record: verified deletion plus key lifecycle where applicable.
- Local working file/cache: secure deletion per platform capability and device policy.
- Physical notes/media: approved shredding/destruction/return.
- Backup: expire through documented backup lifecycle; record residual period.

| Item / category | Method | Requested by | Executed by | Timestamp | Verification | Exceptions |
|-----------------|--------|--------------|-------------|-----------|--------------|------------|
| | | | | | | |

Never claim destruction when only a link, shortcut, or repository reference was removed.

## 10. Exception process

An exception must identify the prohibited/additional field, necessity, alternatives rejected, risk, safeguards, approver, duration, affected participants, and destruction date.

| Exception ID | Field / scope | Necessity | Risk / safeguard | Approver | Expiry | Decision |
|--------------|---------------|-----------|------------------|----------|--------|----------|
| | | | | | | |

No retrospective exception may legitimize unauthorized collection. Quarantine first, then decide return/deletion/incident handling.

## 11. Overscope or leakage response

1. Stop collection and preserve safety; do not inspect more than necessary to identify scope.
2. Isolate the item/store, revoke sharing/access, and prevent further copies.
3. Notify evidence custodian plus privacy/security/legal/site contacts according to classification.
4. Record what was exposed, to whom, when, where, and which copies/backups may exist.
5. Follow approved return/deletion/incident/legal-hold instructions.
6. Correct the manifest and custody log without erasing the original record.
7. Reassess whether the capture can continue; default to stop for uncertain restricted data.

## 12. Sign-off

| Review | Real name / role | Decision | Timestamp | Conditions |
|--------|------------------|----------|-----------|------------|
| Research necessity | | | | |
| Source/data owner | | | | |
| Privacy/ethics | | | | |
| Security/site | | | | |
| Retention/destruction owner | | | | |

**Minimization readiness:** Not ready / Ready for authorized collection / Withdrawn  
**Residual risks:**  

This readiness decision does not establish live evidence, satisfy T2/T3, mark Complete, flip a floor, Promote, open Eng work, or change Const/BP.
