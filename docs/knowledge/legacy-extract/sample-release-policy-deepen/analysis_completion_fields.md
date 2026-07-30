# 统一分析完成字段与子表推断

## Scope与证据强度

本页逐表核验 completion/is_complete/completed_at/status 字段，并区分持久状态与 Object360 shadow 推断。结论：没有统一 completion 字段；存在性推断不写回主表，且 analyzed 的文档与代码定义不一致。基础规则见 [`../sample-gate-deepen/analysis_completion.md`](../sample-gate-deepen/analysis_completion.md)。

## 业务规则（稳定ID）

1. **ACF-R01** samples 无 analysis_complete、is_complete、completed_at 或统一 analysis_status。
2. **ACF-R02** sample_measurements 无完成字段。
3. **ACF-R03** sample_material_analysis 无完成字段。
4. **ACF-R04** sample_quality_assessment 无完成字段。
5. **ACF-R05** sample_supplier_matching 无完成字段。
6. **ACF-R06** samples.status 只承载 New/Stocked 等业务标签，不表示分析完成。
7. **ACF-R07** 测量、材料和质量保存均追加记录。
8. **ACF-R08** 测量、材料和质量读取以最大 id 的一条作为当前展示。
9. **ACF-R09** 供应商匹配保留多行，没有 current/approved 标志。
10. **ACF-R10** Shadow `measured` 由 measurement 非空推断。
11. **ACF-R11** Shadow `analyzed` 仅由 quality_assessment 非空推断。
12. **ACF-R12** 文档声明 material 或 quality 均可 analyzed，与代码不一致。
13. **ACF-R13** Shadow `matched` 由 supplier_matching 至少一行推断。
14. **ACF-R14** measured/analyzed/matched 都不写回 samples.status。
15. **ACF-R15** 子表有行只代表保存过，不证明字段完整、审核通过或完成。
16. **ACF-R16** 分析 POST 可写默认 0/空值，存在性推断不会识别低质量记录。
17. **ACF-R17** 当前 sample 模板无四类分析录入 form，数据来源可能是 API、历史或脚本。
18. **ACF-R18** Object360 runtime 只在普通详情尝试 attach，Sample360 主页面未以它作为权威 completion。
19. **ACF-R19** materialize 与 create_quote_from_sample 都不读取 completion。
20. **ACF-R20** sample_dashboard_statistics 是子表行数，不是完成率。

## 流程

1. 样品以 New 创建。
2. 每次分析保存向独立子表追加一行。
3. 服务取最新记录或全部供应商候选用于展示。
4. Object360 按“是否有行”计算 shadow stage。
5. 计算结果不持久化，也不回写 samples.status。
6. 文档与代码对 material analysis 是否算 analyzed 存在冲突。
7. 后续入库/转报价不消费统一完成字段，因为该字段不存在。

## 校验（强/弱/缺失）

1. **ACF-V01（强/DDL）** 五张相关表均可确认无 completion 类字段。
2. **ACF-V02（弱/类型）** 部分 Form 做数值类型转换。
3. **ACF-V03（缺失）** 未定义四类分析必须全部完成。
4. **ACF-V04（缺失）** 未定义各类最小必填字段。
5. **ACF-V05（缺失）** 未定义 completed_by/completed_at。
6. **ACF-V06（缺失）** 未定义审核、批准、作废和 is_current。
7. **ACF-V07（缺失）** Shadow 推断只看行存在，不看字段质量。
8. **ACF-V08（缺失）** analyzed 声明/代码冲突无一致性校验。
9. **ACF-V09（缺失）** 入库不校验 completion。
10. **ACF-V10（缺失）** 转报价不校验 completion。
11. **ACF-V11（缺失）** 多版本记录没有有效版本约束。
12. **ACF-V12（缺失）** dashboard 行数不能验证单样品完成度。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.status` | New/Stocked 主状态，不是 completion |
| `sample_measurements` | 测量历史容器 |
| `sample_material_analysis` | 材料分析历史容器 |
| `sample_quality_assessment` | 质量评价历史容器 |
| `sample_supplier_matching` | 多行供应商候选 |
| `measurement` | 最新测量上下文 |
| `material_analysis` | 最新材料上下文 |
| `quality_assessment` | 最新质量评价上下文 |
| `supplier_matching` | 全部候选列表 |
| `measured` | 有测量行的 shadow stage |
| `analyzed` | 代码按质量评价存在推断 |
| `matched` | 有供应商匹配的 shadow stage |
| `current_stage` | 计算投影，非数据库字段 |
| `mode=shadow` | 不写回 Legacy 的运行模式 |
| `sample_dashboard_statistics` | 子表 COUNT |
| `Stocked` | 入库结果，不是分析完成 |
| `Draft` | 可在无 completion 时创建的报价状态 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| New | 样品初始状态 |
| measured | Shadow 推断 |
| analyzed | Shadow 推断，声明/实现分裂 |
| matched | Shadow 推断 |
| complete | 未持久化 |
| is_current | 未建模 |
| Stocked | 库存过账结果 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| ACF-E01 | samples 与四子表无 completion 字段 | 强 | `runtime/v14/legacy_support.py` |
| ACF-E02 | 四类分析追加写且不改 status | 强 | `apps/sample/services.py` |
| ACF-E03 | POST Form 默认和唯一 supplier_id 必填 | 强 | `apps/sample/router.py` |
| ACF-E04 | Shadow stage 按上下文存在性推断 | 中/计算 | `core/object360/sample/sample_integration.py`、`sample_lifecycle.py` |
| ACF-E05 | 文档把 material 也定义为 analyzed | 中/冲突 | `docs/sample/Sample360_Lifecycle.md` |
| ACF-E06 | Sample360 服务不使用 shadow completion 权威 | 强 | `apps/sample/services.py` |
| ACF-E07 | sample 模板无四类分析 form | 强（缺失证据） | `templates/sample*.html` |
| ACF-E08 | materialize/can_materialize 不读分析表 | 强 | `apps/sample/services.py` |
| ACF-E09 | 转报价不读分析表 | 强 | `apps/quotation/services.py` |
| ACF-E10 | A-005/A-017 未定义 completion gate | 强 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md`、`Business_Strong_A017_Sample_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **统一完成是否要求四类记录全部存在 UNKNOWN。** 已查路径：Sample service、Object360、docs/sample、reports。
2. **测量完整字段、单位和公差 UNKNOWN。** 已查路径：DDL、Form、templates、business_modules。
3. **材料分析是否应触发 analyzed UNKNOWN。** 已查路径：生命周期文档与代码。
4. **质量等级何时代表分析完成 UNKNOWN。** 已查路径：assessment、overall_grade、quality-compliance。
5. **供应商匹配是否是 completion 必需条件 UNKNOWN。** 已查路径：matching 表、shadow stage、Sample360。
6. **历史多版本哪条被正式批准 UNKNOWN。** 已查路径：ORDER BY、DDL、审批/审计模块。
7. **外部实验室是否维护 completion UNKNOWN。** 已查路径：integrations、v15/core、business_modules。
8. **Sample360 是否计划接入 Object360 completion bundle UNKNOWN。** 已查路径：Sample service、integration attach、templates。
9. **completion 未来是否应阻断 Stock/Quote UNKNOWN。** 已查路径：materialize、quotation、reports、邻包。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample*`
- `H:\Workspace\EZAM_CRM - 9.0\docs\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
