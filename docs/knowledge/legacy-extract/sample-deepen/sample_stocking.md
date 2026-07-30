# 绑定产品入库、Sample Receipt 与 Stocked

## Scope与证据强度

本页深化“客户样品作为库存收货”的运行路径。强证据覆盖 `samples.product_id` 后加字段、产品绑定、幂等检查、库存/产品镜像/流水三写和 Stocked 状态。库存台账通用语义交叉引用 [`../inventory-deepen/stock_ledger.md`](../inventory-deepen/stock_ledger.md)。

这里的 materialize 是入库，不是样品分析完成、产品主数据自动创建或向客户发样。

## 业务规则（稳定ID）

1. **SST-R01** 样品入库前必须把样品绑定到一个现有目录产品 id。
2. **SST-R02** `product_id` 不在原始 samples 主表稳定定义中；repository 会运行时检查并按需 ALTER ADD。
3. **SST-R03** 绑定只更新 `samples.product_id`，不改变样品状态、不写库存或样品日志。
4. **SST-R04** Sample360 仅在已绑定且尚无对应收货流水时显示/允许 materialize。
5. **SST-R05** materialize 默认数量为 1，也可通过查询参数传入其他正数。
6. **SST-R06** 幂等依据为 `inventory_ledger.trans_type='Sample Receipt'` 且 remark=`SAMPLE-{sample_id}`。
7. **SST-R07** 未发现同样品流水时，系统取得或建立产品库存行；缺行基线来自 `products.stock_qty`。
8. **SST-R08** 入库同时增加 `inventory.stock_qty`、对 `products.stock_qty` 加同量 delta，并写 `inventory_ledger`。
9. **SST-R09** 流水 qty 为正，balance_qty 为过账后现存量，产品代码/名称取过账时产品记录。
10. **SST-R10** 入库成功后样品状态直接更新为 `Stocked`。
11. **SST-R11** 绑定与 materialize 路由均要求 `Samples.edit`；页面还用浏览器 confirm 提示人工确认。
12. **SST-R12** 已物化后 Sample360 隐藏绑定表单和 materialize CTA，改为展示库存/流水链接。
13. **SST-R13** 重复入库检查是应用层先查后写，没有数据库唯一键。
14. **SST-R14** 未见 Stocked 的自动反向、退库或解绑流程；修正只能借助库存调整等外部动作。
15. **SST-R15** materialize 不复制样品测量、材料分析或图片到产品主数据。
16. **SST-R16** 绑定下拉只取按名称排序的前 500 个产品；超出集合的产品无法从当前 UI选择。
17. **SST-R17** materialize 只检查 Samples.edit，不额外要求 Inventory.edit；库存写权限边界跨模块。
18. **SST-R18** stocking repository 的样品、产品和流水查询未见显式 tenant 条件或写入 tenant_id，端到端租户隔离不成立为已证事实。

## 流程

1. 打开 Sample360，repository 确保 samples 有 product_id 列。
2. 用户选择目录产品并保存绑定。
3. 页面检查是否存在 `Sample Receipt + SAMPLE-{id}`。
4. 用户点击 Materialize，默认 qty=1并确认。
5. 服务验证样品、产品绑定、未重复和正数量。
6. 取得/创建该产品库存行。
7. 增加 inventory、同步 products镜像并追加 Sample Receipt 流水。
8. 更新样品状态 Stocked，一次提交。
9. 页面转为只读已物化提示。

## 校验（强/弱/缺失）

1. **SST-V01（强）** 绑定前样品必须存在。
2. **SST-V02（强）** 绑定 product_id 必须大于零。
3. **SST-V03（强）** 绑定和入库要求 Samples.edit。
4. **SST-V04（强）** materialize 前样品必须存在且已绑定产品。
5. **SST-V05（强）** materialize 数量必须大于零。
6. **SST-V06（强）** 同 Sample Receipt+remark 已存在则拒绝重复。
7. **SST-V07（强）** 无法取得/建立库存行则拒绝。
8. **SST-V08（弱）** 页面 browser confirm 提示人工确认；GET 路由仍执行有副作用动作。
9. **SST-V09（缺失）** 绑定时未显式验证 product_id 对应产品存在。
10. **SST-V10（缺失）** 未见数据库唯一幂等键或并发锁。
11. **SST-V11（缺失）** 未见数量单位、整数/小数、最大值或包装规则。
12. **SST-V12（缺失）** 未见 Stocked 状态前必须完成测量/分析/质量批准。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.product_id` | 样品到目录产品的可选绑定 |
| `sample_product_id` | Sample360 上下文解析出的绑定值 |
| `sample_materialized` | 是否已找到该样品 Sample Receipt 流水 |
| `can_materialize` | 已绑定且未物化的页面条件 |
| `qty` | 本次样品入库数量，默认 1 |
| `inventory.stock_qty` | 入库后的库存现存量 |
| `products.stock_qty` | 同步增加的产品库存镜像 |
| `Sample Receipt` | 样品入库流水类型 |
| `SAMPLE-{id}` | 样品入库溯源/幂等备注 |
| `balance_qty` | 本次入库后的库存余额 |
| `Stocked` | 样品已入库状态 |
| `inventory_id` | 被更新或新建的库存余额行 |
| `product_code/name` | 流水中的产品识别快照 |
| `create_time` | 应用服务器生成的过账时间 |

## 状态词汇

| 状态/词汇 | 含义 |
|---|---|
| `New` | 尚未表示库存物化 |
| Bound | 页面语义：已有 product_id；不是持久状态 |
| Materialize | 执行样品收货过账 |
| `Stocked` | 已写 Sample Receipt |
| `already_materialized` | 已有同样品收货流水 |
| `missing_product` | 未绑定目录产品 |
| `invalid_qty` | 入库数量不为正 |
| Reversed / Unstocked | UNKNOWN；未见反向状态 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SST-E01 | repository 按需增加 product_id 并执行绑定 | 强 | `apps/sample/repository.py` |
| SST-E02 | Sample360 计算 materialized/can_materialize | 强 | `apps/sample/services.py` |
| SST-E03 | 页面绑定与 materialize CTA/确认 | 强 | `templates/sample360.html` |
| SST-E04 | materialize 完整校验与三写 | 强 | `apps/sample/services.py` |
| SST-E05 | 库存 repository 负责 ensure、余额与流水写入 | 强 | `apps/inventory/repository.py` |
| SST-E06 | 路由要求 Samples.edit | 强 | `apps/sample/router.py` |
| SST-E07 | A-005 报告运行验证 Sample Receipt、产品 delta 和 Stocked | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| SST-E08 | A-017 强调 materialize 人工确认与诚实展示 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |
| SST-E09 | 台账 DDL存类型、数量、结余、备注和时间 | 强 | `runtime/v14/legacy_support.py` |
| SST-E10 | 绑定产品查询按名称限制 500 条 | 强 | `apps/sample/repository.py` |
| SST-E11 | materialize 只使用 Samples.edit 门禁 | 强 | `apps/sample/router.py` |

## UNKNOWN + 已查路径

1. **绑定产品是否必须 Active/可库存 UNKNOWN。** 已查路径：Sample bind、Product schema/services、Inventory ensure。
2. **一个样品能否拆分入库到多个产品 UNKNOWN。** 已查路径：samples.product_id、materialize、ledger幂等逻辑。
3. **样品数量的业务单位和换算 UNKNOWN。** 已查路径：materialize route/template、inventory schema、Sample报告。
4. **Stocked 后退库、报废或冲销流程 UNKNOWN。** 已查路径：Sample routes、Inventory adjustment、returns knowledge。
5. **绑定错误后的换绑规则 UNKNOWN。** 已查路径：bind service、Sample360；物化后UI隐藏但后端边界未完整审计。
6. **并发点击是否可能重复 Sample Receipt UNKNOWN。** 已查路径：ledger count、insert逻辑、数据库约束。
7. **入库是否应要求测量/质量评估完成 UNKNOWN。** 已查路径：Sample service、status、analysis tables。
8. **Sample Receipt 的成本价值来源 UNKNOWN。** 已查路径：Sample materialize、Inventory ledger、Product cost、Finance估值。
9. **租户字段是否在样品及流水写入中一致 stamp UNKNOWN。** 已查路径：Sample/Inventory repository、tenant schema。
10. **Inventory.edit 是否应成为跨模块入库的附加权限 UNKNOWN。** 已查路径：Sample router、Inventory router、permission aliases、A-005报告。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\core\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A005_Sample_Quote_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A017_Sample_Ops_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
