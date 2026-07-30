# PHX-G44 Terminal Extension Signature Cryptography Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**退出门禁：** activate HMAC/Ed25519 可选验签；默认兼容；无 schema 变更

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0063 + Architecture Gate |
| B | `smart_terminal.signing` |
| C | `activate_extension` 接线 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 默认 `mode=off` 保持非空引用兼容  
- required/misconfigured → `TERMINAL_EXTENSION_SIGNING_UNCONFIGURED`  
- 坏签名 → `TERMINAL_EXTENSION_SIGNATURE_INVALID`  
- 与 Marketplace 密钥空间独立  

## 3. 自动化证据

- 本地完整回归：`438 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0063 |
| Constitution Review | 通过；Smart Terminal 边界 |
| Cross-reference Review | 通过；G39 默认路径仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 多发行方 JWKS、Marketplace 绑定、支付清算延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- 多发行方 JWKS / 密钥轮换产品化  
- Marketplace listing ↔ Extension 自动绑定验签  
- 支付清算 / 外部仲裁  

## 6. 证据索引

- [PHX-G44 Architecture Gate](PHX-G44_ARCHITECTURE_GATE.md)
- [ADR-0063](../decisions/ADR-0063-terminal-extension-signature.md)
