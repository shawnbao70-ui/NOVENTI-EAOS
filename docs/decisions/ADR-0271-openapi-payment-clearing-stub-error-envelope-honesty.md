# ADR-0271 — OpenAPI PaymentClearingStubError Envelope Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G252  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U125**

## 背景

Live `raise_payment_clearing_disabled` 经 FastAPI 返回 `{detail: StubDetail}`，
但 OpenAPI 503 直接 `$ref` StubDetail（缺信封），与 WebAuthn/RoleGrant StubError 不一致。

## 决策

1. 新增 `PaymentClearingStubError`；503 → `$ref`。  
2. StubDetail `additionalProperties: false`；显式 400 → GatewayDetailError。  
3. marketplace **1.2.12**；ops **1.0.51**；inventory PHX-G252。  
4. external PSP HARD HOLD 仍关。
