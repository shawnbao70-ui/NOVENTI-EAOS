# 需求到样品、报价的追溯与静默降级

## Scope与证据强度

本页深化 requirement 向 sample、quote、sales order 的追溯。Legacy 同时使用三类表示：

1. `business_requirements.sample_id/quote_id/sales_order_id` 单值快捷指针；
2. 下游 `samples/quotes/sales_orders.requirement_id` 与 `opportunity_id` 反向字段；
3. `requirement_links` 多值关系流水。

workflow 的条件列检测和 propagation 为强证据；它对缺表、缺列和部分异常静默降级，三类表示的一致性不是强保证。样品业务和转报价主规则交叉引用 [`../sample-deepen/sample_to_quote.md`](../sample-deepen/sample_to_quote.md)，此处不重写。

## 业务规则（稳定ID）

1. **RT-R01** schema 在需求头保留 sample_id、quote_id、sales_order_id 三个单值下游指针。
2. **RT-R02** schema 以 ALTER 为 samples、quotes、sales_orders 增 requirement_id/opportunity_id 反向字段。
3. **RT-R03** `link_sample_to_requirement` 在列存在时双向写 sample.requirement_id 与 requirement.sample_id。
4. **RT-R04** 样品绑定 helper 不写 requirement_links，也不传播 opportunity_id 到 sample。
5. **RT-R05** 当前 `apps/sample` 创建/编辑路径未见调用 `link_sample_to_requirement`；helper 存在不等于可操作流程已接通。
6. **RT-R06** `link_quote_from_requirement` 先读需求，再把 requirement_id 和可选 opportunity_id 写入报价。
7. **RT-R07** 直转报价随后覆盖 requirement.quote_id，并尝试追加 `requirement_links(entity_type='quote', link_role='direct')`。
8. **RT-R08** 样品转报价读取 sample.requirement_id/opportunity_id，写 quote 的 sample/requirement/opportunity 追溯。
9. **RT-R09** 样品转报价若有 requirement_id，覆盖 requirement.quote_id，并尝试追加 from_sample quote link。
10. **RT-R10** Quote→Sales Order 复制 quote.requirement_id/opportunity_id，覆盖 requirement.sales_order_id，并尝试追加 from_quote order link。
11. **RT-R11** requirement 头字段是最后写入的单值指针；`requirement_links` 可保存多个历史关系。
12. **RT-R12** 重复从同一需求生成报价时，quote_id 指向最新报价，而 links/下游查询可同时列出多条报价。
13. **RT-R13** `_safe_update` 只写目标表实际存在且 value 非空的列；缺列时无错误返回。
14. **RT-R14** `_fetchone` 查询异常返回空对象；link helper 随即静默返回。
15. **RT-R15** requirement_links 追加被 try/except 吞掉；报价/订单主体动作可成功但关系行缺失。
16. **RT-R16** `_safe_update` 每次可独立 commit，跨多表传播没有显式单一事务。
17. **RT-R17** Requirement360 同时按头指针和反向 requirement_id 查询，并用 `OR` 聚合报价/订单。
18. **RT-R18** 样品列表先按 requirement.sample_id 取一条，再追加按 samples.requirement_id 取多条，未去重。
19. **RT-R19** Requirement360 的 customer feedback 固定空列表；追溯面板不能证明反馈已实现。
20. **RT-R20** timeline 从聚合结果构造展示，不是独立、不可变审计台账。
21. **RT-R21** Quotation 普通创建只有显式 requirement_id 时调用 direct link；未传该字段的报价不自动推断需求。
22. **RT-R22** `requirement_links` 虽被 Requirement360 读取，但 lifecycle upstream/downstream 面板以反向字段查询为主，不把 links 当导航权威。
23. **RT-R23** `copy_quote` 的极简 INSERT 不复制 sample_id、requirement_id、opportunity_id，复制报价会丢失这组三类追溯。
24. **RT-R24** `apps/sample` 的 `sample_requirements` 是样品技术参数子表，不等于 `business_requirements`，保存它不会触发 lifecycle 绑定。

## 流程

### 需求直转报价

1. Requirement360 CTA 打开报价中心，并把 requirement_id/customer_id 放入查询参数。
2. 报价创建表单需实际保留并提交 requirement_id。
3. Quotation 服务创建报价头。
4. 若 requirement_id > 0，调用 direct link。
5. workflow 条件写 quotes.requirement_id/opportunity_id。
6. 覆盖 business_requirements.quote_id。
7. 尝试追加 direct requirement_link；失败可静默。

### 需求→样品→报价

1. 先通过未明确暴露的调用点将 sample 与 requirement 双向绑定。
2. Sample 转 Quote 时读取 sample 上的 requirement/opportunity。
3. 写 quote 追溯并覆盖 requirement.quote_id。
4. 尝试追加 from_sample link。

### 报价→订单

1. 读取 quote 的 requirement/opportunity。
2. 条件写 sales_order 反向字段。
3. 覆盖 requirement.sales_order_id。
4. 尝试追加 from_quote link。

## 校验（强/弱/缺失）

1. **RT-V01（弱/条件列）** 写前用 PRAGMA 检查目标列存在。
2. **RT-V02（缺失）** helper 返回 None，不向调用方报告哪些列未写。
3. **RT-V03（弱/存在性）** link_quote_from_requirement 查不到需求时直接返回。
4. **RT-V04（缺失）** 报价主体成功后未校验 requirement 追溯是否完整。
5. **RT-V05（缺失）** requirement_links 失败被吞掉，无用户错误或补偿队列。
6. **RT-V06（缺失）** 头指针、反向字段与 link 行之间没有一致性约束。
7. **RT-V07（缺失）** requirement_links 没有 `(requirement_id,entity_type,entity_id,role)` 唯一约束，可重复追加。
8. **RT-V08（缺失）** 同一需求多个报价/订单没有主关系选择校验。
9. **RT-V09（缺失）** 传播没有显式跨表事务或 rollback。
10. **RT-V10（缺失）** link_sample_to_requirement 不验证 sample 与 requirement 客户一致。
11. **RT-V11（缺失）** 未见 sample 绑定路由的权限和存在性校验，因为调用入口未找到。
12. **RT-V12（弱/聚合）** Requirement360 查询异常返回空列表，使页面可用但会隐藏缺表/SQL错误。
13. **RT-V13（缺失）** 聚合样品列表未按 id 去重。
14. **RT-V14（缺失）** 下游对象删除/取消后不清除需求头指针或 link 行。
15. **RT-V15（缺失）** copy_quote 完成后不校验或恢复来源需求/样品/商机追溯。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `business_requirements.sample_id` | 单值样品快捷指针，可能被后写覆盖 |
| `business_requirements.quote_id` | 单值报价快捷指针，重复报价时指向最新写入 |
| `business_requirements.sales_order_id` | 单值订单快捷指针 |
| `samples.requirement_id` | 样品→需求反向追溯 |
| `samples.opportunity_id` | 样品→商机反向追溯；sample helper 本身不写 |
| `quotes.sample_id` | 报价来源样品 |
| `quotes.requirement_id` | 报价来源需求 |
| `quotes.opportunity_id` | 从需求或样品传播的商机 |
| `sales_orders.requirement_id` | 从报价复制的需求 |
| `sales_orders.opportunity_id` | 从报价复制的商机 |
| `requirement_links.requirement_id` | 多值关系的需求端 |
| `requirement_links.entity_type` | quote、sales_order、document 等下游类型 |
| `requirement_links.entity_id` | 下游记录 id |
| `link_role=direct` | 需求直接生成报价 |
| `link_role=from_sample` | 经样品生成报价 |
| `link_role=from_quote` | 经报价生成订单 |
| `updated_at` | 下游指针覆盖时的需求更新时间 |
| `quotations/sales_orders/samples` | Requirement360 聚合列表，不等同单值头指针 |
| `timeline` | 根据当前聚合结果临时构造的展示事件 |
| `traceability_columns` | workflow status API 对部分反向列的存在性探针 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| direct | 需求直接到报价的 link role |
| from_sample | 样品转报价形成的 link role |
| from_quote | 报价转订单形成的 link role |
| linked | 有字段或 link 关系的语义，不是业务状态 |
| silent degrade | 缺表/缺列/异常时跳过追溯，但主体动作可继续 |
| quoted | 需求状态常量；workflow 只写 quote_id，不自动写此状态 |
| ordered | 需求状态常量；workflow 只写 sales_order_id，不自动写此状态 |
| schema_ready | 表能力探针，不保证每个扩展列/每条关系完整 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| RT-E01 | 需求头字段、关系表和下游扩展列 | 强 | `database/business_lifecycle_schema.py` |
| RT-E02 | 条件列、静默读取、三类 link helper | 强 | `v15/business_lifecycle/workflow.py` |
| RT-E03 | requirement_links 增查与无唯一约束调用 | 强 | `v15/business_lifecycle/repository.py` |
| RT-E04 | Requirement360 头指针+反向字段聚合与空列表降级 | 强 | `v15/business_lifecycle/requirement360.py` |
| RT-E05 | lifecycle panel 对跨对象关系做查询投影 | 中 | `v15/business_lifecycle/context360.py` |
| RT-E06 | 普通报价仅在显式 requirement_id 时调用 direct helper | 强 | `apps/quotation/services.py`、`apps/quotation/router.py` |
| RT-E07 | 样品转报价调用 from_sample helper并吞异常 | 强 | `apps/quotation/services.py` |
| RT-E08 | Sample 应用未找到 link_sample_to_requirement 调用点 | 强（缺失证据） | `apps/sample/` |
| RT-E09 | Requirement360 CTA 仅通过 query 参数引导报价创建 | 强 | `templates/business/requirement360.html` |
| RT-E10 | 转样报价不自动建行、不更新样品状态 | 强（交叉） | `docs/knowledge/legacy-extract/sample-deepen/sample_to_quote.md` |
| RT-E11 | workflow status API 只探测三个 requirement_id 列 | 强 | `v15/business_lifecycle/routes.py` |
| RT-E12 | copy_quote 未复制三类 lifecycle 外键 | 强 | `apps/quotation/repository.py`、`apps/quotation/services.py` |
| RT-E13 | sample_requirements 保存路径与 business requirement 分离 | 强（边界） | `apps/sample/services.py`、`apps/sample/repository.py` |
| RT-E14 | SO 转换调用 from_quote helper，失败可静默 | 强 | `apps/sales/services.py` |

## UNKNOWN + 已查路径

1. **`link_sample_to_requirement` 在生产是否由未纳入仓库的外部入口调用 UNKNOWN。** 已查路径：v15 lifecycle、apps/sample、apps/customer、templates、reports。
2. **一个需求允许关联多少个样品及哪个是 primary UNKNOWN。** 已查路径：单值 sample_id、samples.requirement_id 查询、Requirement360。
3. **一个需求多个报价时 quote_id 的业务含义是否“最新/主报价” UNKNOWN。** 已查路径：workflow、Requirement360、Quotation 和 reports。
4. **重复 requirement_links 是否已经存在于生产数据 UNKNOWN。** 已查路径：schema、repository、三个 link helper；未读取生产数据。
5. **追溯 helper 失败是否由全局日志捕获 UNKNOWN。** 已查路径：workflow try/except、Quotation 调用、logging/audit。
6. **跨表部分提交后的补偿或重试机制 UNKNOWN。** 已查路径：workflow、repository、background jobs、docs/reports。
7. **下游删除后需求头/link 如何清理 UNKNOWN。** 已查路径：sample/quotation/order 删除流程、workflow、schema。
8. **quoted/ordered 状态应由追溯建立自动推进还是人工更新 UNKNOWN。** 已查路径：constants、update_requirement_status、workflow、templates。
9. **需求与样品/报价客户不一致是否允许 UNKNOWN。** 已查路径：link helpers、Sample/Quotation create、Requirement360。
10. **requirement_links 与反向字段谁是审计权威 UNKNOWN。** 已查路径：schema、context360、requirement360、reports。
11. **扩展列 ALTER 失败时 status API 是否足以暴露缺口 UNKNOWN。** 已查路径：schema `_add_column`、workflow status route、readiness reports。
12. **复制报价是否应继承全部来源追溯 UNKNOWN。** 已查路径：copy_quote service/repository、workflow、Quote360 与 reports。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\workflow.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\requirement360.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\context360.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\business_lifecycle_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\business\requirement360.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
