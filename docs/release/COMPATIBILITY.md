# EAOS Compatibility Policy

**Baseline:** EAOS Phoenix Foundation `0.2.5`  
**Prior Foundation baseline:** `0.2.4`（PHX-G461；historical `0.2.3` / G404）  
**Milestone:** PHX-G509（0.2.5 release cut at tip `0092`）· **hygiene PHX-G510/G511**（V2.0 readiness only；≠ V2.0 cut）

## Rules

1. **Additive-only in minor releases** — new OpenAPI paths, optional fields, and error codes may be added.
2. **Breaking changes require major bump** — removing/renaming paths, making optional fields required, or changing error semantics.
3. **ExecutionContext** — clients must never supply authoritative `tenant_id` / `subject_id` / `platform_scope` / `session_id`; trusted gateway derives them.
4. **Marketplace commercial endpoints** — Foundation policy (ADR-0054) enables fixed pricing / immediate invoice / revenue share / publisher-tenant dispute; payment capture and external arbitration remain fail-closed.
5. **Alembic** — migrations are append-only; downgrade is supported for the current head only as documented.

## Supported matrix (Foundation)

| Consumer | Compatible with |
|----------|-----------------|
| `eaos_sdk` 0.2.x | Kernel / Shared / Runtime contracts in this repo |
| OpenAPI 3.1 contracts | HTTP adapters implementing the listed specs |
| PostgreSQL integration | Alembic head `0092_finance_realized_fx_gl_bridge_g372` |

## Versioning

- Package version follows SemVer.
- OpenAPI `info.version` may track capability slice versions independently but must not break consumers without a major bump.
- Patch `0.2.1` rolled accepted G18–G143 work into the published baseline without schema change.
- Patch `0.2.2`（PHX-G376） publishes the Foundation package at Alembic tip `0092_finance_realized_fx_gl_bridge_g372` without a new Alembic revision in the cut.
- Patch `0.2.3`（PHX-G404） republishes at the same tip `0092` after Marketplace economy shells（G400–G402）and Workflow multi-step narrow deepen（G403）；no Alembic revision in the cut.
- Patch `0.2.4`（PHX-G461） publishes Batches E→L at the same tip `0092`.
- Patch `0.2.5`（PHX-G509） publishes Batches M→T additive status and
  governance residuals at the same tip `0092`; production promotion remains
  NO-GO until the external evidence in `PRODUCTION_GO_DECISION_G469.md` is met.
- **Additive surfaces previously landed on package `0.2.1`（historical note；prior Alembic baseline `0029`）：**
  - PHX-G145 — WebAuthn/MFA thin product posture  
  - PHX-G146 — Role→grant thin product posture  
  - PHX-G147 — OIDC login product surface  
  - PHX-G148 — OpenAPI inventory product posture（T-0188 partial）  
  - PHX-G149 — Eng soft-queue tip hygiene（docs）  
  - PHX-G150 — Autonomous Execution Directive v1.1（docs）  
  - PHX-G151 — WebAuthn ceremony stub routes → 503（live mint still Held）  
  - PHX-G152 — AR Board Queue + Manifest milestone hygiene（docs）  
  - PHX-G153 — Ops / Compatibility / Checklist hygiene（docs）  
  - PHX-G154 — WebAuthn ceremony stub observability（503 `ceremony_step`）  
  - PHX-G155 — T2/T3 Evidence Readiness Board（docs；floors T1）  
  - PHX-G156 — Role→grant auto-write stub 503  
  - PHX-G157 — Ops / Checklist hygiene after G154–G156（docs）  
  - PHX-G158 — Autonomous Soft-Queue Natural Pause（docs）  
  - PHX-G159 — Generation-1 AR Board Hold×10（docs；≠ Eng ingest）  
  - PHX-G160 — WebAuthn env-gated challenge-bound live mint（default OFF → 503；`EAOS_WEBAUTHN_REGISTRATION_ENABLED` + RP；`attestation_crypto_verified=false`）  
  - PHX-G161 — Role→grant env-gated live mint（default OFF → 503；`EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED`；Cap≠grant）  
  - PHX-G162 — Marketplace payment clearing env-gated internal record（default OFF；≠ external PSP）  
  - PHX-G163 — T2/T3 Evidence Intake（docs；0 Complete）  
  - PHX-G164 — OpenAPI semantic deepen（mount complete；semantic partial）  

Clients must treat WebAuthn registration ceremony as **fail-closed 503 by default**；live mint only when `EAOS_WEBAUTHN_REGISTRATION_ENABLED=true` and RP_ID/ORIGIN are configured（PHX-G160）；packed/TPM attestation crypto remains deferred.  
Clients must treat Role→grant auto-write as **fail-closed 503 by default**；live mint only when `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED=true` and the role grant map is configured（PHX-G161）.
