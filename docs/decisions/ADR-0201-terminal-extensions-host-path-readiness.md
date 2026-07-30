# ADR-0201 — Terminal Extensions Demo Host-Path Readiness

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G182  
**归属：** Smart Terminal Extensions  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U055**；PO cue「充分授权…自主开发…加快」

## 背景

G167–G175 已打通 demo bootstrap、HMAC 扩展、allowlisted host-acquire 与 Admin status 行，但 Acquire→Host 与 readiness 仍偏 Admin。Extensions 操作者需在 Admin↔Extensions 间往返。

## 决策

1. Extensions 面板增加 **host-path readiness** 摘要（listing / allowlist key / hydrated / scripts·install·psp）。  
2. Extensions 提供 **Acquire → Host** CTA（allowlisted only），成功后 hydrate 并展示 `host_actions`。  
3. Demo bootstrap milestone → **PHX-G182**；可选返回 `host_actions`。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不扩展 allowlist；不打开 HARD HOLDS。

## Explicit Out

- Non-allowlist catalog / Marketplace arbitrary scripts  
- Package install / external PSP / Brain / Twin  

## 关联

- [../project/PHX-G182_ARCHITECTURE_GATE.md](../project/PHX-G182_ARCHITECTURE_GATE.md)  
- [ADR-0194-terminal-host-acquire-status-surface.md](ADR-0194-terminal-host-acquire-status-surface.md)  
