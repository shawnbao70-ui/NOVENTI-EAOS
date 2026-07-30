# ADR-0309 — Legacy Knowledge Extract CRM + Sales Packs

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G290  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U163**

## 背景

Eng tip 在 PHX-G289 锁定 outer-close regression guard，禁止空 OpenAPI hygiene 循环。AED 优先序 #1 Foundation harden 之外，**Knowledge Driven** 允许从只读 Legacy 抽取业务知识，且 MASTER_PLAN 禁止过早业务模块实现。

## 决策

1. 正式接受 `docs/knowledge/legacy-extract/crm/**`（客户 / 商机 / 合同缺席诚实记录 / 报价）为 Knowledge 交付物。  
2. 新增 `docs/knowledge/legacy-extract/sales/**`（销售订单：convert / 归属 / V18 Approve / 佣金钩子）。  
3. 根索引 `docs/knowledge/legacy-extract/README.md` 记录包边界与收入链地图。  
4. **不**打开 CRM/Sales 产品 CRUD、Kernel/Runtime 改动、新 Alembic、Brain/Twin。  

## 后果

- EAOS 重写以知识包为业务语义输入，而非拷贝 Legacy 架构。  
- Quote `已确认` vs English Won、Contract 缺席、双 convert 路径等矛盾显式保留。  
- 包仍 `0.2.1`；Alembic 仍 `0029`。

## 非目标

- 不实现业务模块  
- 不 Promote Research AR Candidates  
- 不继续 OpenAPI inventable-outer 空循环  
