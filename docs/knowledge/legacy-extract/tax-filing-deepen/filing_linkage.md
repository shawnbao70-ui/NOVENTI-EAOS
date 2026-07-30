# 报税 / 申报期间 / 税号联动有无

## Scope 与结论

本页回答：Legacy 是否存在报税（filing）、申报期间（tax/filing period）、以及税号与税码/单据/台账的联动。必查 `apps/finance`、tax 关键词、NDE、templates、business_modules、docs/reports。

**结论：** **无**活动报税引擎、**无**申报期间实体、**无**税号驱动选税或汇总申报闭环。可见残留是：`tax_records` 手工/测试台账、`tax_settings` 字典、`brand_profiles.tax_number` 与 NDE `customer.tax_number` 展示槽、国家 profile `tax_fields` 字段名意图。Tax Center 不是 VAT/GST 申报中心。`customers` 启动 DDL **无** `tax_number` 列（与品牌税号分离）。

## 业务规则（稳定 ID）

1. **FLK-R01** 未观察到名为 filing / tax return / VAT return / GST return / 申报 的路由、作业或表。  
2. **FLK-R02** 未观察到 `filing_period` / `tax_period` / `period_start` / `period_end` 财务税务期间实体。  
3. **FLK-R03** `tax_records.tax_date` 是记录日期文本，**不是**明确的税期/申报期起止。  
4. **FLK-R04** `/tax_center` 仅 `SELECT * FROM tax_records ORDER BY id DESC` 列表；无期间过滤、无汇总、无提交申报动作。  
5. **FLK-R05** `/add_test_tax` 写入固定 `tax_no`/`VAT`/`1500`/`Pending`，不绑定期间、主体税号或来源单据。  
6. **FLK-R06** `tax_settings` 与 `tax_records` 无外键或税码关联；`tax_type` 为自由文本。  
7. **FLK-R07** `brand_profiles.tax_number` 是公司/品牌身份字段；打印可显示「Tax ID」。  
8. **FLK-R08** NDE `customer.tax_number` 来自 `extra.get("customer_tax","")` —— 展示槽，非主数据强制联动。  
9. **FLK-R09** `customers` 启动 DDL（legacy_support 客户表段）未见 `tax_number` 列；客户税号不在该 DDL 段落库。  
10. **FLK-R10** country profile 可为各国声明 `tax_fields`（如 `npwp`/`gstin`/`sst`/`vat_trn`）—— **字段名意图**，未见申报校验引擎消费。  
11. **FLK-R11** `business_modules/finance.md` 职责列出发票/收付/报表；**未**列报税、税期关闭或税务机关接口。  
12. **FLK-R12** docs/reports 中 Finance/Tax 叙述停留在 Tax Center 路由存在与「Financial control 含 Tax」战略层；**无**申报闭环验收。  
13. **FLK-R13** Tax capability 仅 health/permissions；无 filing action。  
14. **FLK-R14** 进项/销项抵扣、零申报、更正申报、税务会计科目 —— 均未建模。  
15. **FLK-R15** `tax_records.status` 页面仅特判 `Pending` vs 其他（展示为完成风格）；无 Filed/Submitted/Accepted 状态机证据。  
16. **FLK-R16** EAOS 不得把「税号展示」或「Tax Center 列表」解释为已实现申报合规模块。  

## 联动矩阵（有 / 无）

| 联动 | 有无 | 证据形态 |
|---|---|---|
| 税号 → 自动选税码 | 无 | 无匹配逻辑 |
| 税号 → 单据强制校验 | 无 | customers DDL 无税号；NDE 可选展示 |
| 品牌税号 → 报税主体登记 | 展示有 / 申报无 | brand_profiles + print |
| 单据 → tax_records 过账 | 无 | 仅测试插入 |
| tax_records → 申报期间汇总 | 无 | 无期间实体 |
| 申报期间关闭 → 禁止改税 | 无 | 无期间状态机 |
| 国家 tax_fields → 校验必填 | 意图槽 | country_templates |
| Tax Center → 提交税务机关 | 无 | 只读列表 + 测试写 |

## 流程（缺失汇合）

1. 用户可在 Tax Center 看到独立 `tax_records` 行。  
2. 用户可点测试按钮插入固定 VAT 行。  
3. 打印层可显示品牌 Tax ID 与（若注入）客户税号。  
4. **缺失：** 选择申报期 → 拉取销项/进项 → 校验税号/税码 → 生成申报表 → 提交/回执 → 关账。  
5. 因此报税联动在 Legacy 中应记为**强缺口**。  

## 校验（强 / 弱 / 缺失）

1. **FLK-V01（强缺口）** 申报前必须存在 Open 税期 —— 无期间实体。  
2. **FLK-V02（缺失）** 报税主体税号必填且格式合法（各国规则）。  
3. **FLK-V03（缺失）** 客户/供应商税号与交易方国家一致。  
4. **FLK-V04（缺失）** 申报金额必须等于期间内税票/台账汇总。  
5. **FLK-V05（缺失）** `tax_records` 必须引用 source document。  
6. **FLK-V06（缺失）** 已提交期间禁止静默改数。  
7. **FLK-V07（违反）** `/add_test_tax` GET 写库；非受控申报写入。  
8. **FLK-V08（弱/展示）** Pending 徽标存在；无 Filed 生命周期。  
9. **FLK-V09（缺失）** 进销项抵扣勾稽。  
10. **FLK-V10（缺失）** 多国家并行申报日历与截止日。  
11. **FLK-V11（弱/意图）** country `tax_fields` 可提示应展示字段名，不构成校验。  
12. **FLK-V12（缺失）** 税号变更审计与历史版本。  

## 数据含义

| 数据 / 概念 | Legacy 含义 |
|---|---|
| Filing / tax return | **未建模** |
| Filing period / tax period | **未建模** |
| `tax_records.tax_date` | 台账日期，非税期 |
| `tax_records.tax_no` | 事项编号（测试路径可写死） |
| `tax_records.status` | 台账标签；非申报状态机 |
| `tax_settings.country_code` | 字典国家；不驱动申报日历 |
| `brand_profiles.tax_number` | 品牌/公司税号展示与主数据 |
| NDE `customer.tax_number` | 打印身份槽（extra 注入） |
| `customers.tax_number` | **启动客户 DDL 段未见** |
| country `tax_fields` | 模板字段名意图列表 |
| `legal_footer_key`（如 `cn_vat`） | 页脚法务文案键意图 |
| Tax Center | `tax_records` 列表 UI |
| `/add_test_tax` | 固定测试写入，非报税 |
| Tax capability | health/bridge 脚手架 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| FLK-E01 | tax_records DDL 无期间/税号/来源 | 强 | `runtime/v14/legacy_support.py`（~1488–1504） |
| FLK-E02 | Tax Center 只读列表 | 强 | `apps/finance/finance_ops_pages.py`、`templates/tax_center.html` |
| FLK-E03 | 测试税插入固定值 | 强 | `apps/finance/finance_ops_pages.py`（`/add_test_tax`） |
| FLK-E04 | brand tax_number | 强 | `runtime/v14/legacy_support.py` brand_profiles；`apps/brand_center/` |
| FLK-E05 | NDE customer tax_number 槽 | 强 | `document/nde_engine.py`；`templates/print/blocks/03_customer.html` |
| FLK-E06 | customers DDL 无 tax_number | 强缺席 | `runtime/v14/legacy_support.py`（customers ~671–697） |
| FLK-E07 | country tax_fields stubs | 中 | `document/country_templates.py` |
| FLK-E08 | finance 模块规格无报税交付 | 中 | `business_modules/finance.md` |
| FLK-E09 | reports 仅登记 Tax Center 路由/战略 | 中 | `docs/reports/Enterprise_Module_Recovery_Report.md`、`V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| FLK-E10 | apps 层 filing/tax_period/vat_return 检索无活动命中 | 强缺席 | `apps/**`、`docs/reports/**` 关键词检索 |
| FLK-E11 | locale-commerce 已声明无申报期 | 强 | [`../locale-commerce/tax.md`](../locale-commerce/tax.md) |

## UNKNOWN + 已查路径

1. **是否存在库外 Excel/人工报税 SOP 替代系统 UNKNOWN。** 已查：Tax Center、finance services、business_modules、docs/reports。  
2. **生产库是否手工 ALTER customers 增加税号列 UNKNOWN。** 已查：启动 DDL customers 段；未读生产 schema drift。  
3. **brand tax_number 是否被任何合规导出作业读取 UNKNOWN。** 已查：brand_center schemas/repository、NDE print identity；未见申报导出。  
4. **未来税控/电子发票接口是否在保留文档中规划 UNKNOWN。** 已查：business_modules/finance Future Scope、tax capability README、constitution 多税制原则（原则≠实现）。  
5. **collection_tasks 或其他财务表是否隐式承载税期 UNKNOWN。** 已查：finance_ops_pages collection_center、tax_records 结构；无税期字段。  
6. **locales 文案是否含「申报」UI 词但无后端 UNKNOWN。** 已查：Tax Center 模板键与 apps 路由；无 filing 路由。  
7. **多租户下税号是否存于 tenant 配置而非 brand_profiles UNKNOWN。** 已查：brand_profiles、finance、platform-obs 交界关键词；本页不断言租户税籍引擎。  

## 只读来源路径

`apps/finance/finance_ops_pages.py` · `templates/tax_center.html` · `runtime/v14/legacy_support.py` · `apps/brand_center/` · `document/nde_engine.py` · `document/country_templates.py` · `templates/print/blocks/_company_identity.html` · `templates/print/blocks/03_customer.html` · `core/capabilities/tax/` · `business_modules/finance.md` · `docs/reports/` · `docs/knowledge/legacy-extract/locale-commerce/tax.md`
