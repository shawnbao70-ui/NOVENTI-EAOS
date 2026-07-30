# ADR-0188 — Signed Extension Host Productization

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G169  
**归属：** Smart Terminal Extensions  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U042**；PO cue「充分授权…自主开发…加快」

## 背景

G168 已在 demo 预置 HMAC 签名并激活的首方扩展，但 Extensions 面仍以「先 Register」为主路径。需要产品化 signed host：hydrate 已激活扩展 → Mount/Invoke，形成完整垂直切片，同时继续禁止 Marketplace 任意脚本。

## 决策

1. Terminal Extensions 增加 **Hydrate signed** 与 host status；从 `GET /v1/terminal/extensions` 按 bootstrap `extension_id` 或 `extension_key`+`active` 选中扩展。  
2. Demo bootstrap 成功后自动 hydrate；切换到 Extensions surface 时再次 hydrate。  
3. 登记/激活路径保留；不引入 Marketplace catalog 任意脚本执行；不打开 HARD HOLDS。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- Marketplace unsigned / arbitrary remote script host  
- Bootstrap 返回 HMAC secret  
- Brain execute / Twin authorize / Cap→grant  

## 关联

- [../project/PHX-G169_ARCHITECTURE_GATE.md](../project/PHX-G169_ARCHITECTURE_GATE.md)  
- [ADR-0187-demo-signed-extension-seed.md](ADR-0187-demo-signed-extension-seed.md)  
