# EAOS Operations Runbook — Phoenix Foundation

**Version:** 0.2.5  
**Milestones:** PHX-R17 · PHX-G49…G54 · PHX-G58/G59 · **PHX-G144**…**PHX-G164**  
**Prior Foundation baseline:** `0.2.1`（PHX-G144；historical `0.2.0` / PHX-R17）  
**Hygiene:** PHX-G153（foundation ops baseline）· PHX-G157（ops/checklist）；**WebAuthn live mint** PHX-G160（env-gated）；**Role→grant live mint** PHX-G161（env-gated）

## 1. Install

```bash
cd H:\Workspace\NOVENTI-EAOS
python -m pip install -e ".[dev,persistence,api]"
```

Production install may omit `dev`: `".[persistence,api]"`.

## 2. Migrate (PostgreSQL)

```bash
set EAOS_DATABASE_URL=postgresql+psycopg://...
alembic upgrade head
```

Expected head: `0092_finance_realized_fx_gl_bridge_g372`.
## 3. Verify

```bash
# PHX-G408 — required PR contracts (≤10 min budget；see docs/release/CONTRACT_SHARDS.md)
python scripts/run_contract_shard.py pr_required
# full contracts：nightly / parallel（publish DURATION_SECONDS；do not hide latency）
pytest tests/contracts
# optional dedicated destructive DB:
set EAOS_TEST_DATABASE_URL=postgresql+psycopg://...
pytest tests/integration
```

## 4. Production start (single-host)

Normative topology: [PRODUCTION_TOPOLOGY.md](PRODUCTION_TOPOLOGY.md) (PHX-G49 / ADR-0068).

```bash
set EAOS_DATABASE_URL=postgresql+psycopg://...
set EAOS_REQUIRE_JWT=1
set EAOS_ALLOW_DEV_CONTEXT_HEADERS=0
set EAOS_JWT_SECRET=...
set EAOS_JWT_ISSUER=https://eaos.example/issuer
set EAOS_JWT_AUDIENCE=eaos-api
rem optional deploy-region identity (PHX-G76; empty = unlabeled):
rem set EAOS_DEPLOY_REGION=ap-east-1
rem optional durable IdP registry (PHX-G57; default memory):
rem set EAOS_IDP_REGISTRY_STORE=sql
rem optional OIDC refresh encrypt at rest (PHX-G64; default off):
rem set EAOS_OIDC_REFRESH_ENCRYPT=1
rem set EAOS_OIDC_REFRESH_KEY_PROVIDER=env
rem set EAOS_OIDC_REFRESH_FERNET_KEY=...
rem optional file key provider (PHX-G74):
rem set EAOS_OIDC_REFRESH_KEY_PROVIDER=file
rem set EAOS_OIDC_REFRESH_FERNET_KEY_FILE=C:\secrets\oidc_fernet.key
rem set EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE=C:\secrets\oidc_fernet_previous.keys
rem optional KMS key provider (PHX-G75; pip install noventi-eaos[kms-aws|kms-gcp|kms-azure] as needed):
rem set EAOS_OIDC_REFRESH_KEY_PROVIDER=kms
rem set EAOS_OIDC_REFRESH_KMS_BACKEND=http
rem set EAOS_OIDC_REFRESH_KMS_HTTP_URL=https://secrets.example/oidc-fernet
rem set EAOS_OIDC_REFRESH_KMS_BACKEND=aws
rem set EAOS_OIDC_REFRESH_KMS_KEY_ID=alias/eaos-oidc
rem set EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64=...
rem optional previous Fernet keys for rotation window (PHX-G65; env provider):
rem set EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS=oldkey1,oldkey2
rem optional re-encrypt old ciphertext on get (PHX-G70; default off):
rem set EAOS_OIDC_REFRESH_REENCRYPT_ON_READ=1
rem optional OIDC required id_token claims (PHX-G79; empty = off):
rem set EAOS_OIDC_REQUIRED_CLAIMS=email,email_verified
rem optional OIDC amr/acr auth context (PHX-G80; empty = off):
rem set EAOS_OIDC_REQUIRED_AMR=mfa,otp
rem set EAOS_OIDC_REQUIRED_ACR=urn:mace:incommon:iap:silver
rem optional OIDC authorize step-up params (PHX-G87; empty = off):
rem set EAOS_OIDC_AUTHORIZE_ACR_VALUES=urn:mace:incommon:iap:silver
rem set EAOS_OIDC_AUTHORIZE_PROMPT=login
rem optional IdP MFA enrollment URL (PHX-G89; empty = off; https):
rem set EAOS_OIDC_MFA_ENROLLMENT_URL=https://idp.example/account/mfa
rem optional OIDC claim→eaos_roles mint (PHX-G81; empty = off):
rem set EAOS_OIDC_ROLE_CLAIM=groups
rem set EAOS_OIDC_ROLE_MAP=Engineering=operator,Admins=admin
rem set EAOS_OIDC_REQUIRE_MAPPED_ROLE=0
rem optional Permission context-role evaluate map (PHX-G83; empty = off):
rem set EAOS_PERMISSION_ROLE_GRANT_MAP=operator=document:read,admin=document:read|document:write
rem optional Role→grant live mint (PHX-G161; default OFF → 503; needs map above):
rem set EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED=true
rem optional WebAuthn live mint (PHX-G160; default OFF → 503; needs RP_ID + ORIGIN):
rem set EAOS_WEBAUTHN_REGISTRATION_ENABLED=true
rem set EAOS_WEBAUTHN_RP_ID=localhost
rem set EAOS_WEBAUTHN_ORIGIN=http://localhost:8000
rem optional declared EAOS roles catalog (PHX-G88; empty = off):
rem set EAOS_ROLE_CATALOG=viewer,operator,admin
rem optional declared roles store (PHX-G90; default memory):
rem set EAOS_ROLE_CATALOG_STORE=sql
rem optional OIDC multi-provider login catalog (PHX-G84/G86; empty = off):
rem set EAOS_OIDC_LOGIN_PROVIDERS=google|https://accounts.google.com|CLIENT|SECRET|||https://accounts.google.com/logout
rem optional tenant IdP federation enforce on OIDC (PHX-G66; default off):
rem set EAOS_TENANT_IDP_FEDERATION=1
rem optional durable federation bindings (PHX-G67; default memory):
rem set EAOS_TENANT_IDP_FEDERATION_STORE=sql
rem federation matrix (PHX-G77): GET /v1/platform/idp/federation/matrix (platform context)
rem federation priority (PHX-G78): POST /v1/platform/idp/federation/bindings/{id}/priority body {priority}
uvicorn api.gateway.app:app --host 0.0.0.0 --port 8000
```

Smoke:

- `GET /v1/health` → 200  
- `GET /v1/release` → version `0.2.5`；可选 `deploy_region`（PHX-G76；未设置则为 `null`）  
- `GET /terminal/` → Operator Shell  
- `GET /v1/auth/oidc/status` → 含 `webauthn_product`（default `webauthn_registration_enabled=false`；G160 env-gated live mint；ceremony routes listed）  
- `POST /v1/auth/webauthn/register/options` 与 `…/verify` → default **503** `GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`（detail 含 `ceremony_step`）；with `EAOS_WEBAUTHN_REGISTRATION_ENABLED=true` + `EAOS_WEBAUTHN_RP_ID`/`ORIGIN` → challenge-bound mint（PHX-G160；`attestation_crypto_verified=false`）  
- `POST /v1/permission/role-grants` → default **503** `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`；with `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED=true` + non-empty `EAOS_PERMISSION_ROLE_GRANT_MAP` → mint grants from roles（PHX-G161；Cap≠grant）  
- `GET /v1/permission/roles/status` → 含 `role_grant_product`（`auto_grant_from_role_enabled` mirrors env；`auto_write_routes` lists `/permission/role-grants`）  
- `GET /v1/marketplace/status` → 含 `payment_clearing_product`（G162；`payment_clearing_enabled=false` by default）  
- `POST /v1/marketplace/listings/{id}/payment-clearing` → default **503** `GATEWAY_PAYMENT_CLEARING_DISABLED`；with `EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED=true` → internal audit record（≠ external PSP）  
- `GET /v1/adapters` → meta 含 `openapi_inventory_product`（G148/G164；`route_mount_parity_complete=true`；`full_openapi_http_complete=false`；semantic 仍 deferred）  

**Held / do not enable casually in Foundation ops**

- Env `EAOS_WEBAUTHN_REGISTRATION_ENABLED` — WebAuthn live mint is **env-gated**（G160）；do not run always-on without ops intent；packed/TPM attestation crypto still Held  
- Role→grant live mint is **env-gated**（G161）；do not run always-on without ops intent  
- Marketplace payment clearing is **env-gated internal record only**（G162）；external PSP / arbitration remain fail-closed  
- Finance tax authority network (`EAOS_TAX_NETWORK` / `ENABLE_TAX_NETWORK`) — **default OFF**（PHX-G318 / PHX-G328）；ON without `EAOS_TAX_AUTHORITY_URL` → stub fail-closed；ON + URL → live `HttpTaxAuthorityAdapter` (stdlib HTTP). Optional `EAOS_TAX_AUTHORITY_BEARER` / `EAOS_TAX_AUTHORITY_TIMEOUT_SEC` (~5s). **Never commit secrets** (bearer/URL credentials) to the repo.  
- Finance PSP network (`EAOS_PSP_NETWORK` / `ENABLE_PSP_NETWORK`) — **default OFF**（PHX-G326 / PHX-G331）；`EAOS_PSP_PROVIDER` default `off`; ON + `stripe_like` without `EAOS_PSP_URL` → stub fail-closed；ON + `stripe_like` + `EAOS_PSP_URL` → live `HttpPspAdapter` (stdlib HTTP). Optional `EAOS_PSP_BEARER` / `EAOS_PSP_TIMEOUT_SEC` (~5s). **Never commit secrets** (bearer/URL credentials) to the repo.  
- Brain execute / Twin authorize — fail-closed  

### 4.0 Production GO evidence（PHX-G468）

Unconditional production promotion additionally requires:

1. human branch-protection evidence from `BRANCH_PROTECTION.md`;
2. green CI `docker-smoke` history for the candidate revision;
3. green `integration_critical` on a dedicated `eaos_test*` database; and
4. a GO decision replacing the current fail-closed decision in
   `PRODUCTION_GO_DECISION_G469.md`.

Batch M closed with **NO-GO** because these external/runtime evidence items were
not all available. Do not infer production GO from local contracts alone.

Stop: terminate the uvicorn process (SIGTERM preferred). Do not leave `--reload` enabled in production.

### 4.1 Docker Compose (optional reference)

See [COMPOSE.md](COMPOSE.md) and `deploy/docker/compose.yaml` (PHX-G50 / ADR-0069).

```bash
copy deploy\docker\.env.example deploy\docker\.env
docker compose -f deploy/docker/compose.yaml --env-file deploy/docker/.env up --build
```

### 4.2 Helm (optional reference)

See [HELM.md](HELM.md) and `deploy/helm/eaos` (PHX-G51 / ADR-0070).

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

### 4.3 Ingress / TLS (optional)

See [INGRESS.md](INGRESS.md) (PHX-G52 / ADR-0071). Default `ingress.enabled=false`.

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=eaos.example.local \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

### 4.4 HPA (optional)

See [HPA.md](HPA.md) (PHX-G53 / ADR-0072). Default `autoscaling.enabled=false`.

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set autoscaling.enabled=true \
  --set resources.requests.cpu=100m \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

### 4.5 VPA (optional)

See [VPA.md](VPA.md) (PHX-G54 / ADR-0073). Default `vpa.enabled=false`. Mutually exclusive with HPA / KEDA.

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set vpa.enabled=true \
  --set vpa.updateMode=Off \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

### 4.6 KEDA (optional)

See [KEDA.md](KEDA.md) (PHX-G58 / ADR-0077). Default `keda.enabled=false`. Mutually exclusive with HPA / VPA.

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set keda.enabled=true \
  --set resources.requests.cpu=100m \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

### 4.7 Service Mesh (optional)

See [MESH.md](MESH.md) (PHX-G59 / ADR-0078 · G71–G73 / ADR-0090–0092). Default mesh inject/policy/traffic/authz all off. Optional Istio PeerAuthentication + VS/DR + AuthorizationPolicy. No control-plane install.

```bash
helm upgrade --install eaos deploy/helm/eaos \
  --set mesh.enabled=true \
  --set mesh.policy.enabled=true \
  --set mesh.traffic.enabled=true \
  --set mesh.authz.enabled=true \
  --set secrets.jwtSecret=REPLACE_ME \
  --set secrets.postgresPassword=REPLACE_ME
```

## 5. Rollback guidance

- Prefer forward-fix migrations.
- `alembic downgrade -1` only after reviewing the revision notes for the current head.
- Do not edit applied revisions in place.
- Gateway rollback: stop process → redeploy previous artifact → confirm Alembic head compatibility (`COMPATIBILITY.md`).

## 6. Release gates

1. Release Manifest present and valid  
2. All OpenAPI files listed in Manifest exist  
3. Alembic single linear head matches Manifest  
4. Contract + PostgreSQL suites green  
5. Marketplace Foundation commercial enabled; payment capture still fail-closed  
6. Webhook subscriptions may set `signing_secret` (HMAC v1); rotate secrets out-of-band  
7. Production topology + this runbook present (PHX-G49)  
8. Compose artifacts + COMPOSE.md present (PHX-G50)  
9. Helm chart + HELM.md present (PHX-G51)  
10. Ingress template + INGRESS.md present (PHX-G52)  
11. HPA template + HPA.md present (PHX-G53)  
12. VPA template + VPA.md present (PHX-G54)  
13. KEDA ScaledObject + KEDA.md present (PHX-G58)  
14. Mesh inject labels + MESH.md present (PHX-G59)  
15. Mesh PeerAuthentication template opt-in present (PHX-G71)  
16. Mesh VirtualService + DestinationRule opt-in present (PHX-G72)  
17. Mesh AuthorizationPolicy opt-in present (PHX-G73)  
18. Seven-step review recorded in acceptance docs  
19. Manifest `milestones` includes PHX-G145…G164 when cutting a Foundation patch note  
20. WebAuthn ceremony default remains 503 unless `EAOS_WEBAUTHN_REGISTRATION_ENABLED` + RP（PHX-G160；attestation crypto still Held）；Role→grant default 503 unless `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED` + map（PHX-G161）  

## 7. Out of scope for Foundation ops

- 安装 Ingress Controller / cert-manager / metrics-server / VPA components / KEDA operator / Mesh 控制面（声明见 G52–G54 / G58–G59 / G71）  
- 公有镜像仓库推送  
- Marketplace billing / payment clearing operations  
- Multi-region failover runbooks（部署区域标签见 [REGION.md](REGION.md)；非 failover）  
- Live WebAuthn packed/TPM attestation crypto verify / single-path `/auth/webauthn/register`（G160 opens challenge-bound mint only；default 503）  
- Always-on WebAuthn mint without env + RP（PHX-G160 is **env-gated** only）  
- Always-on Role→grant mint without env gate（PHX-G161 is **env-gated** only；Cap≠grant）  
- Brain execute / Twin authorize  
- Architecture Review Board sessions（Research queue：[ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)；not an ops opening）  
- 全量 OpenAPI **semantic** parity（T-0188 remainder after G164；mount parity complete）  
