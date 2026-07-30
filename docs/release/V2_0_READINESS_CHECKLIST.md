# V2.0 Readiness Checklist（PHX-G506 refresh）

**Foundation baseline:** `0.2.5`（PHX-G509）  
**Alembic tip:** `0092_finance_realized_fx_gl_bridge_g372`  
**Status:** Readiness board only — **does not** cut or publish V2.0.

This checklist records what Foundation `0.2.5` already holds for a future
major train, and what remains deliberately deferred. It is not an Eng ticket
generator and does not authorize V2.0 implementation.

---

## Ready (held at Foundation 0.2.5)

- [x] Contiguous ladder through Batches A–D（G382–G405）at tip `0092` / package `0.2.3`
- [x] Remediation G406–G415 → RC CONDITIONAL GO；`FINAL STOP TRACK-G415`
- [x] Batch E RC HOLD closeout（G416–G421）：PG `integration_critical` green；Docker CI-path；REPAIR FREEZE lifted
- [x] Batch F integration tip / suite truth（G422–G427）
- [x] Batch G Finance deepen（G428–G433）：GL/period / party balance / treasury status；`bank_file_import=deferred`；PSP default off
- [x] Batch H Workflow deepen（G434–G439）：escalation fail-closed；compensation/SLA invent=false
- [x] Batch I OpenAPI semantic remainder honesty（G440–G445）：`full_openapi_http_complete=false` + `semantic_remainder_honest=true`
- [x] Batch J Knowledge + Twin/Brain advisory（G446–G451）：sample-pack ≠ complete evidence；execute/authorize commercial auto-write closed
- [x] Batch K Ops/Tenant/Observability（G452–G457）
- [x] Batch L Foundation `0.2.4` cut + **FINAL STOP TRACK-G463**
- [x] Batch M production evidence decision（G464–G469）：honest **NO-GO** pending human/CI/PG evidence
- [x] Batch N Identity/Auth residual（G470–G475）：secrets hidden；PKCE S256；attestation crypto false；Role→grant default OFF
- [x] Batch O CRM/commercial residual（G476–G481）
- [x] Batch P Purchase/Inventory posture（G482–G487）
- [x] Batch Q Marketplace residual（G488–G493）：external commercial services fail closed
- [x] Batch R Event/Outbox/Audit residual（G494–G499）：on-demand；no multi-region failover claim
- [x] Batch S Terminal/Plugin residual（G500–G505）：no signature bypass / sandbox escape
- [x] Batch T Foundation `0.2.5` cut + **FINAL STOP TRACK-G511**
- [x] Explicit non-goals still documented：external PSP capture、multi-region SaaS、public registry、Industry host-install

## Deferred / fail-closed (must stay OFF until separate PO auth)

- [ ] External PSP payment capture / settlement rail live invent
- [ ] `ENABLE_*_NETWORK` / `ENABLE_PSP_NETWORK` / `ENABLE_TAX_NETWORK` production default ON
- [ ] Bank file import / treasury bank statement ingest
- [ ] Marketplace external arbitration API / third-party arbiter
- [ ] Industry package host install runtime
- [ ] Brain execute / Twin authorize commercial auto-write
- [ ] Full OpenAPI semantic parity（mount complete；semantic still partial）
- [ ] WebAuthn attestation crypto verify；always-on Role→grant / payment clearing / WebAuthn mint
- [ ] Unconditional production GO without human branch-protection click + CI `docker-smoke` history

## V2.0 cut gate（future — not authorized here）

- [ ] Separate PO auth for major version train
- [ ] Compatibility / migration notes for any intentional breaking surface
- [ ] Release Manifest `version` major bump + Acceptance seven-step for that train
- [ ] Explicit revisit of deferred items above（each requires its own gate）

---

**PHX-G506 note:** Refreshing this checklist at tip `0092` / package `0.2.5`
records readiness evidence. It does **not** open V2.0 implementation.
Historical Foundation `0.2.4` and `0.2.3` evidence remains valid.
