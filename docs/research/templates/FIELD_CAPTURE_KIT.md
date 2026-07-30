# Field Capture Kit

**Template ID:** NRI-TPL-FIELD-KIT  
**Version:** 1.0  
**Status:** Minimum field-preparation package — not live evidence  
**Last Updated:** 2026-07-23  
**Governing:** [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md) · [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) · [LIVE_VS_SYNTHETIC_FENCE.md](LIVE_VS_SYNTHETIC_FENCE.md)

> This kit establishes the minimum fields to collect during an authorized field capture. A filled kit is neither verification nor Complete. The LC form, resolvable artifacts, registrar review, and V3/V4 transaction remain mandatory.

## Capture identity

| Field | Required value |
|-------|----------------|
| Capture ID | `LC-YYYYMMDD-RP-00N-##` |
| RP / claimed tier | RP-001…010 / T2 or T3 |
| mode / status | `live` / Draft or In-progress |
| site / tenant / cohort | Real authorized context |
| purpose and scope | Included/excluded systems, processes, domains |

## Who

| Field | Required value |
|-------|----------------|
| Observer | Real name, role, affiliation, contact/controlled identity reference |
| Domain representative | Real accountable source/context contact |
| Facilitator / submitter | Real names and responsibilities |
| Evidence custodian | Owner of each restricted source/handle |
| T3 witness/attestor | Real identity and attestation route, when applicable |
| Consent | Participation/recording basis and timestamp |

Never pre-fill, infer, or invent identities. Role names alone do not satisfy observer requirements.

## When

| Field | Required value |
|-------|----------------|
| Window | Start/end with timezone, or justified `as_of` |
| Collection timestamps | UTC per artifact/export |
| System time basis | Clock source and known skew if relevant |
| Submission / verification | UTC timestamps, recorded separately |
| Retention / expiry | Duration, disposition, and renewal/expiry trigger |

## What system / context

| Field | Required value |
|-------|----------------|
| System/context name | Site, tenant, environment, cohort, process, or cell |
| Owner / custodian | Accountable organization/contact |
| Environment class | Pilot, non-production, production, multi-site, executive-attested |
| Version / configuration | Relevant release, instrument, model, process, or protocol version |
| Boundary | Read-only/supervised scope, exclusions, dependencies, degraded state |

## What artifacts

For each item record:

- Artifact ID; repository path or controlled external handle.
- Kind/format, producer/source system, collection timestamp, and claim IDs supported.
- Integrity marker: hash, export ID, immutable version, or explicit reason none applies.
- Custodian, access classification, redaction state, retention/expiry, and registrar access check.
- Known gaps, transformations, filters, sampling, conflicting evidence, and falsifier result.

Minimum package: dated observation record, source/context evidence, program-specific output, claim-to-source trace, exception/falsifier log, and provenance/retention record.

## What permission

| Field | Required value |
|-------|----------------|
| Site/system access approval | Approver, scope, basis, granted/expiry timestamps |
| Collection permission | Allowed interviews, screenshots, exports, recordings, measurements |
| Data-use basis | Consent, agreement, policy, or other authorized basis |
| Handling controls | Classification, encryption/store, redaction, sharing, deletion |
| Safety/security constraints | Stop rules, escort/PPE, disclosure route, prohibited actions |
| Registrar retrieval | Who may resolve each handle and under what conditions |

Capture permission is not product Permission and never grants runtime authority.

## Field stop conditions

Stop collection and record the reason if access/consent is absent or revoked, scope is exceeded, safety/security is at risk, source identity/provenance is uncertain, restricted data cannot be handled safely, or a participant asks the researcher to perform an operational action.

## Handoff

1. Preserve source material in its authorized store; put only safe metadata/handles in repository Markdown.
2. Transfer fields into a fresh [LIVE_EVIDENCE_CAPTURE_TEMPLATE](LIVE_EVIDENCE_CAPTURE_TEMPLATE.md).
3. Keep status Draft/In-progress until all intake and tier gates pass.
4. A kit, signature, artifact count, or field visit alone cannot mark Complete, flip a floor, Promote, open Eng work, or change Const/BP.

**Default outcome:** kit prepared / capture pending; Registry unchanged.
