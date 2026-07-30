# Live Evidence Interview Protocol

**Template ID:** NRI-TPL-INTERVIEW  
**Version:** 1.0  
**Status:** Interview preparation/recording standard — interview alone ≠ Complete  
**Last Updated:** 2026-07-23  
**Governing:** [SITE_ACCESS_PACK.md](SITE_ACCESS_PACK.md) · [DATA_MINIMIZATION_PACK.md](DATA_MINIMIZATION_PACK.md) · [CHAIN_OF_CUSTODY.md](CHAIN_OF_CUSTODY.md) · [OBSERVATION_LOG.md](OBSERVATION_LOG.md) · [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md)

> Interviews can explain context, decisions, exceptions, and source locations. They do not replace dated operational artifacts, system evidence, provenance, or registrar verification. Interview evidence alone cannot mark Complete.

## 1. Interview identity

| Field | Required value |
|-------|----------------|
| Interview ID | `INT-LC-YYYYMMDD-RP-00N-##` |
| Proposed LC ID / RP / tier | |
| Mode | live interview / follow-up |
| Named context | Site, tenant, cohort, system, process |
| Research purpose | |
| Interviewer / note taker | Real assigned identities only |
| Participant role | Role and relevance; name held only where required |
| Scheduled window / timezone | |
| Recording mode | None / notes / audio / video / transcript |

## 2. Recruitment and role selection

- Select roles because they directly observe, operate, govern, own, audit, or are affected by the in-scope process.
- Include differing perspectives and avoid sponsor-only or management-only sampling.
- Do not recruit through coercion, performance-management channels, or implied employment consequences.
- Record inclusion/exclusion logic, sampling limits, conflicts of interest, and missing perspectives.
- Never invent participants, statements, attendance, affiliation, or authority.

## 3. Informed consent essentials

Before questions begin, explain and record:

1. Research purpose, sponsoring program, and why the participant’s role was invited.
2. Voluntary participation and the right to skip questions, pause, withdraw, or request correction.
3. What will be recorded, how quotes/notes will be attributed or de-identified, and who can access them.
4. Expected duration, sensitive topics, foreseeable risks, and any compensation/none.
5. Data minimization, storage, custody, retention, destruction, and legal-hold exceptions.
6. Limits to confidentiality, including safety/security/legal reporting obligations.
7. The distinction between interview statements, verified artifacts, researcher inference, and policy/authorization.
8. Contact route for questions, withdrawal, correction, complaint, or data request.

| Consent item | Method / version | Confirmed by | Timestamp | Limits / withdrawal |
|--------------|------------------|--------------|-----------|---------------------|
| Participation | | | | |
| Notes | | | | |
| Audio/video, if any | | | | |
| Quote attribution | | | | |
| Follow-up | | | | |

Consent to an interview does not imply consent to every recording/export or secondary use.

## 4. Interview guide structure

Use a semi-structured sequence:

1. **Opening/context:** role, scope, time in context, systems/processes directly known.
2. **Concrete recent example:** ask for a dated event/workflow/decision, not general opinion first.
3. **Normal path:** actors, systems, inputs, outputs, controls, and evidence generated.
4. **Exceptions/failure:** deviations, workarounds, escalation, HOLD/stop, and recovery.
5. **Authority/boundaries:** who may observe, decide, approve, execute, and audit.
6. **Artifacts/provenance:** where supporting records live, owner, versions, access, and retention.
7. **Counter-evidence:** what would disprove the participant’s account or change the conclusion.
8. **Close/member check:** summarize, invite correction/dissent, identify follow-up artifacts and missing roles.

## 5. Question design rules

Preferred questions:

- Open, neutral, single-focus, role-appropriate, and tied to observable events.
- “Walk me through the last time…” before “Do you usually…”
- Ask for source location/owner and uncertainty without demanding restricted content.
- Separate what the participant directly observed from what they inferred or heard.
- Probe variation by time, site, cohort, system version, exception, and risk.
- Ask about adverse outcomes, failed controls, disagreement, and should-HOLD cases.

Avoid:

- Leading/loaded questions that contain the desired answer.
- Compound questions, jargon tests, blame framing, or requests for speculation outside role.
- Requests for secrets, credentials, unnecessary personal data, privileged advice, or prohibited operational details.
- Promises of anonymity/confidentiality beyond approved controls.
- Asking participants to approve architecture, Promote, open Eng work, mint grants, execute actions, or rewrite Const/BP.

## 6. Timebox

| Block | Suggested time | Purpose |
|-------|----------------|---------|
| Consent / boundaries | 5–10 min | Confirm voluntariness and recording |
| Context / recent example | 10 min | Establish direct knowledge |
| Core questions | 25–40 min | Normal path, exceptions, artifacts |
| Counter-evidence / gaps | 10 min | Falsifiers and uncertainty |
| Summary / member check | 5–10 min | Corrections and follow-up |

Default maximum is 60–80 minutes unless a longer session is explicitly consented. Stop on fatigue, distress, operational interruption, or consent change.

## 7. Recording and note standards

Every note segment records:

- Interview ID, UTC/local timestamp, speaker role/token, question ID, and recording/note source.
- Evidence type: direct observation, participant statement, quoted source, hearsay, researcher inference, or unresolved.
- Exact quote versus paraphrase; translations and transcription/OCR tools/versions.
- Referenced system, event date/window, artifact owner/location, and proposed artifact ID.
- Confidence, contradiction, missing context, follow-up, and potential falsifier.
- Consent/redaction restriction for that segment.

Do not silently “clean up” meaning. Corrections are append-only with who/when/why.

## 8. Attribution and de-identification

| Attribution level | Use |
|-------------------|-----|
| Named | Required and explicitly consented; restricted access |
| Role-attributed | Role is analytically necessary and re-identification risk accepted |
| Tokenized | Participant code held separately by custodian |
| Aggregated | Individual identity not necessary |
| Not quotable | Context only; do not publish or attribute |

Small cohorts and unique roles may remain identifiable after removing names; document residual risk and minimize detail.

## 9. Bias and quality controls

- Pre-register role sampling, core questions, and expected evidence before interviews.
- Record interviewer assumptions, sponsor relationship, prior knowledge, and desired-outcome risk.
- Use consistent core questions while allowing role-specific probes.
- Seek disconfirming roles/examples and record refusals/nonresponse without inference.
- Compare statements with operational artifacts; do not count repeated hearsay as corroboration.
- Conduct member check without pressuring agreement.
- Preserve dissenting accounts and explain reconciliation or unresolved conflict.

## 10. Sensitive disclosure and stop rules

Pause/stop if a participant:

1. Withdraws/limits consent or shows distress/fatigue.
2. Reveals credentials, secrets, unnecessary personal data, security vulnerabilities, privileged material, or out-of-scope content.
3. Reports immediate safety/security/legal risk requiring approved escalation.
4. Is asked by another party to approve, execute, or retaliate within the interview.
5. Cannot distinguish direct knowledge from speculation on a material claim.

Record only minimum incident metadata; follow site/custody procedures.

## 11. Handoff and evidence mapping

| Question / statement ID | Claim supported/challenged | Artifact referenced | Source owner | Follow-up status | Evidence class |
|-------------------------|----------------------------|---------------------|--------------|------------------|----------------|
| | | | | | Statement / artifact / inference |

After the interview:

1. Reconcile notes/recording, consent limits, participant token, and custody log.
2. Redact/minimize before repository reference; raw recordings remain controlled.
3. Send member-check summary where consented and log corrections.
4. Request supporting artifacts through authorized channels rather than accepting uncontrolled copies.
5. Record unresolved contradictions, missing roles, and falsifiers in the observation log/capture form.
6. Dispose recordings/working notes according to the approved schedule.

## 12. Interview outcome

| Field | Value |
|-------|-------|
| Conducted / stopped / withdrawn | |
| Consent status | |
| Directly supported claims | |
| Challenged claims | |
| Artifact follow-ups | |
| Missing perspectives | |
| Bias/limitations | |
| Custody references | |

**Invariant:** interview completed ≠ artifact accepted ≠ T2/T3 verified ≠ Registry Complete. No interview can by itself flip a floor, Promote, open Eng work, authorize Brain/Twin/grants, or change Const/BP.
