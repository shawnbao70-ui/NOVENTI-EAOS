# 税务发票实体 / 表 / 路由有无

## Scope 与结论

交叉引用权威：[`../finance/invoices.md`](../finance/invoices.md)。本页只回答「销售税务发票是否作为一等实体存在」。

**结论：** Legacy **没有**可运行的销售税务发票实体。运行中可见的相关对象是：采购发票 `purchase_invoices`、应收台账 `ar_records`、税务记录 `tax_records`、税率字典 `tax_settings`、以及 NDE/模板层的 Invoice 文档类型。Finance 仓储与模块规格声明的 `invoices` / `invoice_items` / `/invoices` CRUD **无 DDL、无活动页面、无可证写入链**，属 phantom / 规划面。

## 业务规则（稳定 ID）

1. **TIE-R01** 销售税务发票主表 `invoices` 在 `runtime/v14/legacy_support.py` 启动 DDL 中未发现 `CREATE TABLE`。
2. **TIE-R02** `invoice_items` 同样未见 DDL；无发票行持久化证据。
3. **TIE-R03** `apps/finance/repository.py` 声明 `primary_table = "invoices"`，scaffold `list_records`/`count` 会对该表发 SQL，但不构成业务开票能力。
4. **TIE-R04** `business_modules/finance.md` 规划拥有 `/invoices`、`/add_invoice`、`/create_invoice_from_order` 等路由，并自标 phantom-table 风险。
5. **TIE-R05** 活动 Finance HTTP scaffold（`apps/finance/routes.py`）仅暴露 health/records/workspace，未见 `/api/invoices` 业务实现。
6. **TIE-R06** 活动采购发票实体是 `purchase_invoices`，由 `/create_purchase_invoice/{purchase_id}` 从 PO 生成，同步写 `ap_records`。
7. **TIE-R07** 采购发票字段无税码、税额、含税标记、法定票号或红冲引用列。
8. **TIE-R08** 名称含 Invoice 的 DO 路径 `/delivery_order/{do_id}/invoice` 只过账 `ar_records`，locale 明确「不是税务发票」。
9. **TIE-R09** `tax_records` 是独立税务台账（税号/税种/日期/金额/状态/备注），无 source document / party / rate 快照外键。
10. **TIE-R10** `tax_settings` 是税率字典（税码唯一、国家、百分比），不自动绑定销售发票实体。
11. **TIE-R11** `/tax_center` 只读 `tax_records`；`/add_test_tax` 用 GET 插入固定测试 VAT 行，不是开票。
12. **TIE-R12** NDE 文档类型 `Invoice` / `Proforma Invoice` 属于打印家族，不创建 `invoices` 行。
13. **TIE-R13** 全库 apps 层未观察到 `INSERT INTO invoices` / `FROM invoices` 业务 SQL（相对 `purchase_invoices` / `ar_records`）。
14. **TIE-R14** 模板 `invoices.html` / `invoice_detail.html` / `edit_invoice.html` 在检索范围内未找到活动文件；规格列出的 Owned Templates 未落地。
15. **TIE-R15** `receivables.invoice_no` 字段存在于旁路 DDL，活动 DO Post AR 写的是 `ar_records`，不经 `receivables` 开票。
16. **TIE-R16** EAOS 不得把 Finance workspace `LEGACY_ROUTES = ["/invoices"]` 或模块路由表当作已实现税票域。

## 对象矩阵（有 / 无）

| 对象 | 有无 | Legacy 实际角色 |
|---|---|---|
| `invoices` 表 | 无 DDL | repository/规格声明；phantom 风险 |
| `invoice_items` | 无 DDL | 规格规划 |
| `purchase_invoices` | 有 | 采购发票头 |
| `ar_records` | 有 | DO 来源应收计提 |
| `tax_records` | 有 | 手工/测试税务台账 |
| `tax_settings` | 有 | 税率字典种子 |
| `/delivery_order/{id}/invoice` | 有路由 | Post AR，非税票 |
| `/purchase_invoices` | 有路由 | 采购发票列表 |
| `/invoices` CRUD | 无活动实现 | 规格/workspace 目标 |
| NDE Invoice 打印 | 有 | 文档呈现 |
| 法定税票号 / 开票方资质 | 未建模于活动销售发票 | — |

## 校验（强 / 弱 / 缺失）

1. **TIE-V01（强/缺席）** 销售发票主表必须存在于 DDL —— **失败**：未找到 `CREATE TABLE invoices`。
2. **TIE-V02（强/缺席）** 销售发票行表必须存在 —— **失败**：未见 `invoice_items`。
3. **TIE-V03（强）** 采购发票创建前 PO 必须存在。
4. **TIE-V04（强/应用层）** 同 `purchase_id` 不得重复创建采购发票（服务层查重，DDL 无 UNIQUE）。
5. **TIE-V05（强）** DO Post AR 必须 Human Confirm；否则不入账。
6. **TIE-V06（弱/文案）** DO Invoice 页展示 honesty：非税务/NDE 商业发票。
7. **TIE-V07（缺失）** 销售发票号法定唯一 / 税控号校验 —— 无实体可挂。
8. **TIE-V08（缺失）** 税码、税率快照、税额、价税合计一致性 —— 销售开票链不存在。
9. **TIE-V09（缺失）** `/add_invoice`、`/create_invoice_from_order` 活动路由与权限门槛 —— 规格有、实现未见。
10. **TIE-V10（违反安全惯例）** `/add_test_tax` 以 GET 写库，且固定金额，不能当开票校验。
11. **TIE-V11（缺失）** `tax_records` 必须绑定来源发票 —— 结构无 FK。
12. **TIE-V12（弱）** Tax capability health 可查询，但不校验任何税票生命周期。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `invoices`（声明） | Finance 仓储主键表名；无启动 DDL，不能当销售税票权威 |
| `invoice_items`（规格） | 规划中的发票行；未实现 |
| `purchase_invoices.id` | 采购发票主键 |
| `purchase_invoices.invoice_no` | 系统生成 `PINV`+时间戳，非供应商法定票号 |
| `purchase_invoices.invoice_amount` | 复制自 PO 头总额 |
| `purchase_invoices.status` | 初始化 `Unpaid`；非税票状态机 |
| `ar_records` | 应收计提；`source_no`=DO 号 |
| `ar_records.ar_no` | 独立应收号；DO 路径常为空 |
| `tax_records.tax_no` | 税务事项编号（测试路径写死示例号） |
| `tax_records.tax_type` | 自由文本（如 `VAT`），不绑 `tax_code` |
| `tax_settings.tax_code` | 税率字典唯一键（如 `CN_VAT`） |
| `tax_settings.tax_rate` | 百分比配置；无生效期 |
| `receivables.invoice_no` | 旁路应收设计字段；非主链销售税票 |
| NDE `doc_info.invoice_no` | 打印语境编号（可来自 `ar_no`/`source_no`/`INV-{quote}`） |
| `/invoices` LEGACY_ROUTES | workspace 注册目标路径，不等于页面已接线 |
| `honesty_ar_not_tax` | DO 确认页语义标记：AR ≠ 税票 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| TIE-E01 | `purchase_invoices` / `ar_records` / `tax_records` DDL 存在；未见 `invoices` CREATE | 强 | `runtime/v14/legacy_support.py` |
| TIE-E02 | repository `primary_table = "invoices"` | 强 | `apps/finance/repository.py` |
| TIE-E03 | 模块规格声明 invoices/API 与 phantom 风险 | 强 | `business_modules/finance.md` |
| TIE-E04 | 采购发票创建 + AP 同步 | 强 | `apps/finance/services.py`、`router.py` |
| TIE-E05 | DO Invoice = Post AR + honesty | 强 | `apps/inventory/router.py`、`services.py`、`templates/do_invoice.html`、`locales/*.json` |
| TIE-E06 | Tax Center / add_test_tax | 强 | `apps/finance/finance_ops_pages.py`、`templates/tax_center.html` |
| TIE-E07 | `tax_settings` 种子 | 强 | `runtime/v14/legacy_support.py` |
| TIE-E08 | Finance API scaffold 无 invoices CRUD | 强 | `apps/finance/routes.py` |
| TIE-E09 | workspace LEGACY_ROUTES `/invoices` | 中 | `apps/finance/workspace.py` |
| TIE-E10 | V18 报告：「AR accrual — not tax invoice」 | 强 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| TIE-E11 | 模板 `invoices.html` 等未找到 | 强缺席 | 全局文件名检索 `templates/` |

## UNKNOWN + 已查路径

1. **生产库是否被外部脚本手工建了 `invoices` 表 UNKNOWN。** 已查：`runtime/v14/legacy_support.py` DDL、`apps/finance/**/*.py` SQL、`database/**/*.sql`（名称命中范围）；未读生产库文件。
2. **历史版本 `app.py::create_invoice_from_order` 是否仍残留可调用 UNKNOWN。** 已查：`business_modules/finance.md` 目标声明、`apps/finance/routes.py`、`apps/finance/service.py`、`apps/sales/**` invoice 路由关键词。
3. **`receivables`/`collections` 是否被离线工具写入并充当发票 UNKNOWN。** 已查：Finance services INSERT 路径、DO Post AR、reports；活动主链为 `ar_records`。
4. **国家税控/电子发票对接是否在未索引私有插件中 UNKNOWN。** 已查：`apps/**` fapiao/e-invoice/einvoice/税票、`core/capabilities/tax/**`、`docs/reports/**`。
5. **多租户下是否另有 tenant schema 含销售发票表 UNKNOWN。** 已查：legacy_support 主 DDL、tenant 相关命名检索片段；未枚举全部租户迁移。
6. **采购发票是否在业务上被当作进项税票登记 UNKNOWN。** 已查：`purchase_invoices` 字段、Finance/AP reports、tax_records 关联；无税字段绑定。
7. **`/invoices` 是否仅由前端死链引用 UNKNOWN。** 已查：`workspace.py`、`business_modules/finance.md`、templates 文件名；未见活动 invoices 页面模板。

## 只读来源路径

`apps/finance/` · `apps/inventory/` · `runtime/v14/legacy_support.py` · `business_modules/finance.md` · `templates/do_invoice.html` · `templates/tax_center.html` · `templates/purchase_invoices.html` · `core/capabilities/tax/` · `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` · `locales/en.json` · `locales/zh_CN.json` · `locales/zh_TW.json`
