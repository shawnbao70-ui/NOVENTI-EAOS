# ADR-0191 — Marketplace Listing → Extension Host Acquire

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G172  
**归属：** Marketplace / Smart Terminal Extension Host  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U045**；PO cue「充分授权…自主开发…加快」

## 背景

技术 `POST …/acquire`（G103）只写 acquisition 行；G168/G169 已有 signed Extension Host，但 listing→host 无桥接。需要宪章安全的垂直切片：published listing → acquire → first-party host 可用，且不执行 Marketplace 任意脚本。

## 决策

1. 新增 `POST /v1/marketplace/listings/{id}/host-acquire`：技术 acquire（已获取则幂等）后，仅对 allowlist（初始 `noventi.demo.panel`）投影到 Extension Host（register+activate 或复用已 active）。  
2. Listing 签名与 Extension 签名保持分离；host 投影使用 Extension signing 设置重签或 `sig:host-acquire:allowlisted`（mode=off）。  
3. Demo 预置 published listing + marketplace grants；bootstrap 返回 `listing_id` / `host_acquire_url`（无 secrets）。  
4. Terminal Admin CTA「Acquire → Host」；成功后 hydrate Extensions。  
5. **不**自动 `install_package`；**不**打开 external PSP / Brain / Twin；包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- Marketplace arbitrary / remote script execution  
- Package install auto-wire  
- Listing↔extension crypto auto-bind of raw `signature_ref`  
- External PSP / Brain execute / Twin authorize  

## 关联

- [../project/PHX-G172_ARCHITECTURE_GATE.md](../project/PHX-G172_ARCHITECTURE_GATE.md)  
- [ADR-0187-demo-signed-extension-seed.md](ADR-0187-demo-signed-extension-seed.md)  
- [ADR-0188-signed-extension-host-productization.md](ADR-0188-signed-extension-host-productization.md)  
