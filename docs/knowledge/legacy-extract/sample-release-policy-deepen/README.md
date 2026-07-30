# 样品放行策略深化包

## 目的

本包核验 Legacy 是否真正实现样品责任转移、统一分析完成字段、质量冻结/放行，以及入库与转报价的前置门禁。结论只来自可执行路径和只读证据，不把字段、页面提示、旁路状态或文档声明当成已实现政策。

## 与邻包分工

- [`../sample-gate-deepen/`](../sample-gate-deepen/) 是保管、分析、质量和入库门禁的事实基础。
- 本包进一步核验“字段存在是否等于流程可执行”“shadow 推断是否等于完成”“质量词汇是否真正阻断 Stocked/Quote”。
- 样品、库存、报价和质量主流程继续由既有邻包负责；本包不修改或重写其正文。

## 内容

- [`custody_transfer.md`](custody_transfer.md)：owner/location/log 等结构与实际转移执行路径。
- [`analysis_completion_fields.md`](analysis_completion_fields.md)：统一 completion 字段与子表存在性推断。
- [`quality_hold_release.md`](quality_hold_release.md)：hold/release/reject 状态机及 Stocked/Quote 阻断。
- [`pre_stock_quote_gates.md`](pre_stock_quote_gates.md)：入库与转报价前置门禁矩阵。
- [`INDEX.md`](INDEX.md)：稳定 ID、证据和交叉引用索引。

## 证据口径

- **强**：实际路由、service/repository、DDL 和运行时挂载证据互证。
- **弱**：UI confirm、shadow lifecycle、文档声明或可选 helper。
- **缺失**：无执行入口、无字段、无状态迁移或异常被吞掉。
- 所有缺口均记录为 `UNKNOWN + 已查路径`，不从目标架构反推 Legacy 事实。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`
