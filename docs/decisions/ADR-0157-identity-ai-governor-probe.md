# ADR-0157 — Identity AI Employee / Platform Governor Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G138  
**归属：** API Gateway / Smart Terminal / Identity

## 背景

Identity OpenAPI 与 Kernel 已定义 platform governor 与 AI employee（register/profile/assign/reassign）。G137 补齐 credential/session revoke 后，Gateway/Terminal 仍缺该平台治理面薄出口。

## 决策

1. Gateway 薄接线既有 OpenAPI 路径：  
   - `POST /v1/identity/platform-governors`  
   - `POST /v1/identity/platform-governors/{subjectId}/revocation` → 204  
   - `POST /v1/identity/ai-employees`  
   - `GET|PATCH /v1/identity/ai-employees/{id}/profile`  
   - `POST …/assignments`（tenant 上下文）  
   - `POST …/reassignments`（platform 上下文）  
2. Terminal Admin 增加对应薄控件；governor/AI 管理使用 platform 上下文；assign 使用 tenant 上下文。  
3. 调用方须为 bootstrap 或已持久化的 platform identity governor（Kernel 既有规则）。  
4. 无新 Alembic；包 `0.2.0`；≠ Role→grant / WebAuthn / 支付清算。

## Explicit Defer

- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0156-identity-credential-session-revoke-probe.md](ADR-0156-identity-credential-session-revoke-probe.md)
- [../project/PHX-G138_ARCHITECTURE_GATE.md](../project/PHX-G138_ARCHITECTURE_GATE.md)
