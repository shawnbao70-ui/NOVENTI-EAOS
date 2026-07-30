# ADR-0184 — Terminal Declared Package Surface Projection

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G165  
**归属：** Smart Terminal / Package Platform / Demo Gateway  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U038**；PO cue「你决定，我要完整的强大的系统」

## 背景

PHX-B14 已交付声明式 Package surfaces/actions；Terminal 最近增加的 Product/Ops 演示面仍使用壳内硬编码目录，未满足 BOOK23 §10.1「Business Package 仅可通过声明式 surface/action contract 扩展 Smart Terminal」。Natural Pause 后需加深既有 Package + Terminal 能力，而非打开 HARD HOLDS。

## 决策

1. Terminal **Product / Ops** 优先从 `GET /v1/packages/surfaces` 投影已安装声明式 surface（按 `surface_key` 前缀 `product.` / `ops.` 分流）。  
2. 动作经 `POST /v1/packages/actions/resolve` 解析后，**移交 Operator**（Intent → Preview → Commit）；壳不宿主业务规则、不旁路 Permission。  
3. Demo gateway（`api.gateway.demo`）预置安装 `noventi.sample.ops` 与 `noventi.sample.product`，并授予 package/surface/action 与样例资源权限。  
4. 壳内 `DEMO_PRODUCTS` / `DEMO_OPS_ITEMS` 仅作 **offline fixture 回退**（无安装包时），并明确标注非真相源。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`；**不**打开 Brain execute / Twin authorize / Cap→grant / external PSP / Const·BP rewrite。

## Explicit Out

- Marketplace 签名扩展沙箱执行任意包 UI  
- 新 Alembic / 包版本 bump  
- Brain execute / Twin authorize enable  
- 声称业务真相已迁入 Terminal  

## 后果

- Product/Ops 从「壳内原型」升级为「声明式 Package Surface 投影 + Operator 移交」。  
- 宪章 §10.1 路径对齐；演示双轨（demo）继续加速可见联调。

## 关联

- [../project/PHX-G165_ARCHITECTURE_GATE.md](../project/PHX-G165_ARCHITECTURE_GATE.md)  
- [../project/PHX-G165_ACCEPTANCE.md](../project/PHX-G165_ACCEPTANCE.md)  
- [ADR-0029-business-package-platform.md](ADR-0029-business-package-platform.md)  
- [../constitution/BOOK23.md](../constitution/BOOK23.md)  
