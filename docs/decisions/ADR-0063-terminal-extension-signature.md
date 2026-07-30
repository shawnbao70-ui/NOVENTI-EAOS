# ADR-0063 — Terminal Extension Signature Cryptography (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G44  
**归属：** Smart Terminal

## 背景

G39 激活仅要求非空 `signature_ref`。M18 已交付 Marketplace 密码学验签；Extension activate 仍未强制校验。

## 决策

1. 落点：`smart_terminal.signing`；`SmartTerminalService.activate_extension` 调用校验。  
2. 默认 `EAOS_EXTENSION_SIGNING_MODE=off`：保持非空引用兼容。  
3. 模式 `hmac` / `ed25519` 与 M18 相同 `signature_ref` 格式；密钥 env：  
   - `EAOS_EXTENSION_SIGNING_HMAC_SECRET`  
   - `EAOS_EXTENSION_SIGNING_ED25519_PUBLIC_KEY_PEM`  
   - `EAOS_EXTENSION_SIGNING_REQUIRED`  
4. 规范载荷：canonical JSON（`extension_key` / `version` / `tenant_id` / sorted capabilities·actions·surfaces / `data_scope`）。  
5. Fail-closed：`TERMINAL_EXTENSION_SIGNING_UNCONFIGURED` / `TERMINAL_EXTENSION_SIGNATURE_INVALID`；未配置时仍可 `TERMINAL_EXTENSION_UNSIGNED`。  
6. 无 schema 变更；不与 Marketplace 密钥强制共用（可运维上配置相同值）。

## Explicit Defer

- 多发行方 JWKS（Foundation 见 ADR-0064 / PHX-G45）；吊销列表仍延后  

- Marketplace listing ↔ Extension 自动绑定验签  
- 支付清算 / 外部仲裁  

## 关联

- [ADR-0062-marketplace-package-signature.md](ADR-0062-marketplace-package-signature.md)
- [ADR-0057-terminal-extension-host.md](ADR-0057-terminal-extension-host.md)
- [../project/PHX-G44_ARCHITECTURE_GATE.md](../project/PHX-G44_ARCHITECTURE_GATE.md)
