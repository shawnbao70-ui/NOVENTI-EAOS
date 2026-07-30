# API Contracts

Versioned transport contracts only. Implementations, routers and authentication providers are separate milestones.

## Phoenix Foundation inventory (PHX-R17 · PHX-G131)

- [`identity.openapi.yaml`](identity.openapi.yaml) — Identity
- [`organization.openapi.yaml`](organization.openapi.yaml) — Organization
- [`permission.openapi.yaml`](permission.openapi.yaml) — Permission（含 roles list G136 + Role→grant product posture G146；auto-write 仍 deferred）
- [`workflow.openapi.yaml`](workflow.openapi.yaml) — Workflow
- [`knowledge.openapi.yaml`](knowledge.openapi.yaml) — Knowledge
- [`event.openapi.yaml`](event.openapi.yaml) — Event Delivery / Outbox
- [`ai.openapi.yaml`](ai.openapi.yaml) — AI Runtime
- [`terminal.openapi.yaml`](terminal.openapi.yaml) — Smart Terminal
- [`package.openapi.yaml`](package.openapi.yaml) — Package Platform
- [`brain.openapi.yaml`](brain.openapi.yaml) — Enterprise Brain & Twin
- [`marketplace.openapi.yaml`](marketplace.openapi.yaml) — Marketplace（技术 acquire + Foundation 商业 pricing/invoice/dispute/revenue-share；支付清算 / 外部仲裁仍 fail-closed）
- [`auth.openapi.yaml`](auth.openapi.yaml) — Auth status + OIDC login/session + MFA enrollment redirect + OIDC login product posture（PHX-G147）+ WebAuthn/MFA product posture（PHX-G131–G134 / G145；registration ceremony 仍 deferred）
- [`platform.openapi.yaml`](platform.openapi.yaml) — Platform roles + IdP registry/federation（PHX-G135；≠ Role→grant auto-write）
- [`ops.openapi.yaml`](ops.openapi.yaml) — Gateway meta/ops（health/release/adapters/context；PHX-G139；adapters meta OpenAPI inventory product posture PHX-G148/G164；mount parity complete；semantic 仍 deferred）

Foundation Auth / Platform / Ops OpenAPI 已入目录（Manifest 14）；Eng `2`/`3` thin posture delivered（PHX-G145/G146）；OIDC login product surface delivered（PHX-G147 / T-0189）；OpenAPI inventory posture delivered（PHX-G148）；OpenAPI semantic deepen delivered（PHX-G164 / T-0188 mount complete；semantic still partial）；full WebAuthn ceremony / full semantic / external PSP 另批。

Security-sensitive `ExecutionContext` fields are derived by the trusted authentication boundary and must not be accepted from client input.

See also: [`../release/RELEASE_MANIFEST.yaml`](../release/RELEASE_MANIFEST.yaml) and `api.adapters` registry.
