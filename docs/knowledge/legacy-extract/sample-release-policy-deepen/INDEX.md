# 样品放行策略深化索引

## 文档导航

| 文档 | 核验主题 | 稳定 ID |
|---|---|---|
| [`custody_transfer.md`](custody_transfer.md) | 保管人/库位/交接是否可执行 | `CT-*` |
| [`analysis_completion_fields.md`](analysis_completion_fields.md) | completion 字段与 shadow 推断 | `ACF-*` |
| [`quality_hold_release.md`](quality_hold_release.md) | hold/release/reject 与阻断关系 | `QHR-*` |
| [`pre_stock_quote_gates.md`](pre_stock_quote_gates.md) | Stock/Quote 前置门禁矩阵 | `PSQ-*` |

## 权威交叉引用

| 主题 | 邻包 |
|---|---|
| 保管事实 | [`../sample-gate-deepen/sample_custody.md`](../sample-gate-deepen/sample_custody.md) |
| 分析完成 | [`../sample-gate-deepen/analysis_completion.md`](../sample-gate-deepen/analysis_completion.md) |
| 质量放行边界 | [`../sample-gate-deepen/quality_release_gate.md`](../sample-gate-deepen/quality_release_gate.md) |
| 入库门禁 | [`../sample-gate-deepen/stocking_gate.md`](../sample-gate-deepen/stocking_gate.md) |
| 样品转报价 | [`../sample-deepen/sample_to_quote.md`](../sample-deepen/sample_to_quote.md) |
| 通用质量 | [`../quality-compliance/quality_check.md`](../quality-compliance/quality_check.md) |

## 核心结论

1. `samples.owner`、`sample_logs` 是结构证据，不构成可执行的 holder/location transfer。
2. Inventory Transfer 改产品数量，不转移样品实体。
3. samples 与四类分析表均无统一 completion/is_complete/completed_at。
4. Object360 只按子表行存在推断 shadow stage，且不写回 samples.status。
5. 样品域没有 hold/release/reject/quarantine 状态机。
6. Stocked 与 Draft Quote 均不受分析完成或质量放行阻断。
7. Materialize 有样品、产品、数量、幂等、库存行和 Samples.edit 等强门禁。
8. Create Quote 几乎没有服务端硬门禁，可空客户、空行、重复 Draft，并缺权限检查。
9. Manifest 路由先挂载且 residual 去重，服务版转报价是当前运行时权威；legacy 副本仍构成知识分叉风险。

## 证据主路径

- `apps/sample/`
- `apps/inventory/`
- `apps/quotation/`
- `core/object360/sample/`
- `runtime/v14/legacy_support.py`
- `database/upgrade_patch.py`
- `bootstrap/enterprise_cutover.py`
- `bootstrap/v14_residual.py`
- `templates/sample*.html`
- `docs/reports/Business_Strong_A005_Sample_Quote_Report.md`
- `docs/reports/Business_Strong_A017_Sample_Ops_Report.md`
