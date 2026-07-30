# api/

API surface for EAOS.

## Purpose

Host API definitions and service entrypoints. APIs consume Kernel and platform capabilities; they do not host business rules.

## PHX-R17 — Contract catalog

- Contract source of truth: `docs/api/*.openapi.yaml`（含 `auth` / `platform` / `ops`；PHX-G131–G139 / G145 thin WebAuthn posture / G151 ceremony stub 503 / G154 stub observability / **G160** WebAuthn env-gated live mint（`EAOS_WEBAUTHN_REGISTRATION_ENABLED` + RP；default 503；`attestation_crypto_verified=false`）/ G146 thin Role→grant posture / G156 Role→grant stub / G161 Role→grant env-gated live mint（`EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED`；default 503）/ G147 thin OIDC login product / G148 OpenAPI inventory posture / **G164** OpenAPI semantic deepen（mount parity complete；`full_openapi_http_complete=false`）；attestation crypto / full semantic 另批；Manifest 14 份）
- Adapter registry: `api/adapters` (catalog; not a business-rule host；`GET /v1/adapters` meta 含 `openapi_inventory_product`)

```python
from api.adapters import list_adapters
```

## PHX-G18 / G20 — Gateway

- Implementation: `api/gateway` (FastAPI)
- Install: `pip install -e ".[api]"` (or `.[dev,persistence,api]`)
- Trusted context: `Authorization: Bearer` JWT (HS256, G37) or development headers — bodies cannot override `tenant_id` / `platform_scope` / `roles`；JWT `eaos_roles` → `ExecutionContext.roles`（PHX-G82）
- JWT env: `EAOS_JWT_SECRET` (HS256) / `EAOS_JWT_JWKS_JSON` or `EAOS_JWT_JWKS_URL` (单 issuer RS256) / `EAOS_JWT_ISSUERS_JSON`（多发行方 JWKS，G45）/ `EAOS_JWT_DENYLIST_JSON` or `EAOS_JWT_DENYLIST_URL`（吊销列表，G46）/ `EAOS_JWT_ISSUER` / `EAOS_JWT_AUDIENCE` / `EAOS_ALLOW_DEV_CONTEXT_HEADERS` (default on) / `EAOS_REQUIRE_JWT` (default off)
- OIDC login (G40/G47/G48/G61/G63/G64/G65/G70/G74/G75/G79/G80/G81/G84/G85/G86/G87/G89/G145/G147/G151/G154/G160): `/v1/auth/oidc/status|login|callback|providers|mfa-enrollment`；status 含 `oidc_login_product` 只读姿态（authorization_code_enabled 来自配置；未配置 fail-closed）与 `webauthn_product` 只读姿态（default registration_enabled=false；G160 env-gated `POST /v1/auth/webauthn/register/options|verify` → challenge-bound mint when `EAOS_WEBAUTHN_REGISTRATION_ENABLED` + RP_ID/ORIGIN；default 503；`/auth/webauthn/register` ABSENT；`attestation_crypto_verified=false`）；可选 `POST /refresh` 与 `POST /logout`；可选 `EAOS_OIDC_REQUIRED_CLAIMS`（G79）、`REQUIRED_AMR`/`REQUIRED_ACR`（G80）、`AUTHORIZE_ACR_VALUES`/`AUTHORIZE_PROMPT` authorize step-up（G87）、`MFA_ENROLLMENT_URL` IdP 注册出口（G89）、`ROLE_CLAIM`+`ROLE_MAP`→JWT `eaos_roles`（G81，可选 `REQUIRE_MAPPED_ROLE`）、`LOGIN_PROVIDERS` 多 IdP 目录 + `login?provider=`（G84）+ JWT `eaos_oidc_login_provider` 驱动 per-provider refresh/logout（G85）+ 可选第 7 段 provider `end_session`（G86）；env `EAOS_OIDC_ISSUER` / `CLIENT_ID` / `CLIENT_SECRET` / `REDIRECT_URI`（及可选 authorize/token/scopes/default tenant/end_session/post_logout）；可选 Discovery/JWKS wire / refresh encrypt；未配置 → 503；Alembic `0026`
- IdP status (G55/G56): `GET /v1/auth/idp/status` 只读脱敏聚合（OIDC + JWT + registry）；端点 `writable=false`
- JWT status (G96): `GET /v1/auth/jwt/status` 只读脱敏（require_jwt / denylist 来源与条目数 / runtime revoke 计数；不下发 jti 列表）
- IdP registry (G56/G57/G60): 平台面 `GET/POST /v1/platform/idp/issuers`、`POST .../{id}/disable`、`POST .../discovery/sync`；`EAOS_IDP_REGISTRY_STORE=memory|sql`；可选 `EAOS_OIDC_DISCOVERY_REGISTRY_WRITE=1`（Discovery→注册表 upsert，不写 env）；env/wire 发行方优先；Alembic `0025`
- Tenant IdP federation (G66/G67/G68/G69/G77/G78): `GET /v1/platform/idp/federation/matrix`、`GET/POST .../tenants/{tenant_id}/bindings`、`POST .../bindings/{id}/unbind`、`POST .../bindings/{id}/priority`（越小越优先，默认 100）；Terminal Admin Matrix/List/Bind/Unbind/Set priority；可选 `EAOS_TENANT_IDP_FEDERATION=1`；`EAOS_TENANT_IDP_FEDERATION_STORE=memory|sql`；Alembic `0028`
- Foundation routes: `/v1/health`, `/v1/release`（含可选 `deploy_region`，PHX-G76）, `/v1/adapters`（meta 含 G148/G164 `openapi_inventory_product`；mount parity complete；semantic 仍 deferred）, `/v1/context`（含 `roles`，PHX-G82）, `/v1/context/echo`
- Identity surface (G20/G120–G121): `/v1/identity/status`；`/subjects`、`/credentials`、`/sessions`、`/sessions/{id}/validation`；Terminal Admin 运维面齐（G120–G121；session 以目标 subject 作 trusted header；secret 仅 vault ref）
- Organization surface (G21/G25/G32/G122–G127): `/v1/organization/status`；`/tenants/{id}`、`/enterprises`、`/organization-units`、`/memberships`；`/v1/platform/tenants*`；Terminal Admin 运维面齐（G122–G127；含 enterprise / platform tenant lifecycle）
- Permission surface (G22/G83/G88/G90/G93/G94/G95/G128/G129/G146/G156/G161): `/v1/permission/policies`, `/grants`, `/evaluations`, `/decisions/...`, `/principals/.../effective-permissions`, `/roles`（G88/G90 只读目录）、`/roles/status`（G93 脱敏摘要 + G146/G161 `role_grant_product`；`auto_grant_from_role_enabled` mirrors env）、`POST /role-grants`（G161 env-gated mint；default 503）；Terminal evaluate/effective（G94/G95）、policy/grant 手工写入（G128）与 deprecate/delegate（G129）；平台 `/v1/platform/roles`（G90，`EAOS_ROLE_CATALOG_STORE=memory|sql`）；可选 `EAOS_PERMISSION_ROLE_GRANT_MAP`（空=off）使 JWT/`ctx.roles` 参与 evaluate（`MATCHED_CONTEXT_ROLE`；deny 优先）并作为 G161 mint 前提；可选 `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED`（default false）；可选 `EAOS_ROLE_CATALOG` 声明角色
- Workflow surface (G23/G104–G107): `/v1/workflow/status`；`/definitions`、`/instances`、`/tasks`，approval/rejection，signal/cancel，compensation，task escalation；Terminal Admin 运维面齐（G104–G107）
- Knowledge surface (G24/G110–G112): `/v1/knowledge/status`；`/entities`（含 archive/share）、`/links`、`/search`、`/provenance/...`；Terminal Admin 运维面齐（G110–G112）
- Platform tenant lifecycle (G25): `/v1/platform/tenants`, `/platform/tenants/{id}/suspension`
- Event Bus surface (G26/E21/E22): `/v1/events`, `/outbox`, `/dispatch`, `/subscriptions`（可选 `delivery_url` + `signing_secret` HMAC）、`/stats`, `/dead-letters`, get/replay
- Package surface (G27/G108–G109): `/v1/packages/status`；`/manifests`、`/installations`、`/surfaces`、`/actions/resolve`；Terminal Admin 运维面齐（G108–G109）
- Twin & Brain surface (G28/G113–G116): `/v1/twin/status`；`/snapshots`、`/authorize`（执行路径恒 403）；Terminal Twin 运维面齐（G113–G114）；`/v1/brain/status`；`/insights`、`/execute`（执行路径恒 403）；Terminal Brain 运维面齐（G115–G116；execute fail-closed）
- AI Runtime surface (G29/G117–G119): `/v1/ai/status`；`/runs`、`/tools`、memory、approvals、commits；Terminal Admin 运维面齐（G117–G119；commit 无审批 fail-closed；`ai_employee` trusted header）
- Smart Terminal surface (G30): `/v1/terminal/sessions|intents|previews`（approval/commit）
- Domain completions (G31): Workflow signal/cancel/compensate/escalate/deprecate；Knowledge archive/share；Permission deprecate/delegate
- Organization completions (G32): Enterprise/Unit/Membership 生命周期扩展
- Marketplace (G34/M17/M18/G101/G141): Listing 生命周期 + acquire；Foundation 定价/发票/分成/争议（Terminal G141）；可选 HMAC/Ed25519 包签名（`EAOS_MARKETPLACE_SIGNING_*`）；`GET /v1/marketplace/status`（支付清算/外部仲裁/计量 fail-closed）；支付清算仍未实现
- Complete Terminal UI (G36/G39–G44/G62/G69/G91–G147): `GET /terminal/` 五表面壳；`/v1/terminal/extensions*` Extension Host（SQL + 首方 iframe/Worker + CSP + 可选验签）；`EAOS_EXTENSION_SIGNING_*`；OIDC Login Product 面板（G147；Auth Code CTA）→ Bearer；Admin IdP 注册表薄操作 + 租户联邦 List/Bind/Unbind（平台面；path 租户独立输入）+ 声明角色 List/Upsert/Disable（G91）+ 租户角色目录只读（G92）+ 角色状态探针（G93）+ permission evaluate/explain（G94）+ effective-permissions 只读探针（G95）+ permission policy/grant 手工写入（G128）+ deprecate/delegate（G129；≠ Role→grant auto-write）+ Role→grant 产品姿态（G146）+ MFA/WebAuthn 产品姿态（G145）+ JWT/denylist 状态探针（G96）+ Event Bus 完整薄运维（G97–G100）+ Marketplace 状态/listing Create·Get（G101）+ listing 生命周期（G102）+ 技术 acquire（G103；≠ 支付清算）+ Foundation 商业薄探针（G141；≠ 支付清算）+ Ops context echo / Workflow definition deprecate（G140）+ Workflow/Package/Knowledge/Twin/Brain/AI Runtime/Identity/Organization Terminal 运维面齐（G104–G127/G137–G138/G142；含 get enterprise 与 platform tenant lifecycle）
- Inject services: `create_app(..., marketplace_service=..., terminal_service=..., ...)`（默认 Terminal 共享 Workflow）

```bash
uvicorn api.gateway.app:app --reload
# Operator Shell: http://127.0.0.1:8000/terminal/
```

生产单主机拓扑与 Runbook：`docs/release/PRODUCTION_TOPOLOGY.md`、`docs/release/OPERATIONS_RUNBOOK.md`（PHX-G49）。  
Docker Compose 参考：`docs/release/COMPOSE.md`、`deploy/docker/compose.yaml`（PHX-G50）。  
Helm 参考：`docs/release/HELM.md`、`deploy/helm/eaos`（PHX-G51）。  
Ingress / TLS：`docs/release/INGRESS.md`（PHX-G52；默认关闭）。  
HPA：`docs/release/HPA.md`（PHX-G53；默认关闭）。  
VPA：`docs/release/VPA.md`（PHX-G54；默认关闭；与 HPA 互斥）。  
KEDA：`docs/release/KEDA.md`（PHX-G58；默认关闭；与 HPA/VPA 互斥）。  
Mesh：`docs/release/MESH.md`（PHX-G59；默认关闭；注入标签/注解，不装控制面）。
