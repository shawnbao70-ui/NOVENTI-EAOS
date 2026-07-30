# PHX-M18 Marketplace Package Signature Cryptography Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Marketplace  
**退出门禁：** HMAC/Ed25519 可选验签；默认兼容；无 schema 变更

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0062 + Architecture Gate |
| B | `marketplace.signing` |
| C | Service attach/submit/publish 接线 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 默认 `mode=off` 保持非空引用兼容  
- required/misconfigured → `MARKETPLACE_SIGNING_UNCONFIGURED`  
- 坏签名 → `MARKETPLACE_SIGNATURE_INVALID`  
- 无支付清算开放  

## 3. 自动化证据

- 本地完整回归：`435 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0062 |
| Constitution Review | 通过；Platform Marketplace 边界 |
| Cross-reference Review | 通过；M16/M17 默认路径仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | Extension 强制验签、多发行方 JWKS、支付清算延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Terminal Extension activate 强制密码学验签  
- 多发行方 JWKS / 密钥轮换产品化  
- 支付清算 / 外部仲裁  

## 6. 证据索引

- [PHX-M18 Architecture Gate](PHX-M18_ARCHITECTURE_GATE.md)
- [ADR-0062](../decisions/ADR-0062-marketplace-package-signature.md)
