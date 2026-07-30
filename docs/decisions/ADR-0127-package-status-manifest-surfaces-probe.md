# ADR-0127 — Package Status / Manifest / Surfaces Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G108  
**归属：** Smart Terminal / Package

## 背景

G27 已交付 Package HTTP 面；Workflow Terminal 运维面（G104–G107）已齐。下一薄切片切入 Package：状态 + manifest 注册/读取 + surfaces 列表；publish/install/disable/resolve 另批。

## 决策

1. 新增只读 `GET /v1/packages/status`（脱敏能力清单；`writable=false`）。  
2. Terminal Admin 增加：Package status、Register/Get manifest、List surfaces。  
3. Register 以 JSON 对象体调用既有 `POST /v1/packages/manifests`；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Terminal publish / install / disable / action resolve  
- Marketplace 支付清算 / 外部仲裁（另批）  
- Knowledge Terminal 薄探针  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [PHX-G27_ACCEPTANCE.md](../project/PHX-G27_ACCEPTANCE.md)
- [../project/PHX-G108_ARCHITECTURE_GATE.md](../project/PHX-G108_ARCHITECTURE_GATE.md)
