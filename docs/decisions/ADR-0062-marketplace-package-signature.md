# ADR-0062 — Marketplace Package Signature Cryptography (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-M18  
**归属：** Platform Marketplace

## 背景

M16/M17 仅要求非空 `signature_ref`。ADR-0057 等显式延后 Marketplace 签名密码学校验。发布路径需 fail-closed 的可验证签名。

## 决策

1. 落点：`eaos_platform.marketplace.signing`；`MarketplaceService` 在 attach / submit / publish 调用校验。  
2. 默认 `EAOS_MARKETPLACE_SIGNING_MODE=off`：保持非空引用兼容（Foundation 开发默认）。  
3. 模式 `hmac`：`signature_ref = v1:hmac-sha256:<hex>`，密钥 `EAOS_MARKETPLACE_SIGNING_HMAC_SECRET`（≥16）。  
4. 模式 `ed25519`：`signature_ref = v1:ed25519:<urlsafe-b64>`，公钥 PEM `EAOS_MARKETPLACE_SIGNING_ED25519_PUBLIC_KEY_PEM`（需 `cryptography`）。  
5. 规范载荷：canonical JSON（`package_key` / `package_version` / `tenant_id` / `publisher_subject_id` / sorted permissions & events / `data_scope`）。  
6. `EAOS_MARKETPLACE_SIGNING_REQUIRED=1` 且 mode=off 或密钥缺失 → `MARKETPLACE_SIGNING_UNCONFIGURED`；校验失败 → `MARKETPLACE_SIGNATURE_INVALID`。  
7. 无 schema 变更；Terminal Extension activate 密码学验签见 ADR-0063 / PHX-G44。

## Explicit Defer

- Marketplace CDN 包分发与热加载  
- 多发行方 JWKS（Foundation 见 ADR-0064 / PHX-G45）；吊销列表仍延后  

- 支付清算 / 外部仲裁  

## 关联

- [ADR-0054-marketplace-commercial-policy.md](ADR-0054-marketplace-commercial-policy.md)
- [../project/PHX-M18_ARCHITECTURE_GATE.md](../project/PHX-M18_ARCHITECTURE_GATE.md)
