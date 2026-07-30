# Site Access Pack

**Template ID:** NRI-TPL-SITE-ACCESS  
**Version:** 1.0  
**Status:** Field-access preparation — not access approval and not live evidence  
**Last Updated:** 2026-07-23  
**Governing:** [FIELD_CAPTURE_KIT.md](FIELD_CAPTURE_KIT.md) · [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) · [LIVE_VS_SYNTHETIC_FENCE.md](LIVE_VS_SYNTHETIC_FENCE.md) · [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md)

> Complete this pack before entering a site, tenant, environment, cohort, executive session, or controlled system. A prepared or approved pack does not prove that observation occurred and can never mark a Registry row Complete.

## 1. Request identity and scope

| Field | Required value |
|-------|----------------|
| Proposed LC ID | `LC-YYYYMMDD-RP-00N-##` |
| Program / claimed tier | RP-001…010 / T2 or T3 candidate |
| Request owner | Real name, affiliation, accountable contact |
| Site/context owner | Real authorized approver; do not infer |
| Location / tenant / environment / cohort | Exact authorized context |
| Observation purpose | Research question and expected decision use |
| Included scope | Systems, spaces, processes, roles, artifacts |
| Explicit exclusions | Actions, systems, zones, data, people not in scope |

## 2. People and responsibility

List actual people only after participation is agreed.

| Role | Name / controlled identity | Responsibility | Contact route | Confirmed at |
|------|----------------------------|----------------|---------------|--------------|
| Site/context approver | | Access authorization | | |
| Escort / environment custodian | | Supervision and stop authority | | |
| Lead observer | | Evidence distinction and notes | | |
| Domain representative | | Source/context validation | | |
| Safety / security contact | | Incident and stop procedure | | |
| Evidence custodian | | Restricted artifact handling | | |
| T3 witness/attestor, if applicable | | Independent attestation | | |

No blank role may be replaced by an invented name. Missing required roles means access is not ready.

## 3. Safety and operational entry

- [ ] Site induction/training requirements identified and scheduled.
- [ ] Escort, badge, zone, PPE, accessibility, emergency, muster, and evacuation rules recorded.
- [ ] Physical/OT hazards and prohibited areas/actions explained.
- [ ] Stop-work authority and immediate contact route confirmed.
- [ ] Photography, audio/video, screen capture, removable media, and device rules confirmed.
- [ ] Observation will not alter production, safety control, machine state, workflow, schedule, recipe, configuration, or business decision.
- [ ] Incident/near-miss reporting route and post-incident evidence restrictions recorded.

### Safety detail

| Field | Value |
|-------|-------|
| Required training / PPE | |
| Escort and stop authority | |
| Emergency contact / route | |
| Restricted zones / activities | |
| Accessibility or accommodation | |

## 4. Confidentiality and ethics

- [ ] NDA, research notice, participant consent, recording consent, and withdrawal route identified.
- [ ] Personal, workforce, health, legal, financial, customer, trade-secret, security, and critical-infrastructure classes identified.
- [ ] Participants understand research purpose, optionality, permitted use, and retention.
- [ ] No coercive participation, hidden recording, deceptive observer role, or performance evaluation.
- [ ] Conflict of interest, sponsor influence, and vulnerable-participant considerations disclosed.
- [ ] Publication/redaction review owner and escalation route recorded.

| Field | Value |
|-------|-------|
| Confidentiality agreement / basis | |
| Participant notice / consent basis | |
| Prohibited content | |
| Redaction reviewer | |
| Withdrawal / correction route | |

## 5. Accounts and system access

Use least privilege, named accounts, and time-bounded access. Capture permission is not product Permission.

| System / area | Owner | Access mode | Allowed actions | Prohibited actions | Grant time | Expiry | Audit source |
|---------------|-------|-------------|-----------------|--------------------|------------|--------|--------------|
| | | read-only / supervised export / escorted observation | | | | | |

- [ ] No shared credentials, copied secrets, privilege escalation, active probing, or bypass.
- [ ] MFA/device/network prerequisites and support route are confirmed without recording secrets.
- [ ] Test/non-production versus production boundary is explicit.
- [ ] Export/download/screenshot permissions are separately approved.
- [ ] Access revocation and session termination are testable.
- [ ] Tooling cannot mutate production unless separately authorized outside Research; Research capture defaults to no mutation.

## 6. Time window and schedule

| Field | Value |
|-------|-------|
| Authorized start/end + timezone | |
| Arrival / induction slot | |
| Observation blocks | |
| System/export windows | |
| Blackout / change-free periods | |
| Departure / access-revocation deadline | |
| Collection clock source / known skew | |

Access outside the approved window is forbidden. A delayed or interrupted session does not justify extending access without re-approval.

## 7. Data minimization plan

For each proposed field, explain why it is necessary and how a less sensitive substitute was considered.

| Data / artifact category | Research necessity | Minimum fields / sample | Excluded fields | Collection method | Store / handle | Retention / deletion |
|--------------------------|--------------------|-------------------------|-----------------|-------------------|----------------|----------------------|
| | | | | | | |

- [ ] Prefer counts, extracts, redacted views, and controlled handles over raw datasets.
- [ ] Do not collect credentials, secret keys, unrelated personal data, or unrestricted tenant payloads.
- [ ] Sampling, filtering, transformation, and redaction are documented.
- [ ] Raw restricted artifacts stay in the authorized source store.
- [ ] Repository Markdown contains only safe metadata and non-secret handles.

## 8. Artifact and device handling

- [ ] Allowed research devices, storage media, applications, network paths, and note-taking methods identified.
- [ ] Artifact IDs and source-system/export identifiers assigned at collection.
- [ ] Integrity method (hash, export ID, immutable version, or justified alternative) agreed.
- [ ] Chain of custody records producer, collector, custodian, transfers, and access.
- [ ] Encryption, backup, retention, expiry, deletion, and legal-hold conflicts addressed.
- [ ] Registrar can resolve controlled handles under an approved retrieval route.

## 9. Observation boundaries

Record RP-specific target observations and non-observations before entry.

| Target observation | Permitted source | Observer method | Stop / exclusion rule |
|--------------------|------------------|-----------------|-----------------------|
| | | | |

Research personnel must not operate equipment, approve business decisions, issue commands, change configuration, impersonate users, accept on behalf, or turn observations into permissions/grants.

## 10. Entry, in-session, and exit checklist

### Before entry

- [ ] Required approvals, real participants, window, training, accounts, and handling controls verified.
- [ ] Field kit and blank LC form prepared; no observer/result pre-filled.
- [ ] Synthetic rehearsal artifacts are separated and visibly labeled T1.

### During observation

- [ ] Confirm timestamp, system/context/version, and source for every material observation.
- [ ] Separate direct observation, participant statement, researcher inference, and unresolved conflict.
- [ ] Reconfirm consent before recording or expanding scope.
- [ ] Stop immediately on safety, access, confidentiality, provenance, or scope failure.

### On exit

- [ ] Sign out, return badges/devices/media, terminate sessions, and revoke temporary access.
- [ ] Reconcile artifact manifest against collected items; quarantine unauthorized material.
- [ ] Confirm restricted material store, custodian, retention, and registrar retrieval.
- [ ] Record deviations, incidents, consent withdrawals, missing artifacts, and follow-up needs.

## 11. Hard stop conditions

Stop and do not improvise if:

1. Required access, consent, escort, training, or accountable owner is missing/revoked.
2. Safety, security, legal, confidentiality, or production continuity is at risk.
3. Requested action exceeds observation/read-only scope or would mutate a system/process.
4. Source identity, timestamp, provenance, or handling basis cannot be established.
5. Restricted material cannot be safely minimized, stored, transferred, or deleted.
6. A participant requests Complete, floor flip, Board Promote, Eng action, grant mint, Brain execute, Twin authorize, or Const/BP change from the visit.

## 12. Authorization record

| Decision | Name / controlled identity | Scope | Timestamp | Expiry | Conditions |
|----------|----------------------------|-------|-----------|--------|------------|
| Site/context access | | | | | |
| System/data access | | | | | |
| Recording/export | | | | | |
| Safety/security | | | | | |

**Access readiness:** Not ready / Ready for scheduled observation / Withdrawn  
**Open conditions:**  

This decision authorizes only the stated observation. It does not verify evidence, satisfy T2/T3, mark Complete, flip a readiness floor, Promote, open Eng work, or change Const/BP.
