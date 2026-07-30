# Future Terminal Scenario Card

**Template ID:** NRI-TPL-TERMINAL-SCENARIO  
**Version:** 1.0  
**Status:** Research demonstration design — not a product opening  
**Last Updated:** 2026-07-23  
**Governing:** [COMMERCIAL_CHAIN_OBSERVATION.md](COMMERCIAL_CHAIN_OBSERVATION.md) · [LIVE_VS_SYNTHETIC_FENCE.md](LIVE_VS_SYNTHETIC_FENCE.md) · [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md)

> A scenario card describes a possible future Terminal experience for research discussion or a fenced demonstration. It is not a UI requirement, API contract, implementation request, Blueprint/Constitution change, Promote decision, or Eng opening.

## 1. Card identity

| Field | Value |
|-------|-------|
| Scenario ID | `TSC-RP-00N-###` |
| RP / research claim | |
| Title / one-line outcome | |
| Mode | Synthetic T1 demo / live-context observation reference |
| Scenario status | Draft / Reviewed / Retired |
| Source evidence IDs | |
| Owner / reviewers | Real assigned identities only |
| Version / date | |

## 2. Role and context

| Dimension | Description |
|-----------|-------------|
| Primary role | Role class; not an identity or grant |
| Supporting roles | |
| Accountable decision role | |
| Site / tenant / device context | |
| Trigger / precondition | |
| Time pressure / operational state | |
| Data available / unavailable | |
| Accessibility / language / device constraints | |

Role labels never mint Permission or authority.

## 3. Intent and non-intent

| Field | Description |
|-------|-------------|
| User intent | What the role is trying to understand/prepare/review |
| Research intent | Which hypothesis or usability question is tested |
| Success signal | Observable, non-product claim |
| Explicit non-intents | Actions/decisions/system changes not performed |

## 4. Evidence prerequisites

Before showing any state, list:

- Source artifact IDs, system/event versions, and timestamps.
- Whether evidence is synthetic T1 or verified live-context reference.
- Provenance, confidence, contradictions, freshness, and gaps.
- Data classification/redaction and authorized display context.
- Custodian/retrieval route and retention.

No invented “live” dashboard values. Synthetic values must be visibly fenced.

## 5. Scenario flow

| Step | Role intent | Terminal state / information | Evidence shown | User choice | System side effect | Boundary / next gate |
|------|-------------|------------------------------|----------------|-------------|--------------------|----------------------|
| 1 | | | | | None in research demo | |

For research cards, side effect defaults to **None**. Simulated transitions are labeled and do not call production.

## 6. High-impact gates

Identify every state involving commercial commitment, shipment, payment, workforce, safety, identity, permission, legal duty, external communication, or production change.

| Gate ID | High-impact transition | Required accountable role | Required evidence | Approval / separation | Fail-closed state | Audit point |
|---------|------------------------|---------------------------|-------------------|-----------------------|-------------------|-------------|
| G-01 | | | | | HOLD / read-only | |

Hard defaults:

1. Terminal never grants authority from role/title/capability/recommendation.
2. Brain advice never executes; Twin context never authorizes.
3. Accept/review in a research demo is not business acceptance, order approval, shipment release, invoice posting, or payment.
4. Missing/stale/conflicting evidence yields HOLD, not optimistic progression.
5. Identity, Permission, Workflow, safety, legal, and financial controls remain external accountable gates.

## 7. Evidence points and explainability

| Evidence point | Claim supported/challenged | Source/version/time | Direct / derived / statement | Confidence | Contradiction / gap | Drill-down limit |
|----------------|----------------------------|---------------------|------------------------------|------------|---------------------|------------------|
| E-01 | | | | | | |

The scenario must show “why,” “from where,” “as of when,” and “what is missing” without exposing restricted content.

## 8. States and variants

Design at least:

- Normal/read-only review.
- Missing evidence.
- Stale evidence.
- Contradictory evidence.
- Access denied/insufficient permission.
- Degraded/offline system.
- Exception/dispute/HOLD.
- Cancellation/withdrawal/timeout.

Do not design only a sponsor-selected happy path.

## 9. Safety, privacy, and data minimization

- Show only fields necessary for the role’s intent.
- Mask/tokenize customer, worker, site, financial, bank, product-sensitive, and security data.
- Prevent screenshots/exports where the approved context forbids them.
- Provide clear source/classification/freshness labels.
- Preserve accessibility, language, cognitive-load, and high-stress operational constraints.
- Avoid dark patterns, implied consent, false urgency, or automation bias.

## 10. Demonstration controls

| Control | Required posture |
|---------|------------------|
| Data | Synthetic fixtures or explicitly authorized redacted references |
| Connectivity | Isolated/no production mutation |
| Accounts | Demo identities with no production grants |
| Actions | Simulated/read-only |
| Logging | Scenario events, no secret/personal payload |
| Reset | Deterministic reset and fixture disposal |
| Label | Persistent “Research demo — not production” |

## 11. Evaluation plan

| Question | Method | Participant role | Observable measure | Evidence recorded | Stop criterion |
|----------|--------|------------------|--------------------|-------------------|----------------|
| | Walkthrough / think-aloud / comparison | | | | |

Capture comprehension, evidence traceability, HOLD recognition, error recovery, accessibility, workload, and boundary understanding—not product conversion metrics.

## 12. Findings and disposition

| Field | Value |
|-------|-------|
| Supported hypotheses | |
| Challenged hypotheses | |
| Boundary failures | |
| Missing evidence / roles | |
| Bias / limitations | |
| Follow-up research | |
| Card disposition | Revise / retain as research asset / retire |

**Non-claim:** Completing or demonstrating this card is not live evidence Complete, product acceptance, feature authorization, Architecture Promote, Eng invent, Brain execute, Twin authorize, grant mint, or Const/BP change.
