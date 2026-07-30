# ADR-0187 — Demo Signed Extension Seed (HMAC)

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G168  
**归属：** Demo Gateway / Smart Terminal Extensions  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U041**；PO cue「充分授权…自主开发…加快」

## 背景

Demo 双轨已有 bootstrap（G167）与声明式 Package Surfaces（G165），但 Extensions 面仍需手工登记签名包。加速联调需要在 demo 网关预置 **HMAC 验签通过并已激活** 的首方扩展，且生产 fail-closed 网关不得挂载 demo bootstrap / 不得嵌入 demo HMAC。

## 决策

1. Demo `SmartTerminalService` 使用 `ExtensionSigningSettings(mode="hmac", required=True)` 与 dev-only HMAC material。  
2. Demo seed 对 legacy + seeded tenant 各登记并激活 `noventi.demo.panel`（声明动作 `panel.render`）。  
3. `GET /v1/demo/bootstrap`（仍仅 demo 挂载）扩展返回可选 `extension_id` / `extension_key` / `extension_version` / `extensions_url`；**不**返回 HMAC secret。  
4. Terminal boot 探测 bootstrap 成功时写入 Extensions 上下文（key/version + `state.extensionId`）并启用 Activate/Mount/Invoke 控件。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS；不引入 Marketplace 任意脚本执行。

## Explicit Out

- 生产网关挂载 `/v1/demo/*` 或嵌入 demo HMAC  
- Bootstrap 返回 secrets / JWT  
- Marketplace unsigned / arbitrary script host  
- Brain execute / Twin authorize / Cap→grant  

## 关联

- [../project/PHX-G168_ARCHITECTURE_GATE.md](../project/PHX-G168_ARCHITECTURE_GATE.md)  
- [ADR-0186-demo-bootstrap-context.md](ADR-0186-demo-bootstrap-context.md)  
