# 收样创建、客户绑定、编号与 New

## Scope与证据强度

本页只深化样品主记录的入口事实。权威概览交叉引用 [`../sample/sample.md`](../sample/sample.md)。创建服务、列表模板与 DDL为强证据；客户有效性、编号唯一性、重复收样和权限闭环证据不足。

Legacy 入口更接近“收到客户样品并登记”，因为创建时保存 `receive_date` 和 `New`，而不是“向客户申请/发样”。

## 业务规则（稳定ID）

1. **SI-R01** 样品中心创建表单只明确提交 `customer_id`，其余主记录信息不在该入口采集。
2. **SI-R02** 样品编号由服务生成：`SP` 前缀加应用服务器当前年月日时分秒。
3. **SI-R03** 收样日期由服务器写为创建当天日期，不接受用户在创建表单修改。
4. **SI-R04** 新记录状态固定写为 `New`。
5. **SI-R05** 创建成功后立即提交，并重定向到 `/sample/{id}` 详情。
6. **SI-R06** 样品列表把 `samples.customer_id` 左连接客户表，显示客户公司名称。
7. **SI-R07** 列表按样品 id 倒序，不按 receive_date 或编号排序。
8. **SI-R08** 页面按状态文本归类 KPI：包含 Stocked 计已入库，New/空值计开放，其余计其他。
9. **SI-R09** 创建按钮和表单仅在 UI 上受 `Samples.add` 控制；POST `/add_sample` 未见对应服务端权限检查。
10. **SI-R10** `validate_sample` 只声明 customer required，但活动创建路径未显式调用该 validator。
11. **SI-R11** `samples` 在 Legacy 初始化中出现两次不同 CREATE 定义；SQLite 首个已存在定义会使后一个定义不生效，运行列形态依赖历史初始化/迁移。
12. **SI-R12** `core/sample` 仅声明领域 slug、主表、版本及基础表 metadata，不定义收样业务状态机。
13. **SI-R13** 创建时不写 `sample_logs`；未见 Add 动作自动形成时间线日志。
14. **SI-R14** New 只表示初始标签，未见从 New 到分析中/分析完成的正式转换。

## 流程

1. 用户打开 `/samples`；页面读取全部样品与客户选择列表。
2. 拥有 UI 添加权限时选择客户并提交。
3. 服务生成 SP 时间戳编号、当天日期和 New。
4. 写入 `samples(sample_no, customer_id, receive_date, status)`。
5. 提交后进入样品详情；后续测量、图片、产品绑定、入库和转报价均为独立动作。

### 入口边界

创建阶段不采集样品名称、类型、客户型号、需求数量、目标价、负责人、图片或测量；DDL 中出现这些字段并不代表当前表单会填入。

## 校验（强/弱/缺失）

1. **SI-V01（强/UI+类型）** `customer_id` 是必填表单和整数参数。
2. **SI-V02（弱）** validator 将缺 customer 视为错误，但创建服务未调用它。
3. **SI-V03（缺失）** POST 创建未见 `Samples.add` 服务端权限门。
4. **SI-V04（缺失）** 未见客户记录存在、Active 或当前租户归属校验。
5. **SI-V05（缺失）** 未见 `sample_no` 唯一约束；同一秒并发创建可能碰撞。
6. **SI-V06（缺失）** 未见重复样品识别（客户+型号+日期/图片指纹）。
7. **SI-V07（缺失）** 未见 receive_date 时区、未来日期或业务日规则。
8. **SI-V08（缺失）** 未见 New 状态枚举约束或状态转换校验。
9. **SI-V09（缺失）** 列表页面查询未见角色所有者过滤。
10. **SI-V10（缺失）** 创建写入未显式包含 tenant_id，端到端租户隔离未知。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.id` | 样品内部主键 |
| `sample_no` | SP+秒级时间戳的可读编号 |
| `customer_id` | 样品所属客户引用 |
| `customer_name` | 早期/替代 schema 的冗余文本；列表实际 join 客户表 |
| `receive_date` | 服务器创建当天的收样日期 |
| `status` | 样品当前文本标签，创建值 New |
| `remark` | 主记录备注字段；当前创建入口不填写 |
| `sample_name` / `sample_type` | 第一套 DDL字段，当前创建入口不填写 |
| `product_name` / `customer_model` | 第二套重复 DDL字段，实际是否存在取决于历史 schema |
| `demand_qty` / `target_price` | 第二套 DDL意图字段，不由当前入口填写 |
| `owner` | 第二套 DDL意图字段，不由当前入口填写 |
| `company_name` | 列表通过客户 join 得到的展示值 |
| `New` | 新收样初始状态 |

## 状态词汇

| 状态/词汇 | 含义 |
|---|---|
| `New` | 创建时固定初始状态 |
| `Stocked` | 后续样品入库成功状态 |
| 空状态 | 列表 KPI按开放/New处理 |
| other status | 列表能展示但没有正式枚举 |
| received | 由 receive_date 表达收样事实，不是确认的状态值 |
| pending/approved | UNKNOWN；未见收样审批状态机 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SI-E01 | 创建服务生成编号、日期和 New | 强 | `apps/sample/services.py` |
| SI-E02 | POST 入口只接 customer_id | 强 | `apps/sample/router.py` |
| SI-E03 | 创建 UI要求选择客户并按 Samples.add 隐藏 | 强 | `templates/samples.html` |
| SI-E04 | 列表左连客户并按 id 倒序 | 强 | `apps/sample/services.py` |
| SI-E05 | validator 只检查 customer required | 强但未接线 | `apps/sample/validator.py` |
| SI-E06 | samples 两次不同 CREATE 定义 | 强（风险） | `runtime/v14/legacy_support.py` |
| SI-E07 | core metadata 只列基础表和路由所有者 | 中 | `core/sample/metadata.py`、`sample.py` |
| SI-E08 | A-017 报告确认 hub、状态 KPI 与诚实边界 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |
| SI-E09 | 既有样品知识页将其判为收样链 | 强（交叉） | `../sample/sample.md` |

## UNKNOWN + 已查路径

1. **样品编号唯一性及冲突处理 UNKNOWN。** 已查路径：`apps/sample/services.py`、Legacy DDL、repository。
2. **客户必须 Active/可交易的规则 UNKNOWN。** 已查路径：Sample 创建、Customer schema/services、templates。
3. **当前生产数据库实际采用哪套 samples 列顺序 UNKNOWN。** 已查路径：两段 CREATE、迁移、Sample templates索引。
4. **创建动作是否在其他钩子写 sample_logs UNKNOWN。** 已查路径：`apps/sample/utils.py`、services、router、lifecycle enrichment。
5. **New 之后除 Stocked 外的正式状态与转换 UNKNOWN。** 已查路径：Sample全目录、templates、reports、状态常量。
6. **重复收样、退回和拒收规则 UNKNOWN。** 已查路径：Sample routes/services、business_modules、Sample报告。
7. **收样人、收样地点、承运单号和包裹数量 UNKNOWN。** 已查路径：samples DDL、创建表单、Sample360。
8. **创建 POST 的租户和后端权限保护 UNKNOWN。** 已查路径：Sample router/repository、tenant helpers、permission checker。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\core\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\samples.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A017_Sample_Ops_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
