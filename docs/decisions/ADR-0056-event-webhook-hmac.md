# ADR-0056 — Event Webhook HMAC Signatures

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-E22  
**归属：** Shared Event Capability / Event Bus

## 背景

ADR-0051 交付可选 `delivery_url` webhook，但显式延后签名。订阅方需要可验证的投递完整性。

## 决策

1. 订阅可带可选 `signing_secret`（仅与 `delivery_url` 联用）。  
2. 签名算法：**HMAC-SHA256**，版本前缀 `v1`。  
3. 签署材料：`{unix_timestamp}.{raw_json_body}`（body 与实际 POST 字节一致）。  
4. 请求头：  
   - `X-EAOS-Webhook-Timestamp`  
   - `X-EAOS-Webhook-Signature: v1=<hex>`  
5. 无 `signing_secret` 时行为同 E21（未签名，兼容）。  
6. Kernel 提供 `verify_webhook_signature` 供契约/订阅方校验；Gateway 不验签入站。

## Explicit Defer

- 密钥轮换 / 多版本并存产品化编排  
- 加密存储密钥（本切片明文持久化于租户库，运维加密另批）  
- mTLS webhook

## 关联

- [ADR-0051-event-webhook-transport.md](ADR-0051-event-webhook-transport.md)
- [../project/PHX-E22_ARCHITECTURE_GATE.md](../project/PHX-E22_ARCHITECTURE_GATE.md)
