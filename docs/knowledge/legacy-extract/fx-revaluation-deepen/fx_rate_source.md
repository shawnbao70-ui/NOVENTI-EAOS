# 汇率来源 / 维护 / 生效日

## Scope 与结论

本页深化 [`../locale-commerce/currency.md`](../locale-commerce/currency.md) 的汇率治理缺口。Legacy 的 `currency_settings` 在运行时 DDL 中种子化若干币种与相对基准汇率；EOC 财务条带可读该表做展示快照。活动代码中**未见**汇率维护页面、UPDATE API、外部提供方接入、生效日/版本/买卖价、审批或自动刷新。`core/capabilities/currency` 仅暴露 health 与 formatter bridge，不是汇率服务。

## 业务规则（稳定 ID）

1. **FXS-R01** `currency_settings` 以 `currency_code` 唯一标识币种字典行。
2. **FXS-R02** 字典行保存 `currency_name`、`currency_symbol`、`exchange_rate`、`is_base`、`status`、`remark`、`create_time`、`update_time`。
3. **FXS-R03** 种子数据以 USD 为 `is_base=1` 且汇率 1；CNY/IDR/BDT/VND 为非基准并带固定种子汇率。
4. **FXS-R04** 种子写入使用 `INSERT OR IGNORE`，重复启动不会覆盖已有行上的人工或历史改动（若库中已有行）。
5. **FXS-R05** `system_parameters` 另有 `DEFAULT_CURRENCY=USD` 种子，与字典并列，不是单一权威写路径。
6. **FXS-R06** 品牌档案可保存 `currency`；新报价默认链可读取活动品牌币种，但**不**从 `currency_settings` 取活汇率。
7. **FXS-R07** 新报价默认链优先级：最近客户报价商业头 → 品牌币种 → 平台字面量 USD/1.0（禁止虚构 FX）。
8. **FXS-R08** EOC `format_exchange_snapshot` 从 `currency_settings` 读 Active 行，拼 `BASE/CODE rate` 展示字符串。
9. **FXS-R09** EOC 汇率展示失败时回退文案为 “Configure currency rates in Administration”，**不**证明存在管理端维护实现。
10. **FXS-R10** `get_currency_list()` 返回硬编码币种代码列表，与字典表无强制同步。
11. **FXS-R11** `core/capabilities/currency` 的 HTTP 片段仅 `/currency/health`，无 rate CRUD。
12. **FXS-R12** 独立价格试算的 `exchange_rate` 为表单手输浮点，不读、不写 `currency_settings`。
13. **FXS-R13** 字典表无 `effective_from` / `effective_to` / `rate_date` / `provider` / `bid` / `ask` / `version` 列。
14. **FXS-R14** 全库活动路径未见对 `currency_settings` 的 `UPDATE`（除备份副本中的同类种子逻辑）。
15. **FXS-R15** i18n formatter 只做符号与数字展示，不执行换算，不校验代码是否在字典中。

## 校验（强 / 弱 / 缺失）

1. **FXS-V01（强）** `currency_code` UNIQUE（schema）。
2. **FXS-V02（弱）** `status` 默认 Active；EOC 查询允许 `status IS NULL`。
3. **FXS-V03（弱）** EOC 拼展示时跳过 `exchange_rate <= 0` 的非基准行。
4. **FXS-V04（缺失）** 恰好一个 `is_base=1` 的唯一约束。
5. **FXS-V05（缺失）** 基准币汇率必须为 1。
6. **FXS-V06（缺失）** 汇率必须大于零（字典写入路径）。
7. **FXS-V07（缺失）** 生效日区间不重叠 / 按日取价。
8. **FXS-V08（缺失）** 外部提供方签名、来源审计、审批后生效。
9. **FXS-V09（缺失）** 停用币种禁止新单据引用。
10. **FXS-V10（缺失）** ISO 长度、小数位与舍入规则绑定币种。
11. **FXS-V11（缺失）** 买卖价差与中间价选用策略。
12. **FXS-V12（缺失）** capability 层权限覆盖 rate 维护（仅有 `capability.currency.use` 脚手架）。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `currency_settings.currency_code` | 币种字典键（如 USD/CNY） |
| `currency_name` | 展示名称 |
| `currency_symbol` | 展示符号，非唯一标识 |
| `exchange_rate`（字典） | 相对基准的配置数值；无方向正式声明，仅由价格试算“原币÷汇率=USD”间接暗示 |
| `is_base` | 基准币标记；无唯一保证 |
| `status` | Active 等；不等于“今日有效汇率” |
| `create_time` / `update_time` | 行时间戳；不是汇率生效日 |
| `DEFAULT_CURRENCY` | 系统参数默认币种字面量 |
| 品牌 `currency` | 公司/品牌默认币种候选，无伴随汇率 |
| 平台默认 `exchange_rate=1.0` | 字面量回退，非市场汇率 |
| EOC `exchange_rate` 字符串 | 展示快照，非会计事实 |
| `get_currency_list()` | UI/辅助硬编码列表 |
| capability health | 能力可用探针，无业务汇率语义 |
| 价格试算 `exchange_rate` | 会话级手输，不落主数据 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| FXS-E01 | `currency_settings` DDL 与列集合 | 强 | `runtime/v14/legacy_support.py`（Currency Settings 段） |
| FXS-E02 | USD/CNY/IDR/BDT/VND 种子与 `INSERT OR IGNORE` | 强 | 同上 |
| FXS-E03 | `DEFAULT_CURRENCY` 系统参数种子 | 强 | `runtime/v14/legacy_support.py`（Settings Center） |
| FXS-E04 | EOC 读字典拼展示快照 | 强 | `v15/template_services/_helpers.py` |
| FXS-E05 | EOC financial command 使用 snapshot | 强 | `v15/template_services/eoc.py` |
| FXS-E06 | capability 仅 health/bridge | 强 | `core/capabilities/currency/` |
| FXS-E07 | 报价默认链禁止虚构 FX | 强 | `v15/ux/master_defaults.py` |
| FXS-E08 | 硬编码币种列表 | 强 | `runtime/v14/legacy_support.py` `get_currency_list` |
| FXS-E09 | 审计称“表 + capability scaffold” | 中 | `docs/reports/audit/07_I18N_AUDIT.md` |
| FXS-E10 | PRODUCT_EXCELLENCE 称 EOC 读字典而非静态率 | 中 | `docs/reports/PRODUCT_EXCELLENCE.md` |
| FXS-E11 | 全库无 `UPDATE currency_settings` 活动路径 | 强缺口 | 检索 `apps/`、`templates/`、`v15/`、`core/` |
| FXS-E12 | `business_modules/finance.md` 无汇率维护职责 | 中 | `business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **生产库是否曾手工 SQL 改过 `currency_settings.exchange_rate` UNKNOWN。** 已查：活动 UPDATE 路径、Finance/Admin 路由、templates；未读生产库。
2. **“Administration” 文案是否对应未合入分支或外部工具 UNKNOWN。** 已查：templates 币种设置页、settings 路由、`currency_settings` 维护表单。
3. **是否存在外部汇率 API / webhook / 批处理导入 UNKNOWN。** 已查：`apps/finance/`、`core/capabilities/currency/`、integration 模块名、`docs/reports/GTFIP.md` 保留接口叙述。
4. **买卖价、中间价政策 UNKNOWN。** 已查：DDL 列、pricing/finance 服务、reports。
5. **多公司/多租户是否各有独立汇率表 UNKNOWN。** 已查：`currency_settings` DDL、tenant schema 叙述、`docs/reports/MULTI_COMPANY_ARCHITECTURE.md`。
6. **历史汇率是否保留在审计日志 UNKNOWN。** 已查：audit_center、currency 事件、`update_time` 用法。
7. **种子汇率 7.20/16500 等是否代表某日市场 UNKNOWN。** 已查：种子注释、docs；无日期标注。

## 只读来源路径

`runtime/v14/legacy_support.py` · `core/capabilities/currency/` · `v15/template_services/_helpers.py` · `v15/template_services/eoc.py` · `v15/ux/master_defaults.py` · `core/i18n/formatter.py` · `apps/finance/finance_ops_pages.py` · `templates/product_pricing_engine.html` · `business_modules/` · `docs/reports/` · 邻包 [`../locale-commerce/currency.md`](../locale-commerce/currency.md)
