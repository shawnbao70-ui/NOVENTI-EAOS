# ADR-0114 — Terminal Effective Permissions Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G95  
**归属：** Smart Terminal / Permission

## 背景

G94 已提供 evaluate/explain 薄探针。运维仍缺 Terminal 内对 principal 有效权限列表的只读调用面。

## 决策

1. Terminal Admin 增加「List effective permissions」薄控件。  
2. 仅调用既有 `GET /v1/permission/principals/{subject_id}/effective-permissions`。  
3. path 中 `subject_id` 由独立输入提供（默认可填当前 Subject）；禁止 body 提升。  
4. 鉴权沿用 Kernel self-or-auditor；不创建/修改 grant。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0113-terminal-permission-evaluate.md](ADR-0113-terminal-permission-evaluate.md)
- [../project/PHX-G95_ARCHITECTURE_GATE.md](../project/PHX-G95_ARCHITECTURE_GATE.md)
