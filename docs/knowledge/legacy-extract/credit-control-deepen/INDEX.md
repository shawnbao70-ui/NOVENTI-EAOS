# 信用控制深化索引

## 文档导航

| 文档 | 主题 | 稳定 ID |
|---|---|---|
| [`credit_limit_fields.md`](credit_limit_fields.md) | 信用额度、等级、账期字段来源 | `CLF-*` |
| [`status_pause_freeze.md`](status_pause_freeze.md) | 客户标签与交易阻断 | `SPF-*` |
| [`convert_ship_credit_gates.md`](convert_ship_credit_gates.md) | Convert/Create DO/Ship 信用矩阵 | `CSG-*` |
| [`override_bypass.md`](override_bypass.md) | 特权、告警绕过和权限缺口 | `OB-*` |

## 交叉引用

| 邻包 | 权威主题 |
|---|---|
| [`../commercial-terms/credit_limit.md`](../commercial-terms/credit_limit.md) | 信用额度总览 |
| [`../customer-deepen/customer_status_lifecycle.md`](../customer-deepen/customer_status_lifecycle.md) | 客户状态词汇 |
| [`../customer-deepen/ar_balance_view.md`](../customer-deepen/ar_balance_view.md) | 经营余额口径 |
| [`../quote-convert-policy-deepen/approve_convert_policy.md`](../quote-convert-policy-deepen/approve_convert_policy.md) | 报价批准与转换 |

## 核心结论

1. customers 的 credit_limit、credit_level、payment_days 来自升级列，但无客户 CRUD 写入口。
2. 经营余额按 SO−Receipts 计算，只驱动风险提示，不与 credit_limit 比较。
3. 暂停跟进、失效客户是可编辑文本标签；freeze/blacklist/credit hold 未建模。
4. Quote 创建/批准、SO 转换/批准、DO 创建/Ship 都不读取客户信用、余额、逾期或状态。
5. 真正硬门禁集中于单据状态、行项、人工确认、库存和发运幂等。
6. Convert SO 与 Create DO 路由缺服务端 RBAC，只依赖 UI 按钮权限。
7. Admin/Super Admin 全局绕过 RBAC；Manager 只有数据可见性扩展，不是 credit override。
8. quote_approval、approval_records 和 V18 Human Approved 未连接信用例外。
9. 未找到正式 credit_override/exception/bypass 实体、理由、审批或审计链。

## 主要证据

- `apps/customer/`
- `apps/quotation/`
- `apps/sales/`
- `apps/inventory/`
- `templates/`
- `runtime/v14/legacy_support.py`
- `core/permission/checker.py`
- `business_modules/`
- `docs/reports/Business_Strong_A003_Delivery_Report.md`
- `docs/reports/Business_Strong_A013_Quote_Ops_Report.md`
- `docs/reports/Business_Strong_A015_Customer_Ops_Report.md`
