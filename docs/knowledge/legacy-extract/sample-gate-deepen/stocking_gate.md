# 样品入库门禁、过账触发与失败回退

## Scope与证据强度

本页深化 `materialize_sample` 的真正入库门禁、同步过账时点和失败边界。三写/四写、Samples.edit、应用层幂等和一次 commit 为强证据；并发安全、显式 rollback、补偿、冲销和跨模块权限为缺失。

库存物化结果交叉引用 [`../sample-deepen/sample_stocking.md`](../sample-deepen/sample_stocking.md)；本页只深化 gate，不重写库存台账。

## 业务规则（稳定ID）

1. **SG-R01** 入库前必须已有样品记录。
2. **SG-R02** 入库前 samples.product_id 必须大于 0。
3. **SG-R03** product_id 是运行时按需增加的列，不是最初 samples DDL 的稳定字段。
4. **SG-R04** bind 只更新 product_id 并独立 commit，不写库存、流水或状态。
5. **SG-R05** 绑定产品下拉只取按名称排序的前 500 条。
6. **SG-R06** materialize 默认 qty=1，路由 query 可传其他 float。
7. **SG-R07** qty 只要求大于 0，不读取 samples.demand_qty。
8. **SG-R08** 幂等条件是 inventory_ledger 中 `Sample Receipt` 且 remark=`SAMPLE-{sample_id}`。
9. **SG-R09** 幂等为先 COUNT 后 INSERT 的应用层检查，无数据库唯一约束。
10. **SG-R10** inventory 行不存在时可按 products.stock_qty 基线创建。
11. **SG-R11** 过账先增加 inventory.stock_qty。
12. **SG-R12** 同次过账再对 products.stock_qty 加同量 delta。
13. **SG-R13** 同次过账追加 ledger，qty 为正，balance_qty 为过账后余额。
14. **SG-R14** ledger 保存产品代码/名称的过账时快照。
15. **SG-R15** 成功后更新 samples.status=`Stocked`。
16. **SG-R16** inventory、products、ledger、sample status 四步后调用一次 commit。
17. **SG-R17** 用户点击 Sample360 Materialize 并 confirm 后同步过账，不走审批或异步队列。
18. **SG-R18** materialize 是有副作用 GET；confirm 只是浏览器提示。
19. **SG-R19** bind 和 materialize 只要求 Samples.edit，不额外要求 Inventory.edit。
20. **SG-R20** `can_materialize` 只等于已绑定且未发现对应 Sample Receipt。
21. **SG-R21** 测量、材料、质量、供应商分析和样品 status 都不是前置门禁。
22. **SG-R22** materialize 不复制分析、图片或认证信息到产品主数据。
23. **SG-R23** 已物化后 UI 隐藏 bind/materialize，但后端 bind 未明确拒绝 Stocked 样品。
24. **SG-R24** 未见 Stocked 专用反向、退库、解绑或报废流程。
25. **SG-R25** AI brief 只推荐入库动作，不自动执行。

## 流程

1. Sample360 加载时确保 product_id 列存在。
2. 未绑定时，用户从最多 500 个产品中选择并 POST bind。
3. bind 写 product_id 并提交。
4. 页面以 product_id + ledger count 计算 can_materialize。
5. 用户点击 GET materialize，默认 qty=1，并接受浏览器 confirm。
6. 路由检查 Samples.edit。
7. 服务检查样品、product_id、既有 Sample Receipt、qty 和库存行。
8. 顺序更新 inventory、products、ledger、sample status。
9. 一次 commit 后重定向 Sample360。
10. 任一步失败没有业务补偿/重试/回退流程证据。

## 校验（强/弱/缺失）

1. **SG-V01（强）** 样品不存在返回 not_found。
2. **SG-V02（强）** 绑定 product_id 必须大于 0。
3. **SG-V03（强）** materialize 必须已有 product_id。
4. **SG-V04（强）** qty 必须大于 0。
5. **SG-V05（强）** 已有同样品 Sample Receipt 返回 already_materialized。
6. **SG-V06（强）** 无法取得/建立 inventory 行返回 inventory_missing。
7. **SG-V07（强/权限）** bind/materialize 要 Samples.edit。
8. **SG-V08（弱/UI）** browser confirm 提示人工确认。
9. **SG-V09（缺失）** bind 未显式验证 product_id 对应产品存在、Active 或可库存。
10. **SG-V10（缺失）** 未验证 qty 单位、精度、整数、上限或包装倍数。
11. **SG-V11（缺失）** 无数据库唯一幂等键或并发锁。
12. **SG-V12（缺失）** 无 POST/CSRF 语义保护，有副作用 GET 可重放。
13. **SG-V13（缺失）** 不要求分析完成或质量放行。
14. **SG-V14（缺失）** 不要求 Inventory.edit。
15. **SG-V15（缺失）** 不检查样品 status 前置值。
16. **SG-V16（缺失）** 无显式 begin/rollback 和异常后的连接恢复。
17. **SG-V17（缺失）** 无四写完成后的 reconciliation 校验。
18. **SG-V18（缺失）** 后端 bind 不明确阻止已 Stocked 样品换绑。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.product_id` | 样品绑定的单个目录产品 |
| `sample_product_id` | Sample360 上下文中的绑定值 |
| `qty` | 本次入库增量，默认 1 |
| `samples.demand_qty` | 需求数量字段，materialize 不使用 |
| `inventory.id` | 被创建或更新的库存余额行 |
| `inventory.stock_qty` | 入库后库存余额 |
| `products.stock_qty` | 同量更新的产品镜像 |
| `inventory_ledger.trans_type` | 固定 Sample Receipt |
| `inventory_ledger.remark` | SAMPLE-{id} 溯源/幂等文本 |
| `inventory_ledger.qty` | 本次正向库存增量 |
| `inventory_ledger.balance_qty` | 过账后结余 |
| `product_code/product_name` | 过账时产品快照 |
| `create_time` | 应用服务器过账时间 |
| `sample_materialized` | 是否找到对应 Sample Receipt |
| `can_materialize` | 已绑定且未物化 |
| `Stocked` | 样品入库结果标签 |
| `materialize_error` | not_found/missing_product/already_materialized/invalid_qty/inventory_missing |
| `Samples.edit` | 实际跨域库存写门禁 |
| `Inventory.edit` | 库存调整权限，但样品物化未要求 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Bound | 有 product_id 的页面语义，不是持久状态 |
| Materialize | 同步执行样品库存收货 |
| Stocked | Sample Receipt 成功后的样品状态 |
| already_materialized | 已存在幂等流水 |
| missing_product | 未绑定产品 |
| invalid_qty | qty 不为正 |
| inventory_missing | 无法建立/取得库存行 |
| Reversed / Unstocked | 未实现 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SG-E01 | product_id 列、绑定和幂等 COUNT | 强 | `apps/sample/repository.py` |
| SG-E02 | materialize 全部校验、四写和一次 commit | 强 | `apps/sample/services.py` |
| SG-E03 | inventory ensure、余额、镜像和 ledger 原语 | 强 | `apps/inventory/repository.py` |
| SG-E04 | 路由为 GET 且只要求 Samples.edit | 强 | `apps/sample/router.py` |
| SG-E05 | UI can_materialize、qty=1、confirm 和错误提示 | 强 | `templates/sample360.html` |
| SG-E06 | ledger DDL 无幂等唯一约束 | 强 | `runtime/v14/legacy_support.py` |
| SG-E07 | A-005 验证三写、Stocked 与重复拒绝 | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| SG-E08 | A-017 验证人工确认且无 AI 自动入库 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |
| SG-E09 | Inventory adjust 使用不同的 Inventory.edit 权限 | 强（边界） | `apps/inventory/router.py` |
| SG-E10 | AI brief 只生成 materialize 建议 | 中 | `v15/ai_operating_depth/brief.py` |
| SG-E11 | 模块文档声明库存权威，但实际由 Sample 直接调用 repository | 中/偏差 | `business_modules/inventory.md`、`production.md` |

## UNKNOWN + 已查路径

1. **产品是否必须 Active/可库存 UNKNOWN。** 已查路径：bind、Product schema/services、Inventory ensure。
2. **qty 的业务单位及与 demand_qty 换算 UNKNOWN。** 已查路径：route、template、samples DDL、inventory schema。
3. **一样品能否拆分多个产品或多次部分入库 UNKNOWN。** 已查路径：单 product_id、单 remark 幂等、ledger。
4. **并发双 GET 是否会双过账 UNKNOWN。** 已查路径：COUNT/INSERT、DDL、连接事务与锁。
5. **四写中途异常是否会由连接自动 rollback UNKNOWN。** 已查路径：service commit、repository、全局异常中间件。
6. **commit 失败后的补偿或重试 UNKNOWN。** 已查路径：jobs、workflow、reconciliation scripts、reports。
7. **Stocked 后标准退库/报废/冲销流程 UNKNOWN。** 已查路径：Sample routes、Inventory adjustment、returns/reversal。
8. **Stocked 样品后端换绑是否是允许行为 UNKNOWN。** 已查路径：bind service、Sample360 UI、status checks。
9. **Sample Receipt 成本和估值来源 UNKNOWN。** 已查路径：ledger、Product cost、Finance inventory valuation。
10. **租户字段是否在四写中一致 stamp UNKNOWN。** 已查路径：Sample/Inventory repository、tenant schema。
11. **Inventory.edit 是否应成为附加权限 UNKNOWN。** 已查路径：Sample router、Inventory router、permission matrix。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\core\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A005_Sample_Quote_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A017_Sample_Ops_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
