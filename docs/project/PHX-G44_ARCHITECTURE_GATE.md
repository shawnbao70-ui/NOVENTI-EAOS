# PHX-G44 Terminal Extension Signature Cryptography Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**规范源：** ADR-0063  

## 1. 门禁目标

为 Extension activate 提供可选启用的 HMAC/Ed25519 密码学校验。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Boundary | Smart Terminal；复用 M18 签名格式 |
| Default | mode=off（存在性检查） |
| Gate | `activate_extension` |
| Keys | 独立 `EAOS_EXTENSION_SIGNING_*` |

## 3. Exit Criteria

1. ADR-0063 Accepted。  
2. activate 校验路径绿；默认 off 时 G39 仍绿。  
3. 无 Alembic 变更；全量 contracts 绿。
