# ADR-0213 — Terminal Domain Foundation Status Surface

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G194  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U067**；PO cue「充分授权…自主开发…加快」

## 背景

G191–G193 已诚实文档化 Brain/Twin/AI/Workflow/Package/Terminal/Event status
围栏，但 Admin 仍需逐个按钮探测，缺少一瞥式 fail-closed 摘要。

## 决策

1. Admin CTA **Domain foundation status (G194)** + `domainFoundationStatus` 行。  
2. `loadDomainFoundationStatus` 并行只读探测 twin/brain/ai/workflow/package/
   terminal/event status（`auth: false`），摘要围栏字段（execute/authorize/
   advisory/AI subject/approval SoT/writable）。  
3. Bootstrap quiet refresh（对标 G183）。  
4. **不打开** Brain execute / Twin authorize / external PSP。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- HARD HOLD openings  
- Inventory semantic-complete claim  

## 关联

- [../project/PHX-G194_ARCHITECTURE_GATE.md](../project/PHX-G194_ARCHITECTURE_GATE.md)  
