# 样品分析完成判定与后续门禁

## Scope与证据强度

本页深化“分析何时算完成，以及未完成是否能入库或转报价”。四类分析表的追加写入和后续动作无门禁为强证据；Object360 的 measured/analyzed/matched 是 shadow 推断，不写回 `samples.status`。分析字段与展示细节交叉引用 [`../sample-deepen/sample_analysis.md`](../sample-deepen/sample_analysis.md)。

## 业务规则（稳定ID）

1. **AC-R01** samples 主表没有 analysis_complete、completed_at 或统一 analysis_status 字段。
2. **AC-R02** 测量保存向 sample_measurements 追加一行，不更新样品状态。
3. **AC-R03** 材料、质量和供应商分析分别向独立子表追加记录，不形成统一完成记录。
4. **AC-R04** 测量、材料和质量读取多以最新 id 记录为当前展示；旧记录仍保留。
5. **AC-R05** 供应商匹配可有多行，存在至少一行只代表已录入候选。
6. **AC-R06** Shadow lifecycle 以有测量行推断 `measured`。
7. **AC-R07** Shadow lifecycle 代码以有质量评价推断 `analyzed`。
8. **AC-R08** 生命周期文档声明材料或质量分析均可算 analyzed，与代码只看质量评价不一致。
9. **AC-R09** Shadow lifecycle 以供应商匹配非空推断 `matched`。
10. **AC-R10** 以上 measured/analyzed/matched 不写回 samples.status；主表可仍为 New。
11. **AC-R11** 四类 POST 路由存在，但当前 templates/sample* 未找到对应录入表单。
12. **AC-R12** 分析保存基本采用默认空值/0；“有行”不代表字段完整或结果有效。
13. **AC-R13** supplier_id 是供应商匹配 POST 的硬必填，其他分析缺少同等业务必填。
14. **AC-R14** product bind 不检查任何分析记录，可在未分析时执行。
15. **AC-R15** materialize 不读取测量、材料、质量或供应商表，未完成分析仍可 Stocked。
16. **AC-R16** create_quote_from_sample 不读取分析完成度，未完成仍可创建 Draft 空头报价。
17. **AC-R17** Sample360 Create Quote CTA 不受 analysis complete 条件控制。
18. **AC-R18** `can_materialize` 只由 product_id 与既有 Sample Receipt 推导。
19. **AC-R19** AI brief/next_actions 只给建议顺序，不构成服务端门禁。
20. **AC-R20** 样品列表只按 New/Stocked/其他 status 统计，不展示分析完成率。

## 流程

1. 新样品以 New 创建。
2. 用户可任选顺序调用测量、材料、质量、供应商保存端点。
3. 每次保存追加子表行；samples.status 不变。
4. Object360 可按数据存在性推断 shadow 阶段。
5. 页面/服务不计算统一 completion 百分比。
6. 即使四类记录全空，仍可绑定产品。
7. 已绑定后可 materialize；库存成功后 status 变 Stocked。
8. 无论分析是否完成，也可从 Sample360 创建 Draft 报价。

## 校验（强/弱/缺失）

1. **AC-V01（弱/类型）** 测量数值由 Form 类型转换，但默认 0。
2. **AC-V02（强/HTTP）** supplier matching 要求 supplier_id。
3. **AC-V03（缺失）** 未定义四类分析必须全部完成。
4. **AC-V04（缺失）** 未定义测量非零、单位、范围和公差。
5. **AC-V05（缺失）** 未定义材料分析必填字段或风险接受条件。
6. **AC-V06（缺失）** 未定义质量分数范围和 overall_grade 枚举。
7. **AC-V07（缺失）** 分析 POST 前未统一验证样品存在。
8. **AC-V08（缺失）** 未见完成确认人、完成时间或签名。
9. **AC-V09（缺失）** 入库不校验 completion。
10. **AC-V10（缺失）** 转报价不校验 completion。
11. **AC-V11（缺失）** Shadow stage 不验证记录字段质量，只看存在性。
12. **AC-V12（缺失）** 文档与代码的 analyzed 判定不一致且无一致性 gate。
13. **AC-V13（缺失）** 多版本记录无作废、审核或当前有效标志。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.status` | New/Stocked 等主业务标签，不表达分析完成 |
| `sample_measurements` | 测量记录容器 |
| `sample_material_analysis` | 材料组成、等级和风险描述 |
| `sample_quality_assessment` | 五维评分和人工综合等级 |
| `sample_supplier_matching` | 候选供应商、价格、MOQ、交期和评分 |
| `measurement` | Sample360 最新测量展示对象 |
| `material_analysis` | Sample360 最新材料分析对象 |
| `quality_assessment` | Sample360 最新质量评价对象 |
| `supplier_matching` | Sample360 供应商候选列表 |
| `measured` | 有测量行时的 shadow 阶段 |
| `analyzed` | 代码按质量评价存在推断的 shadow 阶段 |
| `matched` | 有供应商匹配时的 shadow 阶段 |
| `current_stage` | 计算投影，不是 samples 字段 |
| `can_materialize` | 已绑定产品且未入库；不含 completion |
| `sample_materialized` | 是否有 Sample Receipt 流水 |
| `Draft` | 未完成分析也可创建的报价状态 |
| `Stocked` | 入库结果，不是分析完成 |
| `sample_dashboard_statistics` | 各分析表行数，不是完成率 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| New | 样品主表初始状态 |
| measured | Shadow 数据存在阶段 |
| analyzed | Shadow 数据存在阶段；声明/实现不一致 |
| matched | Shadow 数据存在阶段 |
| complete | 未建模为持久状态 |
| Stocked | 库存过账完成 |
| Draft | 样品转出的报价初始状态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| AC-E01 | 四类分析均为追加写且不改 sample status | 强 | `apps/sample/services.py` |
| AC-E02 | 四类 POST 路由及其 Form 默认 | 强 | `apps/sample/router.py` |
| AC-E03 | 四张子表无 completion 字段 | 强 | `runtime/v14/legacy_support.py` |
| AC-E04 | Shadow 阶段按记录存在性推断 | 中/计算 | `core/object360/sample/sample_lifecycle.py` |
| AC-E05 | 文档把材料也纳入 analyzed | 中/声明偏差 | `docs/sample/Sample360_Lifecycle.md` |
| AC-E06 | Sample360 CTA 与 can_materialize 展示 | 强 | `templates/sample360.html` |
| AC-E07 | sample 模板无四类保存 form | 强（缺失证据） | `templates/samples.html`、`sample_detail.html`、`sample360.html` |
| AC-E08 | 转报价不读取分析表 | 强 | `apps/quotation/services.py` |
| AC-E09 | A-005 只验证库存和报价链 | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| AC-E10 | A-017 强调人工动作而非自动完成 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **分析完成是否要求四类记录全部存在 UNKNOWN。** 已查路径：Sample services/router、Object360 lifecycle、docs/sample、reports。
2. **测量完整的最小字段及单位 UNKNOWN。** 已查路径：measurement DDL、Form defaults、templates、business_modules。
3. **材料分析是否应触发 analyzed UNKNOWN。** 已查路径：Sample360_Lifecycle 文档与 sample_lifecycle 代码。
4. **质量评价何种等级才算完成/通过 UNKNOWN。** 已查路径：assessment DDL、save route、quality-compliance。
5. **供应商匹配是否是分析完成必需步骤 UNKNOWN。** 已查路径：supplier matching 表、Object360、Sample360。
6. **四类分析表单是否存在于未同步历史分支 UNKNOWN。** 已查路径：templates/sample*、备份模板、当前 routes。
7. **多条分析记录哪条经审核生效 UNKNOWN。** 已查路径：查询顺序、DDL、审计/审批模块。
8. **未完成样品是否在业务上应禁止报价或入库 UNKNOWN。** 已查路径：Quotation create、materialize、reports、邻包。
9. **completion 是否由外部实验室系统维护 UNKNOWN。** 已查路径：integrations、business_modules、docs/reports。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample*`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
