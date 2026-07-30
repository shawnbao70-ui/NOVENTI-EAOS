# Legacy Knowledge Extract — Fulfillment Deepen

**Source system:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识均衡深挖；不继承 Legacy 架构  
**Writable home:** 仅 `docs/knowledge/legacy-extract/fulfillment-deepen/**`  
**Verified:** 2026-07-23

## Purpose

深挖订单履约中容易被状态标签掩盖的库存预留、分批交付、退货/冲销/重开及仓库组织事实。每篇均以运行实现为主证，分别列出规则、校验、数据语义、证据表和至少五项带已查路径的 UNKNOWN。

## Evidence discipline

- `business_modules/*.md` 是边界/未来重构规范，不自动证明运行能力。
- `docs/reports/*` 用于确认迁移、门禁和已知限制；结论仍与 handler、repository、schema、template 互证。
- 页面词汇、状态手工更新和打印单据不等于库存/财务业务动作。
- 预留、部分发货、退货和仓库主数据缺失时，使用 `UNKNOWN + 已查路径`，不以通用 Adjust 或备注字段冒充。
- 不修改既有 ops/delivery/sales 知识正文，仅作交叉引用。

## Package contents

| File | Purpose |
|---|---|
| [INDEX.md](INDEX.md) | 深挖主题、证据强度与边界 |
| [reservation.md](reservation.md) | 库存预留、占用、可用量与释放 |
| [partial_delivery.md](partial_delivery.md) | 分批/部分发货及累计履约缺口 |
| [returns_reversal.md](returns_reversal.md) | 退货、冲销、重开和反向库存 |
| [warehouse.md](warehouse.md) | 仓库、库位、location 与库间移动表象 |
