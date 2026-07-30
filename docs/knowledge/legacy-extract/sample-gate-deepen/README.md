# 样品门禁深化包

## 目的

本包只抽取 Legacy 中样品保管、分析完成、质量放行与库存物化门禁的可证知识。它遵循 Constitution First、Knowledge Driven、Kernel First：记录事实和缺口，不把 Legacy 的页面、表或旁路引擎直接当作 EAOS 模块设计。

## 边界

- 样品主流程权威仍见 [`../sample/sample.md`](../sample/sample.md)。
- 收样、分析、入库、转报价细节仍见 [`../sample-deepen/`](../sample-deepen/)。
- 通用质量与合规边界仍见 [`../quality-compliance/quality_check.md`](../quality-compliance/quality_check.md)。
- 本包只深化“谁保管、何时算分析完成、何时质量放行、何时允许入库”四类门禁，不修改邻包。

## 文档

- [`sample_custody.md`](sample_custody.md)：收样后的保管责任、持有人、库位、领用/归还证据。
- [`analysis_completion.md`](analysis_completion.md)：分析完成语义及其对入库/报价的实际约束。
- [`quality_release_gate.md`](quality_release_gate.md)：样品质量评价与 New/Stocked/Received 的边界。
- [`stocking_gate.md`](stocking_gate.md)：产品绑定、库存过账、幂等、事务及回退缺口。
- [`INDEX.md`](INDEX.md)：稳定 ID、主题和证据索引。

## 证据口径

- **强**：活动路由、service/repository、DDL 与模板可互证。
- **中/弱**：shadow lifecycle、报告、UI 提示或未接线 helper。
- **缺失**：未找到写路径、门禁、状态或审计链，必须写为 `UNKNOWN + 已查路径`。
- `Stocked` 只证明 Sample Receipt 已过账；不等于分析完成或质量放行。
- `Received` 属采购收货语义；不等于样品质检接受。
- `inventory.location` 是产品库存位置，不能推定为样品保管库位。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`
