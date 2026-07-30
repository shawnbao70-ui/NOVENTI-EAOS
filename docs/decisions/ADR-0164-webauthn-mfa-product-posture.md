# ADR-0164 — WebAuthn / MFA Product Posture (Thin Surface)

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G145  
**归属：** API Gateway / Auth / Smart Terminal  
**授权：** DAL-G003 Eng Explicit Defer item `2`（DAL-U006）

## 背景

Eng Explicit Defer `2` 要求打开 Foundation MFA / WebAuthn **产品面**。既有 G89/G134 已交付 IdP MFA enrollment **redirect**（`GET /auth/oidc/mfa-enrollment`），但运营面缺少显式「WebAuthn 注册未开通」姿态。完整 WebAuthn credential create/get ceremony 仍不在本切片。

## 决策

1. 新增只读 helper `api/gateway/webauthn_product.py`，返回 Foundation MFA/WebAuthn 产品姿态字典：  
   - `webauthn_registration_enabled: false`  
   - `registration_routes: []`（无 live `/auth/webauthn/register`）  
   - MFA enrollment 指针复用 G89/G134（`mfa_enrollment_*` / path）  
   - `fail_closed_reasons` 说明注册仪式仍关闭  
2. 将姿态挂到 `oidc_status()` → `GET /v1/auth/oidc/status` 的 `webauthn_product` 字段（additive；不破坏 G89/G134）。  
3. OpenAPI `auth.openapi.yaml` 文档化姿态字段；`info.version` patch bump。  
4. Terminal 增加薄行：展示 `registration_enabled=false` + 既有 MFA enrollment 链接（当已配置）。  
5. **不**实现 WebAuthn credential create/get；**不**新增 Alembic；包版本保持 `0.2.1`。

## Explicit Out（本切片不开口）

- Live WebAuthn registration ceremony（`/auth/webauthn/register` 仍 ABSENT）  
- Role→grant 自动写入  
- Marketplace 支付清算 / 外部仲裁  
- Brain execute / Twin authorize  
- 新 Alembic revision  

## 后果

- Eng `2` 以 **thin posture surface** 满足门禁；完整 ceremony 仍可另批。  
- Eng 下一可选：Role→grant（`3`）；支付清算（`4`）仍暂缓。  
- IdP enrollment redirect 仍是唯一 live enroll 路径。

## 关联

- [../project/PHX-G145_ARCHITECTURE_GATE.md](../project/PHX-G145_ARCHITECTURE_GATE.md)  
- [../project/PHX-G145_ACCEPTANCE.md](../project/PHX-G145_ACCEPTANCE.md)  
- [ADR-0108-oidc-mfa-enrollment-url.md](ADR-0108-oidc-mfa-enrollment-url.md)  
- [ADR-0153-oidc-mfa-enrollment-openapi.md](ADR-0153-oidc-mfa-enrollment-openapi.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
