# 样品入库与转报价前置门禁矩阵

## Scope与证据强度

本页并排核验 `materialize_sample` 与 `create_quote_from_sample` 的服务端门禁。入库有集中硬校验；转报价几乎没有门禁。两者都不要求分析完成、质量放行或特定样品状态。

入库细节见 [`../sample-gate-deepen/stocking_gate.md`](../sample-gate-deepen/stocking_gate.md)，报价细节见 [`../sample-deepen/sample_to_quote.md`](../sample-deepen/sample_to_quote.md)。

## 业务规则（稳定ID）

1. **PSQ-R01** bind 与 materialize 的运行时权威在 apps/sample manifest router/service。
2. **PSQ-R02** materialize 前必须找到样品。
3. **PSQ-R03** materialize 前必须已有 product_id。
4. **PSQ-R04** bind 只要求 product_id>0，不检查分析、质量或 status。
5. **PSQ-R05** materialize qty 默认 1 且必须大于 0。
6. **PSQ-R06** materialize 不使用 samples.demand_qty。
7. **PSQ-R07** materialize 以 Sample Receipt + SAMPLE-{id} 做应用层幂等。
8. **PSQ-R08** materialize 必须能取得或创建库存行。
9. **PSQ-R09** bind/materialize 要 Samples.edit，不要 Inventory.edit。
10. **PSQ-R10** materialize 成功四写后置 Stocked。
11. **PSQ-R11** create_quote_from_sample 的运行时权威在 apps/quotation router/service。
12. **PSQ-R12** 转报价生成 QT 秒级编号和 Draft 报价头。
13. **PSQ-R13** 转报价继承 sample.customer_id，但允许空客户。
14. **PSQ-R14** 转报价解析客户最近报价→品牌→平台商业头默认。
15. **PSQ-R15** 转报价写 quotes.sample_id，并 best-effort 传播 requirement/opportunity。
16. **PSQ-R16** 转报价不要求 product_id，也不创建 quote_items。
17. **PSQ-R17** 同一样品可重复生成多个 Draft，无查重门禁。
18. **PSQ-R18** 转报价路由无 Quotes.add 或 Samples.view 服务端权限检查。
19. **PSQ-R19** materialize 与 create quote 都是有副作用 GET，并依赖浏览器 confirm。
20. **PSQ-R20** 两动作都不读取测量、材料、质量、供应商分析。
21. **PSQ-R21** 两动作都不要求样品处于 New、Analyzed、Released 或 Stocked 前置状态。
22. **PSQ-R22** create quote 不更新样品 status；materialize 不创建报价。
23. **PSQ-R23** 转报价 lifecycle helper 失败可静默，报价主体仍完成。
24. **PSQ-R24** legacy quote_pages 同名实现硬编码 USD 且功能较少，但 manifest 先挂载、residual 去重使服务版成为当前权威。

## 门禁矩阵

| 维度 | Bind Product | Materialize Stock | Create Quote |
|---|---|---|---|
| 样品存在 | 强 | 强 | 缺失 |
| 客户有效 | N/A | 缺失 | 缺失/仅继承 |
| 产品绑定 | 操作本身 | 强 | 缺失 |
| qty>0 | N/A | 强 | N/A |
| 幂等/查重 | 缺失 | 强/应用层 | 缺失 |
| 库存行 | N/A | 强 | N/A |
| 分析完成 | 缺失 | 缺失 | 缺失 |
| 质量放行 | 缺失 | 缺失 | 缺失 |
| 样品状态 | 缺失 | 缺失 | 缺失 |
| 权限 | Samples.edit | Samples.edit | 缺失 |
| HTTP 安全语义 | POST | 弱：GET+confirm | 弱：GET+confirm |
| 报价行 | N/A | N/A | 缺失 |

## 流程

### 入库

1. POST bind 保存 product_id。
2. GET materialize 检查 Samples.edit。
3. 检查样品、product_id、既有 Sample Receipt、qty 和库存行。
4. 更新 inventory、products、ledger、sample status。
5. 一次 commit 后进入 Stocked。

### 转报价

1. 用户在 Sample360 点击 Create Quote 并 confirm。
2. GET 路由调用 Quotation service。
3. 读取样品；当前服务对缺失/空客户不做硬拒绝。
4. 生成 Draft 报价头和商业默认。
5. 尝试写 sample/requirement/opportunity 追溯。
6. 重定向报价详情；无报价行、无样品状态变化、无重复阻断。

## 校验（强/弱/缺失）

1. **PSQ-V01（强）** bind/materialize 验证样品存在。
2. **PSQ-V02（强）** bind product_id 必须大于 0。
3. **PSQ-V03（强）** materialize 必须已绑定产品。
4. **PSQ-V04（强）** materialize qty 必须大于 0。
5. **PSQ-V05（强/应用层）** materialize 拒绝已有 Sample Receipt。
6. **PSQ-V06（强）** materialize 要求库存行可取得/创建。
7. **PSQ-V07（强/权限）** bind/materialize 要 Samples.edit。
8. **PSQ-V08（弱/UI）** 两个 GET 动作有 browser confirm。
9. **PSQ-V09（缺失）** 转报价不硬拒绝不存在的样品。
10. **PSQ-V10（缺失）** 转报价不验证客户存在/Active。
11. **PSQ-V11（缺失）** 两动作不验证分析完成。
12. **PSQ-V12（缺失）** 两动作不验证质量放行。
13. **PSQ-V13（缺失）** 转报价不按 sample_id 查重。
14. **PSQ-V14（缺失）** 转报价不要求至少一个 quote_item。
15. **PSQ-V15（缺失）** 转报价无 Quotes.add 权限。
16. **PSQ-V16（缺失）** materialize 无 DB 唯一幂等或并发锁。
17. **PSQ-V17（缺失）** bind 不验证产品 Active/可库存。
18. **PSQ-V18（缺失）** bind 后端不明确阻止 Stocked 样品换绑。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.id` | 两动作的来源样品 id |
| `customer_id` | 报价客户继承源 |
| `product_id` | 入库产品绑定；报价不使用 |
| `samples.status` | materialize 写 Stocked；quote 不写 |
| `demand_qty` | 入库不使用 |
| `qty` | Sample Receipt 增量 |
| `inventory.stock_qty` | 入库后库存余额 |
| `products.stock_qty` | 同量镜像 |
| `Sample Receipt` | 入库流水类型 |
| `SAMPLE-{id}` | 入库幂等/溯源 remark |
| `can_materialize` | 已绑定且未入库 |
| `sample_materialized` | ledger 已有对应记录 |
| `materialize_error` | 入库失败 query code |
| `quotes.sample_id` | 报价来源样品 |
| `quote_no` | QT 秒级编号 |
| `Draft` | 样品转报价初始状态 |
| `quote_items` | 此路径不创建 |
| `requirement_id/opportunity_id` | best-effort 追溯 |
| `Samples.edit` | 入库实际权限 |
| `Quotes.add` | 转报价路径未要求的权限 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Bound | 已有 product_id |
| Stocked | 已完成 Sample Receipt |
| Draft | 新报价头 |
| already_materialized | 入库幂等拒绝 |
| Released / Analyzed | 两动作均不要求 |
| duplicate quote | 允许产生，未形成状态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| PSQ-E01 | bind/materialize 路由与 Samples.edit | 强 | `apps/sample/router.py` |
| PSQ-E02 | materialize 校验、四写与 commit | 强 | `apps/sample/services.py` |
| PSQ-E03 | product_id 与 ledger 幂等查询 | 强 | `apps/sample/repository.py` |
| PSQ-E04 | inventory ensure 与库存写原语 | 强 | `apps/inventory/repository.py` |
| PSQ-E05 | Sample360 CTA、confirm、can_materialize | 强 | `templates/sample360.html` |
| PSQ-E06 | Create Quote GET 路由无权限 | 强 | `apps/quotation/router.py` |
| PSQ-E07 | 服务版报价创建、商业默认与追溯 | 强 | `apps/quotation/services.py` |
| PSQ-E08 | 报价 INSERT 只建头且含 sample_id | 强 | `apps/quotation/repository.py` |
| PSQ-E09 | legacy 副本与服务版行为分叉 | 强（分叉） | `apps/quotation/quote_pages.py` |
| PSQ-E10 | manifest 先挂载与 residual 去重 | 强（运行时权威） | `bootstrap/enterprise_cutover.py`、`bootstrap/v14_residual.py` |
| PSQ-E11 | A-005 验证入库/报价但不含分析质量 gate | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |

## UNKNOWN + 已查路径

1. **bind 产品是否必须 Active/可库存 UNKNOWN。** 已查路径：Sample bind、Product services、Inventory ensure。
2. **并发 materialize 是否会双过账 UNKNOWN。** 已查路径：COUNT+INSERT、ledger DDL、事务锁。
3. **四写异常是否自动 rollback UNKNOWN。** 已查路径：service commit、repository、全局异常处理。
4. **Stocked 后换绑是否被允许 UNKNOWN。** 已查路径：bind service、Sample360 UI、status checks。
5. **样品不存在时转报价在目标 DB 是否被约束拒绝 UNKNOWN。** 已查路径：Quotation service、repository、quotes DDL。
6. **同样品多 Draft 的主报价规则 UNKNOWN。** 已查路径：Quotation list、context360、reports。
7. **绑定产品是否应自动成为报价行 UNKNOWN。** 已查路径：Sample requirements、create quote、quote items。
8. **转报价 salesperson_id 应取谁 UNKNOWN。** 已查路径：普通报价、样品转报价、客户 owner。
9. **追溯扩展列是否在全部署存在 UNKNOWN。** 已查路径：lifecycle schema、workflow、status API。
10. **GET 副作用的 CSRF/重放保护 UNKNOWN。** 已查路径：routers、middleware、templates confirm。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
