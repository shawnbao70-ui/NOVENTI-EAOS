# ADR-0156 — Identity Credential Validate/Revoke & Session Revoke Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G137  
**归属：** API Gateway / Smart Terminal / Identity

## 背景

Identity OpenAPI 与 Kernel 已定义 credential validate/revoke 与 session revoke；G121 仅接线 bind + session create/validate。Gateway 与 Terminal 仍缺对等薄出口。

## 决策

1. Gateway 增补既有 OpenAPI 路径：  
   - `GET /v1/identity/credentials/{id}/validation`  
   - `POST /v1/identity/credentials/{id}/revocation` → 204  
   - `POST /v1/identity/sessions/{id}/revocation` → 204  
2. Terminal Admin 增加对应薄控件；revoke 需 `reason`；session/credential 以目标 subject 作 trusted header。  
3. 响应脱敏：永不返回 `secret_handle`；status 探针声明新 surfaces。  
4. 不接线 AI employee / platform governor（另批）；包 `0.2.0`；Alembic `0029`。

## Explicit Defer

- AI employee / platform governor Gateway + Terminal  
- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0140-identity-credential-session-probe.md](ADR-0140-identity-credential-session-probe.md)
- [../project/PHX-G137_ARCHITECTURE_GATE.md](../project/PHX-G137_ARCHITECTURE_GATE.md)
