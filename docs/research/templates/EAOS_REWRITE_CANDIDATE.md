# EAOS Rewrite Candidate Note

**Template ID:** NRI-TPL-EAOS-REWRITE-CANDIDATE  
**Version:** 1.0  
**Status:** Research translation candidate — not Eng invent and not Promote  
**Last Updated:** 2026-07-23  
**Governing:** [COMMERCIAL_CHAIN_OBSERVATION.md](COMMERCIAL_CHAIN_OBSERVATION.md) · [TERMINAL_SCENARIO_CARD.md](TERMINAL_SCENARIO_CARD.md) · [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md)

> This note translates observed Legacy knowledge into a bounded EAOS research candidate. It does not modify Legacy knowledge, Constitution, Blueprint, product code, Smart Terminal packages, schemas, APIs, ADRs, or queues. Candidate ≠ architecture truth ≠ Promote ≠ Eng invent.

## 1. Candidate identity

| Field | Value |
|-------|-------|
| Candidate ID | `RWC-RP-00N-###` |
| RP / research claim | |
| Legacy source scope | Controlled handles only |
| Commercial-chain stages | |
| Proposed EAOS capability boundary | |
| Evidence status | Missing / synthetic T1 / live candidate |
| Author / reviewers | Real assigned identities only |
| Version / date | |

## 2. Legacy knowledge boundary

Document without rewriting the source:

| Legacy concept / term | Source/version/owner | Observed meaning | Known variants | Hidden assumptions | Confidence / gap |
|-----------------------|----------------------|------------------|----------------|--------------------|------------------|
| | | | | | |

Rules:

1. Preserve original source/version and terminology in controlled custody.
2. Separate observed semantics from interview statements and researcher interpretation.
3. Do not “normalize” contradictions away.
4. Do not edit `docs/knowledge/**` or represent this note as replacement knowledge.
5. Use tokenized/redacted references for restricted customer, workforce, financial, payment, OT, or security content.

## 3. Problem and outcome framing

| Field | Description |
|-------|-------------|
| Current Legacy outcome | |
| Friction / risk / evidence gap | |
| Actors affected | Role classes only |
| Desired governed outcome | |
| Explicit non-outcomes | |
| Falsifier | What evidence would reject the candidate |

Avoid feature-first framing. A candidate must explain why an enterprise capability boundary is needed and what must remain outside it.

## 4. Capability boundary

| Dimension | Candidate statement |
|-----------|---------------------|
| Capability name / outcome | |
| Inputs / outputs | |
| In-scope rules | |
| Out-of-scope rules | |
| Accountable owner class | |
| Upstream/downstream dependencies | |
| Failure / degraded behavior | |
| Audit / provenance requirement | |

Constraints:

- Capability≠Organization, Role, Permission, workflow approval, product screen, or package.
- A capability description cannot mint grants or execution authority.
- Brain may advise; Twin may provide context; neither authorizes.
- Commercial commitments, shipment release, invoicing, payment, workforce, safety, and external communication remain high-impact governed transitions.

## 5. Information and invariant candidates

| Candidate concept | Identity / key | State / lifecycle | Invariants | Source evidence | Open questions |
|-------------------|----------------|-------------------|------------|-----------------|----------------|
| | | | | | |

This is conceptual research only. Do not prescribe database schema, Kernel ownership, API payloads, or migration scripts.

## 6. Event candidates

| Event candidate | Trigger / prior state | Minimum payload | Producer class | Consumer class | Ordering/idempotency concern | Audit evidence |
|-----------------|-----------------------|-----------------|----------------|----------------|------------------------------|----------------|
| | | | | | | |

Event rules:

1. Describe observed business fact or proposed semantic boundary, not a command disguised as an event.
2. Distinguish intent/request, approval, committed fact, correction, cancellation, and observation.
3. Include source/version/time/correlation and data-minimization requirements.
4. Do not invent production topic names, integrations, APIs, or delivery guarantees.
5. Missing live event evidence remains a gap and cannot be filled by synthetic naming.

## 7. Permission and authority candidates

| Transition / information | Read evidence needed | Propose/request | Review/challenge | Approve/commit | Execute/release | Audit |
|--------------------------|----------------------|-----------------|------------------|----------------|-----------------|-------|
| | | | | | | |

Record:

- Accountable role classes and segregation-of-duty needs.
- External legal/safety/financial/workflow controls.
- Least-privilege and tenant/site context.
- Denied, stale, conflicting, and revoked-access behavior.
- Explicit prohibition on Role/Title/Capability→grant.

This section maps research questions; it does not grant Permission or change authorization design.

## 8. Terminal surface candidate

| Surface element | Role intent | Evidence displayed | User choice | High-impact gate | Fail-closed/HOLD | Side effect in demo |
|-----------------|-------------|--------------------|-------------|------------------|------------------|---------------------|
| | | | | | | None |

Terminal rules:

1. Surface explains evidence, freshness, contradictions, and accountable next gate.
2. Research demo uses synthetic T1 or explicitly authorized redacted references.
3. Demo actions are simulated/read-only; “accept” is never business acceptance.
4. Do not specify product component, route, API, persistence, package, or code change.
5. Accessibility, language, degraded/offline, privacy, and data minimization are research requirements.

## 9. Commercial-chain trace

| Chain stage | Legacy evidence | Capability boundary | Event candidate | Authority gate | Terminal evidence point | Gap |
|-------------|-----------------|---------------------|-----------------|----------------|-------------------------|-----|
| Sample | | | | | | |
| Quote | | | | | | |
| Order | | | | | | |
| Shipment / receipt | | | | | | |
| Invoice | | | | | | |
| Payment / clearing | | | | | | |

Research must not create or alter any commercial record to populate this trace.

## 10. Rewrite/migration hypothesis

Describe a reversible knowledge translation path:

1. Inventory Legacy terms, rules, variants, source owners, and observed exceptions.
2. Map to candidate outcomes/capabilities/events/authority gates with unresolved conflicts visible.
3. Validate against live evidence from multiple roles/windows where required.
4. Compare candidate semantics to current governed EAOS boundaries without changing them.
5. Produce research findings, falsifiers, risks, and ownership questions for a future legal promotion path.

No implementation sequence, code task, package change, schema migration, or release plan belongs here.

## 11. Evidence requirements and gaps

| Claim / candidate | Required live evidence | Current state | Artifact/observer/site gap | Falsifier | Closure authority |
|-------------------|------------------------|---------------|----------------------------|-----------|-------------------|
| | | Open | | | Registrar/intake only |

Synthetic diagrams, interviews alone, demo cards, and Legacy documents alone cannot establish T2/T3 or Complete.

## 12. HARD HOLD review

- [ ] No product code, Smart Terminal package, database, API, or event implementation is requested.
- [ ] No Constitution/Blueprint/knowledge rewrite is performed.
- [ ] No Board Promote, ADR acceptance, Eng invent, queue entry, or payment clearing is implied.
- [ ] No Brain execute, Twin authorize, Role/Capability→grant, transaction action, or acceptance-on-behalf is opened.
- [ ] Candidate claims remain bounded by evidence status and falsifiers.

Any unchecked item keeps the candidate in HARD HOLD.

## 13. Research disposition

| Outcome | Meaning |
|---------|---------|
| Retain as gap | Evidence/ownership/boundary insufficient |
| Revise research candidate | Mapping needs correction or more evidence |
| Ready for separate research review | Research note coherent; still no Promote/Eng |
| Reject | Contradicted, unsafe, duplicative, or violates invariants |

**Disposition:**  
**Missing live evidence:**  
**Dissent / limitations:**  

**Invariant:** This template can produce only a research candidate. It cannot self-authorize Complete, readiness-floor change, Promote, Eng invent, product opening, Const/BP/knowledge rewrite, Brain execute, or Twin authorize.
