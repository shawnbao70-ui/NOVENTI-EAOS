# Live Observation Log

**Template ID:** NRI-TPL-OBS-LOG  
**Version:** 1.0  
**Status:** Structured field log — not verification or Complete  
**Last Updated:** 2026-07-23  
**Governing:** [INTERVIEW_PROTOCOL.md](INTERVIEW_PROTOCOL.md) · [SITE_ACCESS_PACK.md](SITE_ACCESS_PACK.md) · [DATA_MINIMIZATION_PACK.md](DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY.md](CHAIN_OF_CUSTODY.md)

> Create one log per bounded observation window. Write what was observed, said, inferred, or missing as separate evidence types. A full log does not establish tier or Complete.

## 1. Log header

| Field | Value |
|-------|-------|
| Log ID | `OBS-LC-YYYYMMDD-RP-00N-##` |
| LC ID / RP / claimed tier | |
| mode / status | live / Draft or In-progress |
| Site / tenant / cohort / environment | |
| Authorized window + timezone | |
| Actual start/end | |
| Observer / note taker | Real assigned identities |
| Escort / domain contact | |
| Systems / process / zones in scope | |
| Explicit exclusions | |
| Access/consent/custody references | |
| Instrument/protocol versions | |

## 2. Timebox plan

| Block | Planned time | Actual time | Scope / target | Stop/dependency |
|-------|--------------|-------------|----------------|-----------------|
| Entry/consent/access check | | | | |
| Context orientation | | | | |
| Normal-path observation | | | | |
| Exception/degraded-path observation | | | | |
| Artifact/source reconciliation | | | | |
| Member check / exit | | | | |

Do not extend beyond the authorized window without re-approval. Operational/safety needs override research timeboxes.

## 3. Observation entries

| Seq | UTC/local timestamp | Timebox | Actor role/token | System/location/version | Event / action | Evidence type | Source / artifact ID | Observer note | Confidence | Follow-up |
|-----|---------------------|---------|------------------|-------------------------|----------------|---------------|----------------------|---------------|------------|-----------|
| 001 | | | | | | Direct / statement / source display / inference / hearsay / unknown | | | High / Medium / Low | |

Rules:

- Use observable verbs and concrete sequence; avoid motive or maturity labels without evidence.
- Mark exact quotes; paraphrases and translations are labeled.
- Record “not observed” separately from “did not occur.”
- Capture system/event timestamps and known clock skew.
- Never enter credentials, secrets, unrestricted personal data, or prohibited raw payloads.
- Link screenshots/exports through artifact IDs and custody records, not pasted sensitive content.

## 4. Event detail card

Use for material events or exceptions:

| Field | Value |
|-------|-------|
| Entry / event ID | |
| Trigger / precondition | |
| Actors and systems | |
| Expected path | |
| Observed path | |
| Control / approval / decision | |
| Exception / workaround | |
| Outcome / recovery | |
| Source artifacts | |
| Competing explanation | |
| Falsifier / follow-up | |

## 5. Bias and observer-position record

Complete before, during, and after the session.

| Bias / influence | Before-session assumption | In-session signal | Mitigation / counter-check | Residual effect |
|------------------|---------------------------|-------------------|----------------------------|-----------------|
| Confirmation / desired outcome | | | | |
| Selection / missing roles or periods | | | | |
| Hawthorne / behavior changed by observer | | | | |
| Sponsor / authority pressure | | | | |
| Expertise / jargon interpretation | | | | |
| Recall / recency | | | | |
| Tool / instrumentation visibility | | | | |
| Translation / transcription | | | | |

Also record observer location, visibility, system access, interruptions, fatigue, prior relationships, and any role conflict.

## 6. Deviations and interruptions

| Deviation ID | Timestamp | Planned condition | Actual condition | Cause | Evidence impact | Decision / approver | Follow-up |
|--------------|-----------|-------------------|------------------|-------|-----------------|---------------------|-----------|
| | | | | | | | |

Examples: delayed access, unavailable system, shift/product change, missing role, revoked recording, incident, safety stop, degraded network, instrument version mismatch.

## 7. Contradictions and negative evidence

| Conflict ID | Claim / expectation | Evidence A | Evidence B / absent evidence | Interpretation | Owner | Status |
|-------------|---------------------|------------|-----------------------------|----------------|-------|--------|
| | | | | Unresolved / reconciled / excluded | | |

Do not resolve conflicts by majority vote, title, or deleting the weaker-looking record. Preserve competing sources and limits.

## 8. Artifact capture map

| Artifact ID | Entry/event IDs | Source owner/system | Collection method | Timestamp/version | Integrity / custody ref | Class/redaction | Status |
|-------------|-----------------|---------------------|-------------------|-------------------|-------------------------|-----------------|--------|
| | | | | | | | Requested / received / inaccessible / excluded |

An inaccessible or merely mentioned artifact remains a gap.

## 9. Consent, access, safety, and confidentiality changes

| Timestamp | Change | Raised by | Immediate action | Entries/artifacts affected | Required disposition |
|-----------|--------|-----------|------------------|----------------------------|----------------------|
| | | | | | |

Stop logging/recording immediately when consent/access is narrowed. Do not retroactively broaden consent.

## 10. End-of-window reconciliation

- [ ] Actual window, systems, versions, actors, interruptions, and exclusions recorded.
- [ ] Direct observations, statements, inferences, hearsay, and unknowns are separated.
- [ ] Artifact IDs reconcile with custody manifest; unauthorized material quarantined.
- [ ] Contradictions, absent evidence, falsifiers, and missing perspectives are explicit.
- [ ] Bias/deviation record is complete.
- [ ] Participant/member-check corrections are append-only.
- [ ] Temporary accounts/access revoked and site exit actions complete.
- [ ] Raw notes/recordings moved to approved custody or disposed per schedule.

## 11. Session summary

| Field | Value |
|-------|-------|
| Observations supporting claims | |
| Observations challenging claims | |
| Not observed / unavailable | |
| Material deviations | |
| Bias / limitations | |
| Follow-up artifacts/interviews | |
| Safety/privacy/security events | |
| Custody/disposition status | |

**Observer attestation:** “This log distinguishes direct observation, participant statement, source display, inference, hearsay, and unknown to the best of my knowledge.”  
**Real observer / timestamp:**  

**Invariant:** observation logged ≠ artifact accepted ≠ tier verified ≠ Registry Complete. No log can itself flip a floor, Promote, open Eng work, or change Const/BP.
