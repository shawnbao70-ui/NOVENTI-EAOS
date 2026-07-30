# 样品门禁深化索引

## 文档导航

| 文档 | 主题 | 稳定 ID |
|---|---|---|
| [`sample_custody.md`](sample_custody.md) | 接收、持有人、责任转移、库位与日志 | `SC-*` |
| [`analysis_completion.md`](analysis_completion.md) | 四类分析、完成推断、报价/入库门禁 | `AC-*` |
| [`quality_release_gate.md`](quality_release_gate.md) | 质量评价、放行缺口、状态边界 | `QRG-*` |
| [`stocking_gate.md`](stocking_gate.md) | 绑定、过账、幂等、权限、失败回退 | `SG-*` |

## 交叉引用

| 既有知识 | 本包不重复的权威 |
|---|---|
| [`../sample/sample.md`](../sample/sample.md) | 样品主流程、申请/发样缺口 |
| [`../sample-deepen/sample_intake.md`](../sample-deepen/sample_intake.md) | 收样创建与 New |
| [`../sample-deepen/sample_analysis.md`](../sample-deepen/sample_analysis.md) | 测量、分析表与图片 |
| [`../sample-deepen/sample_stocking.md`](../sample-deepen/sample_stocking.md) | Sample Receipt 三写 |
| [`../sample-deepen/sample_to_quote.md`](../sample-deepen/sample_to_quote.md) | 样品转 Draft 报价 |
| [`../quality-compliance/quality_check.md`](../quality-compliance/quality_check.md) | 通用质量、来料/成品检验缺口 |

## 核心结论

1. Legacy 没有完整 chain-of-custody：可证的是客户来样登记、图片、可选 owner 列和未接线日志，不含持有人转移、领用/归还或样品库位。
2. 四类分析没有统一 completion 字段；shadow stage 由子表行存在性推断，且材料分析的声明与代码判定不一致。
3. 未完成测量、材料、质量或供应商分析仍可绑定产品、入库和转报价。
4. 样品质量评价是追加式人工评分，不形成 release/reject/hold 状态机。
5. `Stocked` 是库存过账结果；`Received` 是采购收货状态；二者都不是质量接受结论。
6. 入库强门禁仅覆盖样品存在、产品绑定、正数量、库存行、应用层幂等和 Samples.edit。
7. 过账执行 inventory、products、ledger、sample status 四写后一次 commit；无显式 rollback、补偿或数据库级幂等约束。

## 主要证据

- `apps/sample/`
- `apps/inventory/`
- `apps/quotation/`
- `core/object360/sample/`
- `core/sample/`
- `templates/samples.html`
- `templates/sample_detail.html`
- `templates/sample360.html`
- `runtime/v14/legacy_support.py`
- `database/upgrade_patch.py`
- `business_modules/`
- `docs/reports/Business_Strong_A005_Sample_Quote_Report.md`
- `docs/reports/Business_Strong_A017_Sample_Ops_Report.md`
