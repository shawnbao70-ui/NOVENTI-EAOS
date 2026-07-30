# ADR-0319 — Sample Knowledge Pack (CRM→Delivery Assembly)

**状态：** Accepted  
**日期：** 2026-07-24  
**里程碑：** PHX-G293  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U229**

## 背景

Eng tip 在 PHX-G290…G292 接受 CRM + Sales + Finance + Delivery Legacy Knowledge Extract 后，优先序指向 **Sample knowledge pack**：将已接受知识组装为 Terminal demo / Research observation 可读切片，且 MASTER_PLAN / AED 仍禁止过早业务模块实现与 Brain/Twin 打开。

## 决策

1. 新增 `docs/knowledge/sample-pack/**`：交叉链接并组装 G290–G292 收入链结论（INDEX + assembled chain + usage + fail-closed）。  
2. **不**打开 CRM/Sales/Finance/Delivery 产品 CRUD；**不**打开 Brain execute / Twin authorize / Cap→grant / external PSP。  
3. “Sample” 指 demo/research 样例组装，**不是** Legacy「客户来样」`legacy-extract/sample/`。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`。

## 后果

- Terminal demo 与 Research 观察有单一入口，权威事实仍在 extract 包。  
- Tip Next 从 Sample knowledge pack 前移到 live T2–T3 / PO-gated items。  
- Deepen packs 与 rewrite-boundary ADRs（0312–0318）不因本切片被隐式 Promote。

## 非目标

- 不实现业务模块  
- 不 Promote Research AR Candidates  
- 不继续空 OpenAPI hygiene 循环  
