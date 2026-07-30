# Evidence Chain of Custody

**Template ID:** NRI-TPL-CHAIN-CUSTODY  
**Version:** 1.0  
**Status:** Evidence-control template — custody ≠ acceptance ≠ Complete  
**Last Updated:** 2026-07-23  
**Governing:** [DATA_MINIMIZATION_PACK.md](DATA_MINIMIZATION_PACK.md) · [FIELD_CAPTURE_KIT.md](FIELD_CAPTURE_KIT.md) · [ARTIFACT_ACCEPTANCE_RUBRIC.md](ARTIFACT_ACCEPTANCE_RUBRIC.md) · [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md)

> A custody record shows where an artifact came from, who controlled it, how it changed, and whether it can be reviewed. It does not prove truth, quality, tier, or Complete.

## 1. Record identity

| Field | Required value |
|-------|----------------|
| Custody record ID | `COC-LC-YYYYMMDD-RP-00N-##` |
| Capture ID / RP | |
| Claimed tier / mode | T2 or T3 candidate / live |
| Custody opened at (UTC) | |
| Custody coordinator | Real name, role, contact |
| Controlling policy / agreement | |
| Primary evidence store | |
| Status | Open / Quarantined / Closed |

## 2. Responsibility roles

| Role | Responsibility | Separation / constraint |
|------|----------------|-------------------------|
| Producer/source owner | Creates or controls original source | Does not self-verify research acceptance |
| Collector | Performs authorized minimum collection | Cannot expand scope without approval |
| Evidence custodian | Controls storage, access, retention, and transfer | Preserves original and logs actions |
| Redaction/transformation reviewer | Validates safe derivative and quality impact | Does not overwrite original |
| Registrar/reviewer | Resolves handles and assesses rubric/intake | Custody receipt is not acceptance |
| Incident/dispute owner | Coordinates leakage, mismatch, or challenge | Preserves contested versions |

Record real identities only when assigned; never invent a role holder.

## 3. Artifact manifest

| Artifact ID | Description / claim IDs | Source system / producer | Original or derivative | Collected at (UTC) | Class | Store / handle | Custodian | Retention / expiry |
|-------------|-------------------------|--------------------------|------------------------|--------------------|-------|----------------|-----------|--------------------|
| | | | | | | | | |

Every derivative links to its parent artifact and transformation record.

## 4. Integrity, hash, and version record

| Artifact ID | Algorithm / version method | Digest / export ID / immutable version | Size / format | Tool/version | Verified at | Verified by | Result |
|-------------|----------------------------|----------------------------------------|---------------|--------------|-------------|-------------|--------|
| | SHA-256 / export ID / repository version / justified alternative | | | | | | |

Rules:

1. Hash bytes before transformation where access permits; hash each derivative separately.
2. Record algorithm, tool/version, canonicalization/compression, and format.
3. A mutable dashboard/URL is not an integrity marker; capture a stable export/version or document the limitation.
4. Never recompute and silently replace a mismatched digest. Open a discrepancy.
5. If hashing is prohibited, use source export ID, signed record, immutable version, or custodian attestation and state the limitation.

## 5. Custody nodes

The minimum lifecycle is:

1. **Source:** original remains with producer/source owner.
2. **Authorized collection:** collector creates or registers the minimum extract/handle.
3. **Secure intake:** custodian validates class, identity, integrity, and scope.
4. **Transformation/redaction:** derivative is created with parent link and review.
5. **Registrar review:** reviewer obtains controlled read access and records verification.
6. **Retention/disposition:** custodian archives, returns, expires, or destroys per schedule.

Skipping a node requires an explicit exception and risk decision.

## 6. Transfer and access log

| Event ID | UTC timestamp | Artifact ID/version | From | To / actor | Purpose | Method / channel | Access level | Integrity before/after | Acknowledged by |
|----------|---------------|---------------------|------|------------|---------|------------------|--------------|------------------------|-----------------|
| | | | | | | | | | |

Log view/download/export/copy/redaction/transfer/return/deletion events according to classification. A repository link change is not custody transfer of an external artifact.

## 7. Transformation and redaction log

| Transformation ID | Parent artifact | Output artifact | Purpose | Exact operations / filters | Tool/version | Performed by / at | Reviewed by / at | Quality loss / residual risk |
|-------------------|-----------------|-----------------|---------|----------------------------|--------------|-------------------|------------------|------------------------------|
| | | | | | | | | |

Do not overwrite source artifacts. Sampling, timezone conversion, transcription, OCR, aggregation, normalization, and manual correction are transformations and must be logged.

## 8. External controlled handles

For an artifact that cannot enter the repository:

| Field | Required value |
|-------|----------------|
| Stable handle / export ID | |
| Source owner / custodian | |
| Retrieval route and eligible roles | |
| Availability window / expiry | |
| Version / integrity basis | |
| Classification / redaction | |
| Registrar access test and timestamp | |
| Fallback if unavailable | |

A bare URL, inaccessible drive path, or verbal claim is insufficient custody.

## 9. Discrepancy and dispute handling

Open a dispute when hashes/versions differ, chronology conflicts, source ownership is contested, access logs are incomplete, redaction is challenged, an artifact appears altered, or submitter and registrar disagree about provenance.

| Dispute ID | Artifact/version | Raised by / at | Issue | Evidence preserved | Access freeze | Owner | Resolution / status |
|------------|------------------|----------------|-------|--------------------|---------------|-------|---------------------|
| | | | | | yes / no | | |

Procedure:

1. Preserve all contested versions and logs; never delete or overwrite the disputed record.
2. Freeze nonessential transfer and mark the artifact disputed.
3. Re-verify from source owner/export, timestamps, signatures, hashes, and audit logs.
4. Record competing explanations, confidence, dissent, and unresolved limitations.
5. Issue a superseding derivative/version only with explicit linkage; do not rewrite history.
6. If unresolved, exclude the artifact from tier support and mark intake incomplete.

## 10. Correction and supersession

Corrections are append-only:

- Original artifact/metadata remains identifiable.
- Correction reason, requester, approver, timestamp, and affected claims are logged.
- New digest/version and parent/superseded relation are recorded.
- Evidence Pack, capture form, rubric, and registry references are reconciled.
- A correction never retroactively fabricates access, consent, timestamp, or observer presence.

## 11. Loss, leakage, or unauthorized access

1. Stop transfer/collection and isolate affected artifacts/accounts.
2. Preserve relevant logs and evidence without spreading sensitive content.
3. Notify custodian and required privacy/security/legal/site owners.
4. Record affected versions, people/systems, time range, copies, backups, and claims.
5. Rotate/revoke access where authorized; follow source-owner incident procedures.
6. Decide quarantine, return, destruction, or legal hold; document verification.
7. Reassess admissibility. Compromised custody defaults to exclusion until resolved.

## 12. Retention and disposition

| Artifact/category | Retention start | Review interval | Maximum / trigger | Legal hold | Final action | Executed / verified |
|-------------------|-----------------|-----------------|-------------------|------------|--------------|---------------------|
| | | | | | | |

Disposition options: source-owner retained, controlled archive, returned, verified deletion, destroyed physical media, or excluded/quarantined. Record backup residuals and access revocation.

## 13. Closure and attestation

| Check | Result / reference |
|-------|--------------------|
| Manifest reconciled | |
| Integrity/version checks resolved | |
| Transfers/access accounted for | |
| Derivatives linked and reviewed | |
| Disputes resolved or excluded | |
| Retention/disposition scheduled | |
| Restricted access revoked/confirmed | |

| Attestor | Real name / role | Timestamp | Scope / statement |
|----------|------------------|-----------|-------------------|
| Custodian | | | |
| Registrar | | | |

**Custody outcome:** Open / Quarantined / Closed and reviewable / Closed with exclusions  

Custody closure means only that the chain record is reconciled. It is not artifact acceptance, T2/T3 verification, Registry Complete, readiness-floor change, Board Promote, Eng authorization, or Const/BP change.
