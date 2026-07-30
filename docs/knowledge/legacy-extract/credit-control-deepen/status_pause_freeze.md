# 客户暂停、失效、冻结与黑名单阻断

## Scope与证据强度

本页核验客户状态词汇是否对 Quote、SO、DO、Ship 形成服务端阻断。`暂停跟进`、`失效客户` 是可编辑标签；freeze/blacklist/disabled 未建模。状态总览交叉引用 [`../customer-deepen/customer_status_lifecycle.md`](../customer-deepen/customer_status_lifecycle.md)。

## 业务规则（稳定ID）

1. **SPF-R01** 新客户默认 customer_status=`开发中`。
2. **SPF-R02** 编辑页提供开发中、已报价、跟进中、已成交、长期客户、暂停跟进、失效客户等标签。
3. **SPF-R03** 服务端接受 customer_status 文本，不执行状态迁移矩阵。
4. **SPF-R04** 状态修改不要求原因、有效期、审批或解冻人。
5. **SPF-R05** 客户列表筛选/新建选项与编辑页词汇不完整一致。
6. **SPF-R06** Dashboard 对 following/active 使用中文 customer_status 分组。
7. **SPF-R07** Opportunity Mining 还使用 Active/NULL 口径。
8. **SPF-R08** customer_statistics 部分读取 `status` 而非 `customer_status`。
9. **SPF-R09** 报价客户 picker 不按 customer_status 过滤。
10. **SPF-R10** 暂停/失效客户仍可创建 Quote。
11. **SPF-R11** Quote Approve 不读取客户状态。
12. **SPF-R12** Quote→SO Convert 不读取客户状态。
13. **SPF-R13** SO Approve 不读取客户状态。
14. **SPF-R14** Create DO 不读取客户状态。
15. **SPF-R15** DO Ship 不读取客户状态。
16. **SPF-R16** 收款不读取客户状态。
17. **SPF-R17** Customer Credit Watch/Needs Follow-up 只是 warning。
18. **SPF-R18** Customer360 New Quote CTA 只按 Quotes.add 显示，不按状态隐藏。
19. **SPF-R19** Customer AI 风险为只读建议，不执行冻结。
20. **SPF-R20** 全库 blacklist 活动实现指 IP 安全黑名单，不是客户黑名单。
21. **SPF-R21** 未见 customer freeze、credit hold、disabled 字段或命令。
22. **SPF-R22** 删除客户是 GET 级联硬删，不是失效/冻结归档。

## 流程

1. 创建客户时写默认开发中。
2. 用户可通过普通更新 POST 覆盖 customer_status。
3. 页面以 badge、筛选和 KPI 展示状态。
4. Customer360 可显示余额风险 warning。
5. 下游 Quote/SO/DO/Ship 不回查状态。
6. 因此暂停/失效只影响展示与统计，不形成交易冻结。

## 校验（强/弱/缺失）

1. **SPF-V01（弱/UI）** 编辑下拉提供有限词汇。
2. **SPF-V02（缺失）** 服务端无状态枚举校验。
3. **SPF-V03（缺失）** 无合法状态转移顺序。
4. **SPF-V04（缺失）** 暂停/失效不要求原因。
5. **SPF-V05（缺失）** freeze/unfreeze 不要求审批。
6. **SPF-V06（缺失）** 客户黑名单无实体、依据和有效期。
7. **SPF-V07（缺失）** 失效客户不阻断 Quote。
8. **SPF-V08（缺失）** 暂停客户不阻断 SO/DO/Ship。
9. **SPF-V09（缺失）** 状态变化不写审计历史。
10. **SPF-V10（缺失）** status 与 customer_status 统计口径不一致。
11. **SPF-V11（强/语义）** IP blacklist 与客户 blacklist 主体不同。
12. **SPF-V12（弱/边界）** AI recommendation 标明只读，不自动冻结。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `customer_status` | 可编辑 CRM 标签 |
| `status` | 部分旧工具使用的并行字段名 |
| `开发中` | 新建默认 |
| `已报价` | UI 状态选项 |
| `跟进中` | 跟进分组 |
| `已成交` | active 分组 |
| `长期客户` | active 分组 |
| `暂停跟进` | 标签，不是硬 pause |
| `失效客户` | 标签，不是交易 invalid gate |
| `Active/Inactive` | 并行英文口径 |
| `healthy/watch/risk` | 余额启发式 |
| `Credit Watch` | UI warning |
| `ip_blacklist` | 安全 IP 黑名单 |
| Customer freeze/hold | 未建模 |
| status history | 未建模 |
| `can_approve` | 单据状态门控，不是客户状态门控 |

## 状态词汇

| 词汇 | 执行判断 |
|---|---|
| 暂停跟进 | 可编辑标签 |
| 失效客户 | 可编辑标签 |
| Paused/Invalid | 英文概念未形成服务端状态 |
| Frozen/Credit Hold | 未实现 |
| Blacklisted | 客户域未实现 |
| Disabled | 客户域未实现 |
| Active/Inactive | 与中文口径并行且不一致 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SPF-E01 | Customer Form 默认与更新写入 | 强 | `apps/customer/router.py`、`services.py` |
| SPF-E02 | 编辑页七态选项 | 强 | `templates/edit_customer.html` |
| SPF-E03 | 列表筛选/创建词汇不完整 | 强 | `templates/customers.html` |
| SPF-E04 | 状态统计使用不同字段/词汇 | 强 | `apps/customer/repository.py`、`utils.py` |
| SPF-E05 | Quote picker 不筛状态 | 强 | `apps/quotation/repository.py` |
| SPF-E06 | Quote Approve/Convert 无状态查询 | 强 | `apps/quotation/services.py`、`apps/sales/services.py` |
| SPF-E07 | Create DO/Ship 无客户状态查询 | 强 | `apps/sales/services.py`、`apps/inventory/services.py` |
| SPF-E08 | Customer Credit tab 是 warning | 强 | `templates/customer_detail.html`、`apps/customer/services.py` |
| SPF-E09 | AI runtime 只读且 gateway 未执行 | 中 | `core/object360/customer/runtime.py` |
| SPF-E10 | Vol007 报告记录 status/customer_status 不一致 | 强 | `docs/reports/V151E_Volume007_Customer_Business_Chain_Extraction_Report.md` |

## UNKNOWN + 已查路径

1. **暂停/失效是否应阻断交易 UNKNOWN。** 已查路径：Customer、Quotation、Sales、Inventory services 与 policy docs。
2. **生产库是否存 Paused/Invalid 英文值 UNKNOWN。** 已查路径：forms、locales、DDL；未读取生产数据。
3. **客户 freeze 字段/表是否在外部系统 UNKNOWN。** 已查路径：integrations、customer schema、business_modules。
4. **客户 blacklist 与解除流程 UNKNOWN。** 已查路径：customer/security/compliance；仅命中 IP。
5. **状态变更历史和原因保存位置 UNKNOWN。** 已查路径：Customer history、audit、approval。
6. **status 与 customer_status 的迁移策略 UNKNOWN。** 已查路径：upgrade、utils、Vol007报告。
7. **制裁/KYC 名单是否应阻断 Ship UNKNOWN。** 已查路径：compliance、customs、inventory ship。
8. **UI 风险阈值为何不一致 UNKNOWN。** 已查路径：Customer service 与 detail template。
9. **删除客户前是否应改为冻结/失效 UNKNOWN。** 已查路径：delete route、repository cascade、governance docs。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
