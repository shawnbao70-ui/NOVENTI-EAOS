# ADR-0128 — Package Publish / Install / Disable / Resolve Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G109  
**归属：** Smart Terminal / Package

## 背景

G108 已覆盖 Package 状态与 manifest 注册/读取 + surfaces 列表。运维仍缺 Terminal 内对 publish / install / disable / resolve 的薄调用面。

## 决策

1. Terminal Admin 增加 Publish manifest、Install package、Disable installation、Resolve action。  
2. 仅调用既有 `.../publish`、`/installations`、`.../disable`、`/actions/resolve`。  
3. path/body id 经独立输入（manifest_id / installation_id / action_key）；禁止上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Knowledge Terminal 薄探针  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0127-package-status-manifest-surfaces-probe.md](ADR-0127-package-status-manifest-surfaces-probe.md)
- [../project/PHX-G109_ARCHITECTURE_GATE.md](../project/PHX-G109_ARCHITECTURE_GATE.md)
