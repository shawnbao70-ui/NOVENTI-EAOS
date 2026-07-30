# Terminal Sample / Order Demo Gap Review

**Template ID:** NRI-TPL-TERMINAL-DEMO-GAP  
**Version:** 1.0  
**Status:** Research comparison template — not a product opening  
**Last Updated:** 2026-07-23  
**Governing:** [TERMINAL_SCENARIO_CARD.md](TERMINAL_SCENARIO_CARD.md) · [COMMERCIAL_CHAIN_OBSERVATION.md](COMMERCIAL_CHAIN_OBSERVATION.md) · [EAOS_REWRITE_CANDIDATE.md](EAOS_REWRITE_CANDIDATE.md)

> Compare only what an existing Terminal sample/order demonstration can be evidenced to show. Unknown, undocumented, or unobserved behavior remains a knowledge gap. This template does not authorize changes to Smart Terminal or packages.

## 1. Review identity and evidence basis

| Field | Value |
|-------|-------|
| Review ID | `TDG-RP-00N-###` |
| Demo name/version/date | |
| Environment / mode | Synthetic / isolated / other |
| Demonstrator / observers | Real assigned identities only |
| Demo artifacts | Screenshots, recording, script, fixture IDs, logs |
| RP claims evaluated | |
| Product/code scope | Read-only evidence reference; no changes |

No artifact means “not evidenced,” not “implemented” or “absent.”

## 2. Classification of findings

| Classification | Meaning |
|----------------|---------|
| **Demonstrated** | Reproduced in the named demo/version with artifact evidence |
| **Scripted assertion** | Mentioned in script/narration but not demonstrated |
| **Synthetic fixture only** | UI state exists only because a T1 fixture supplied it |
| **Knowledge gap** | Semantics, source, state, authority, exception, or evidence unclear |
| **Out of scope** | Not included in the observed demo |
| **Forbidden opening** | Would require unauthorized product/authority/Const/BP/Eng change |

Do not convert scripted assertions or fixture realism into live/product truth.

## 3. Existing surface inventory

| Surface / step | Demonstrated behavior | Artifact reference | Data mode | Role/intent | Evidence shown | User choice | Actual side effect | Classification |
|----------------|-----------------------|--------------------|-----------|-------------|----------------|-------------|--------------------|----------------|
| Sample list/detail | | | | | | | | |
| Sample request/state | | | | | | | | |
| Order list/detail | | | | | | | | |
| Order state/review | | | | | | | | |
| Cross-link/navigation | | | | | | | | |

If actual side effect cannot be independently evidenced, record Unknown—not None.

## 4. Sample knowledge gap

Assess:

- Sample identity, product/specification/version, owner, quantity, status, and lifecycle.
- Request/approval/availability, physical handling, return/disposition, and exception states.
- Customer/account context and data-minimization boundary.
- Source system, timestamps, provenance, freshness, and evidence drill-down.
- Relationship to quote/order without assuming conversion semantics.

| Gap ID | Demonstrated | Needed knowledge/evidence | Risk if assumed | Required live evidence | HARD HOLD |
|--------|--------------|---------------------------|-----------------|------------------------|-----------|
| S-01 | | | | | yes / no |

## 5. Order knowledge gap

Assess:

- Order identity, quote/contract basis, customer acceptance, lines, quantity, price/currency/tax, dates, terms, and versions.
- Draft/accepted/held/changed/cancelled/backordered/fulfilled/disputed states.
- Credit/compliance, approval, segregation, and authority boundaries.
- Shipment/receipt/invoice/payment links and partial/exception behavior.
- Source system, timestamps, provenance, freshness, and audit evidence.

| Gap ID | Demonstrated | Needed knowledge/evidence | Risk if assumed | Required live evidence | HARD HOLD |
|--------|--------------|---------------------------|-----------------|------------------------|-----------|
| O-01 | | | | | yes / no |

## 6. End-to-end chain coverage

| Stage | Demonstrated surface | Knowledge available | Missing semantics / event / authority | Required artifact | Forbidden opening |
|-------|----------------------|---------------------|---------------------------------------|-------------------|-------------------|
| Sample | | | | | |
| Quote | | | | | |
| Order | | | | | |
| Shipment | | | | | |
| Receipt | | | | | |
| Invoice | | | | | |
| Payment | | | | | |

A Sample/Order demonstration does not imply Quote, Shipment, Invoice, or Payment capability.

## 7. Role, intent, and authority gap

| Demo role | Observed intent | Evidence available | Choice shown | Required authority | Authority actually evidenced | Gap / HOLD |
|-----------|-----------------|--------------------|--------------|--------------------|-----------------------------|------------|
| | | | | | | |

Check:

1. Role label versus real authenticated identity.
2. Read versus propose/request versus review versus approve versus execute.
3. Tenant/site/context and segregation of duties.
4. Access denied/revoked/stale-permission states.
5. No Role/Title/Capability→grant inference.

## 8. State and event gap

| Concept | Demonstrated states | Missing states | Event/source evidence | Ordering/correction gap | HOLD |
|---------|---------------------|----------------|-----------------------|-------------------------|------|
| Sample | | | | | |
| Order | | | | | |

Required variants include missing/stale/conflicting data, access denied, duplicate, change, cancellation, partial state, dispute, degraded/offline, timeout, and supersession.

## 9. Evidence and explainability gap

Evaluate whether the demo shows:

- Source, version, timestamp/as-of, confidence, and classification.
- Direct versus derived versus statement/synthetic fixture.
- Contradiction, absent evidence, limitation, and falsifier.
- Custodian/retention/retrieval route.
- Why a state/insight is shown and what next gate remains.

Visual polish, static labels, or generated fixtures are not provenance.

## 10. Terminal UX gap

| UX dimension | Demonstrated evidence | Gap | Research question | Evaluation method |
|--------------|-----------------------|-----|-------------------|-------------------|
| Role intent clarity | | | | |
| Evidence traceability | | | | |
| HOLD recognition | | | | |
| Error/degraded recovery | | | | |
| Accessibility/language | | | | |
| Privacy/data minimization | | | | |
| High-impact gate clarity | | | | |

## 11. Forbidden openings

Do not infer or request:

1. Product API, route, component, persistence, schema, event, package, or source-code implementation.
2. Quote/order approval, shipment release, invoice posting, payment initiation/clearing, customer communication, or acceptance-on-behalf.
3. Role/Capability→grant, Brain execute, Twin authorize, hidden workflow commit, or production tool access.
4. Constitution/Blueprint/knowledge rewrite, Architecture Promote, ADR acceptance, Eng queue/task, or release.
5. Live T2/T3 or Complete from synthetic demo fixtures, screenshots, interviews, or scripts.

## 12. Demo-fence checklist

- [ ] Persistent “Research demo — not production” label.
- [ ] Synthetic T1 fixtures identified and separated from live references.
- [ ] No production credentials, tenant payloads, customer/bank/payment secrets, or restricted data.
- [ ] No network/API path capable of production mutation.
- [ ] Actions are simulated/read-only with deterministic reset.
- [ ] Logs omit sensitive payloads and record scenario/evidence IDs.
- [ ] Missing evidence yields HOLD/unknown rather than fabricated state.

## 13. Gap disposition

| Gap | Research priority | Required evidence | Candidate note | Owner role | Status |
|-----|-------------------|-------------------|----------------|------------|--------|
| | | | | | Open |

Allowed disposition: retain gap, refine research card, request authorized live evidence, or reject candidate. No gap row becomes an Eng task from this template.

**Invariant:** demonstrated UI ≠ established knowledge ≠ live evidence ≠ product opening. This review cannot mark Complete, flip a floor, Promote, open Eng work, modify Smart Terminal/packages, rewrite Const/BP/knowledge, or authorize Brain/Twin.
