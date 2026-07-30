# PHX-M18 Marketplace Package Signature Cryptography Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Marketplace  
**规范源：** ADR-0062  

## 1. 门禁目标

为 listing `signature_ref` 提供可选启用的 HMAC/Ed25519 密码学校验，默认兼容非空引用。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Boundary | Platform Marketplace；Gateway 薄适配 |
| Default | mode=off（存在性检查） |
| Algorithms | HMAC-SHA256；可选 Ed25519 |
| Fail-closed | required/misconfigured → UNCONFIGURED；bad sig → INVALID |

## 3. Exit Criteria

1. ADR-0062 Accepted。  
2. attach/submit/publish 校验路径绿。  
3. 默认 off 时 M16/M17 契约仍绿。  
4. 无 Alembic 变更；全量 contracts 绿。
