# ADR-0075 — Multi-IdP Write Registry (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G56  
**归属：** Platform API Gateway / Identity boundary

## 背景

G55 提供只读 IdP/JWT 状态；发行方仍仅能通过环境变量配置。需最小可写注册表，使平台面可登记 JWKS 发行方并参与校验，同时环境变量保持最高优先级。

## 决策

1. 进程内注册表（Gateway）：`POST/GET /v1/platform/idp/issuers`，`POST .../{id}/disable`；需 `derive_platform_context`。  
2. 记录字段：`issuer`、`jwks_url` 和/或 `jwks_json`、`status`（`active`/`disabled`）；不存 HS256 secret。  
3. 校验合并：env（及 G48 Discovery wire）之后合并 active 注册表绑定；**同 issuer 时 env 胜出**。  
4. Alembic `0025`：`kernel.idp_issuer_bindings` 表（生产持久化契约）；Foundation Gateway 默认进程内存储，SQL 适配器另切片可选。  
5. `GET /v1/auth/idp/status` 增加脱敏 `registry` 段；端点本身仍只读。  
6. 包版本仍 `0.2.0`；Terminal 无写表单（BOOK23）。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Gateway SQL 仓储接线（表已就绪）  
- Discovery 写回 env；组织级联邦策略 UI  
- Service Mesh / KEDA / 多区域  

## 关联

- [ADR-0064-jwt-multi-issuer-jwks.md](ADR-0064-jwt-multi-issuer-jwks.md)
- [ADR-0074-multi-idp-status-ui.md](ADR-0074-multi-idp-status-ui.md)
- [../project/PHX-G56_ARCHITECTURE_GATE.md](../project/PHX-G56_ARCHITECTURE_GATE.md)
