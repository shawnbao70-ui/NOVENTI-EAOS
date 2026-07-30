# EAOS Production Topology — Phoenix Foundation

**Version:** 0.2.3  
**Milestone:** PHX-G49  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Normative:** ADR-0068

## 1. Reference topology (single host)

Foundation 生产参考部署为**单主机、双进程角色**：

| Role | Process | Responsibility |
|------|---------|----------------|
| Database | PostgreSQL 14+ | Kernel / platform persistence plus authorized package schemas；Alembic head `0092_finance_realized_fx_gl_bridge_g372` |
| Gateway | `uvicorn api.gateway.app:app` | HTTP API、OIDC 边界、`/terminal/` Operator Shell、Extension Host |

```text
                    ┌──────────────────────────────────┐
                    │           Single Host            │
  Clients ─────────►│  Gateway (uvicorn :8000)         │
  (Browser / API)   │    /v1/*  /terminal/             │
                    │              │                   │
                    │              ▼                   │
                    │  PostgreSQL (EAOS_DATABASE_URL)  │
                    └──────────────────────────────────┘
```

Smart Terminal UI 与 Extension Host **不**作为独立生产进程；由 Gateway 同进程提供。

## 2. Production security baseline

| Variable | Production value | Notes |
|----------|------------------|-------|
| `EAOS_DATABASE_URL` | `postgresql+psycopg://…` | 必填；非 PostgreSQL fail-closed |
| `EAOS_GATEWAY_STORE` | `sql`（生产建议） | `memory`（默认，本地/契约）或 `sql`；`sql` 需 `EAOS_DATABASE_URL` |
| `EAOS_REQUIRE_JWT` | `1` | 禁止匿名开发头提升 |
| `EAOS_ALLOW_DEV_CONTEXT_HEADERS` | `0` | 生产关闭 |
| `EAOS_JWT_SECRET` 和/或 JWKS | 已配置 | HS256 和/或 RS256 |
| `EAOS_JWT_ISSUER` / `EAOS_JWT_AUDIENCE` | 与令牌一致 | 建议显式设置 |
| `EAOS_JWT_DENYLIST_JSON` 或 `_URL` | 可选 | 吊销列表（G46） |
| `EAOS_OIDC_*` | 可选 | Auth Code 登录（G40） |
| `EAOS_OIDC_REQUIRED_CLAIMS` | 可选 | 逗号分隔 id_token 必填声明（G79）；空=关闭 |
| `EAOS_OIDC_REQUIRED_AMR` | 可选 | 逗号分隔；id_token `amr` 须命中其一（G80） |
| `EAOS_OIDC_REQUIRED_ACR` | 可选 | 逗号分隔；id_token `acr` 须精确命中其一（G80） |
| `EAOS_OIDC_ROLE_CLAIM` | 可选 | IdP 角色/组声明名（G81）；空=关闭 |
| `EAOS_OIDC_ROLE_MAP` | 可选 | `idpValue=eaosRole,...` 映射（G81） |
| `EAOS_OIDC_REQUIRE_MAPPED_ROLE` | 可选（默认 off） | 启用映射后无命中则 deny（G81） |
| （无新 env；G82） | — | JWT `eaos_roles` → `ExecutionContext.roles` / `/v1/context` |
| `EAOS_PERMISSION_ROLE_GRANT_MAP` | 可选 | `role=type:action|...`；空=关闭（G83） |
| `EAOS_ROLE_CATALOG` | 可选 | 逗号分隔声明角色；`GET /v1/permission/roles` 聚合（G88） |
| `EAOS_ROLE_CATALOG_STORE` | 可选 `memory`（默认）/`sql` | 声明角色持久化（G90）；`sql` 需 DB + Alembic `0029` |
| `EAOS_OIDC_LOGIN_PROVIDERS` | 可选 | `key\|issuer\|client_id\|secret[:\|authorize\|token\|end_session],...`；空=关闭（G84/G86）；JWT claim 驱动 refresh/logout（G85） |
| `EAOS_OIDC_AUTHORIZE_ACR_VALUES` | 可选 | authorize `acr_values`（G87）；空=关闭 |
| `EAOS_OIDC_AUTHORIZE_PROMPT` | 可选 | authorize `prompt`（G87，如 `login`）；空=关闭 |
| `EAOS_OIDC_MFA_ENROLLMENT_URL` | 可选 | IdP MFA 注册页 HTTPS URL（G89）；空=关闭 |
| `EAOS_OIDC_DISCOVERY` | 可选 | IdP Metadata（G47） |
| `EAOS_OIDC_JWKS_WIRE` | 可选 | Discovery→JWKS（G48）；显式 JWKS 优先 |
| `EAOS_IDP_REGISTRY_STORE` | 可选 `memory`（默认）/`sql` | IdP 写注册表（G57）；`sql` 需 `EAOS_DATABASE_URL` |
| `EAOS_OIDC_DISCOVERY_REGISTRY_WRITE` | 可选 | Discovery→注册表 upsert（G60）；不写 env |
| `EAOS_OIDC_REFRESH` | 可选 | IdP refresh→重签 EAOS JWT（G61） |
| `EAOS_OIDC_REFRESH_STORE` | 可选 `memory`（默认）/`sql` | Refresh 绑定存储（G63）；`sql` 需 `EAOS_DATABASE_URL` |
| `EAOS_OIDC_REFRESH_ENCRYPT` | 可选（默认 off） | Refresh/id_token 字段 Fernet 加密（G64） |
| `EAOS_OIDC_REFRESH_FERNET_KEY` | 加密开启时必填 | Fernet URL-safe key（G64）；缺密钥 fail-closed |
| `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS` | 可选 | 逗号分隔旧密钥，仅解密（G65 MultiFernet） |
| `EAOS_OIDC_REFRESH_KEY_PROVIDER` | 可选（默认 `env`） | `env` \| `file` \| `kms`（G74/G75） |
| `EAOS_OIDC_REFRESH_FERNET_KEY_FILE` | file 模式必填 | 主密钥文件路径（G74） |
| `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE` | 可选 | 旧密钥文件（每行或逗号分隔；G74） |
| `EAOS_OIDC_REFRESH_KMS_BACKEND` | kms 必填 | `http` \| `aws` \| `gcp` \| `azure`（G75） |
| `EAOS_OIDC_REFRESH_KMS_HTTP_URL` | http 必填 | 返回 Fernet 密钥或 JSON `{primary,previous}` |
| `EAOS_OIDC_REFRESH_KMS_HTTP_BEARER` | 可选 | HTTP Bearer |
| `EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64` | aws/gcp/azure 必填 | KMS 密文（base64） |
| `EAOS_OIDC_REFRESH_KMS_KEY_ID` | aws 必填 | AWS KMS KeyId/Alias |
| `EAOS_OIDC_REFRESH_KMS_KEY_NAME` | gcp/azure 必填 | GCP resource name 或 Azure key name |
| `EAOS_OIDC_REFRESH_KMS_VAULT_URL` | azure 必填 | Key Vault URL |
| `EAOS_OIDC_REFRESH_KMS_REGION` | 可选 | AWS region 覆盖 |
| `EAOS_OIDC_REFRESH_REENCRYPT_ON_READ` | 可选（默认 off） | get 时旧密文迁主密钥（G70） |
| `EAOS_TENANT_IDP_FEDERATION` | 可选（默认 off） | 租户↔issuer 绑定强制（G66/G68）；OIDC + 租户面 JWT fail-closed |
| `EAOS_TENANT_IDP_FEDERATION_STORE` | 可选 `memory`（默认）/`sql` | 联邦绑定存储（G67）；`sql` 需 `EAOS_DATABASE_URL` |
| `EAOS_OIDC_RP_LOGOUT` | 可选 | Logout 返回 end_session URL（G61） |
| `EAOS_EXTENSION_SIGNING_MODE` | 建议非 `off` | Extension 验签（G44） |
| `EAOS_MARKETPLACE_SIGNING_MODE` | 建议非 `off` | 包签名（M18） |
| `EAOS_TAX_NETWORK`（别名 `ENABLE_TAX_NETWORK`） | 默认 off | Tax3/Tax-NET gate（PHX-G318/G328）；ON + `EAOS_TAX_AUTHORITY_URL` → live HTTP validate |
| `EAOS_TAX_AUTHORITY_URL` | 可选 | Live tax endpoint（required for `live_transport`）；never commit secrets |
| `EAOS_TAX_AUTHORITY_BEARER` | 可选 | Authorization bearer；never log / never commit |
| `EAOS_TAX_AUTHORITY_TIMEOUT_SEC` | 可选（默认 ~5） | Live HTTP timeout seconds |
| `EAOS_PSP_PROVIDER` | 默认 `off` | `off` / `fake` / `stripe_like`（PHX-G326/G331） |
| `EAOS_PSP_NETWORK`（别名 `ENABLE_PSP_NETWORK`） | 默认 off | PSP-NET gate；ON + `stripe_like` + `EAOS_PSP_URL` → live HTTP apply |
| `EAOS_PSP_URL` | 可选 | Live PSP endpoint（required for `live_transport`）；never commit secrets |
| `EAOS_PSP_BEARER` | 可选 | Authorization bearer；never log / never commit |
| `EAOS_PSP_TIMEOUT_SEC` | 可选（默认 ~5） | Live HTTP timeout seconds |

Marketplace **支付清算**在 Foundation 仍 fail-closed；不在本拓扑启用外部收单。  
Tax authority / PSP live transport 仅在显式 env 齐全时启用；默认 OFF。

## 3. Bootstrap sequence

1. 准备 PostgreSQL 实例与空库；配置 `EAOS_DATABASE_URL`。  
2. `python -m pip install -e ".[persistence,api]"`（生产可省略 `dev`）。  
3. `alembic upgrade head` → 期望 head `0092_finance_realized_fx_gl_bridge_g372`。
4. 注入 JWT / OIDC / 验签环境变量（见上表）。  
5. 启动 Gateway（无 `--reload`）：

```bash
uvicorn api.gateway.app:app --host 0.0.0.0 --port 8000
```

6. 健康检查：`GET /v1/health` → 200；`GET /v1/release` 版本 `0.2.3`。  
7. Operator Shell：`GET /terminal/`（需浏览器可达同一源）。

## 4. Verify

```bash
pytest tests/contracts
# optional dedicated DB:
# EAOS_TEST_DATABASE_URL=postgresql+psycopg://...
# pytest tests/integration
```

生产冒烟：`/v1/health`、`/v1/context`（有效 Bearer）、OIDC status（若启用）。

## 5. Secret rotation

| Secret | Guidance |
|--------|----------|
| `EAOS_JWT_SECRET` | 轮换后旧 HS256 令牌失效；先发新密钥窗口需并行 issuer/jwks 策略（见 G45） |
| JWKS / `EAOS_JWT_ISSUERS_JSON` | 依赖 `kid` 刷新；URL JWKS 支持 miss 后单次刷新 |
| `EAOS_JWT_DENYLIST_*` | 将吊销 `jti` 写入 JSON/URL；短缓存 |
| OIDC `CLIENT_SECRET` | 在 IdP 与 Gateway 同步轮换 |
| Extension / Marketplace signing keys | 按 `EAOS_*_SIGNING_*` 文档轮换；REQUIRED 模式缺密钥 fail-closed |
| Webhook `signing_secret` | 订阅级 HMAC；出站轮换见 E22 |

## 6. Rollback

- 优先**前向修复**迁移；`alembic downgrade -1` 仅在审阅当前 head 修订说明后执行。  
- Gateway 回滚：停进程 → 部署上一制品 → 确认 Alembic head 与制品兼容（见 `COMPATIBILITY.md` additive-only）。  
- 不原地编辑已应用 revision。

## 7. Compose mapping (PHX-G50)

可选参考实现：`deploy/docker/compose.yaml`（`db` + `gateway`）。操作说明见 [COMPOSE.md](COMPOSE.md)。

## 8. Helm mapping (PHX-G51)

可选参考实现：`deploy/helm/eaos`（单副本 Gateway + 可选 Postgres）。操作说明见 [HELM.md](HELM.md)。

## 9. Ingress mapping (PHX-G52)

可选 Ingress / TLS 声明（默认关闭）。操作说明见 [INGRESS.md](INGRESS.md)。

## 10. HPA mapping (PHX-G53)

可选 Gateway HPA（默认关闭）。操作说明见 [HPA.md](HPA.md)。

## 11. VPA mapping (PHX-G54)

可选 Gateway VPA（默认关闭；与 HPA 互斥）。操作说明见 [VPA.md](VPA.md)。

## 12. Deploy Region (PHX-G76)

| 变量 | 默认 | 说明 |
|------|------|------|
| `EAOS_DEPLOY_REGION` | 空 | 可选部署区域身份；`GET /v1/release` → `deploy_region` |

见 [REGION.md](REGION.md)。与租户 `region_policy_ref`、AWS `EAOS_OIDC_REFRESH_KMS_REGION` 分离。

## 13. Explicit non-goals (this document)

- 安装 Controller / metrics-server / VPA components / 公有镜像仓库推送（声明见 G50–G54）  
- 多区域生产 SaaS / failover、只读副本、跨 AZ 仲裁（区域标签见 G76）  
- Marketplace 支付清算 / 外部仲裁运维  
- 多 IdP 联邦管理 UI  
- 将包版本升至 `0.2.2+`
