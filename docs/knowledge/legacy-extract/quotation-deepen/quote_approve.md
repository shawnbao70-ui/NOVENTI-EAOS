# 报价审批与人工确认点

**Evidence strength:** Strong for Quote Approve; strong negative for its linkage to Approval Center  
**Governance cross-reference:** [`../governance/approval.md`](../governance/approval.md)

## Scope 与关键结论

Legacy 的“报价审批”至少有三种不同语义，不能合并理解：

1. **Quote Approve Type A**：活动业务路径，人工核对 Draft 报价，可改量/改价，满足门槛后写 Sent；
2. **`quote_approval` 辅助表**：可建立 Pending 记录并计数，但未发现活动 Quote Approve 调用；
3. **Approval Center**：使用 `approval_records` / `approval_history` 的横向治理流，未发现对报价 Sent 的回调或强制 gate。

因此 Human Approved 证明有人在动作页确认，不证明已经过指定审批人、多级工作流或中心审计。治理要求和中心审批详情以 [`../governance/approval.md`](../governance/approval.md) 为准。

## 业务规则

| ID | 规则 |
|---|---|
| QAP-R01 | 具有 Quotes view 权限的用户可打开 Quote Approve 页面。 |
| QAP-R02 | POST 动作要求 Quotes edit 权限；页面可见性和执行权限分开。 |
| QAP-R03 | 只有 Draft 报价可完成 Approve→Sent。 |
| QAP-R04 | 批准前报价必须至少有一条行项目。 |
| QAP-R05 | 批准必须由前端确认后提交 `human_confirm=1`，服务端再次校验。 |
| QAP-R06 | Draft Approve 页面允许可选修改数量和单价，再以服务端结果保存。 |
| QAP-R07 | Save Draft 保存行修订并写操作日志，但不改变 Draft 状态。 |
| QAP-R08 | Cancel 返回报价详情，不执行发布。 |
| QAP-R09 | Approve 成功直接写 Sent，并记录 `Human Approved → Sent` 操作日志。 |
| QAP-R10 | Quote Approve 不创建销售订单；Convert SO 保留第二次独立确认。 |
| QAP-R11 | AI 摘要、风险提示、库存提示和历史建议只辅助核对，不得静默批准。 |
| QAP-R12 | Quote Approve 未建立 `approval_records`，也未消费 Approval Center 的 Approved 结果。 |
| QAP-R13 | `quote_approval` 可写 Pending 辅助记录，但全库活动调用仅见定义/桥接，未见主流程调用。 |
| QAP-R14 | `quote_approval` 与 `approval_records` 是不同结构，不能仅凭名称视为同一审批链。 |
| QAP-R15 | 报价状态菜单仍可直接写 Sent/Won 等值，可能绕开 Quote Approve 的人工确认门。 |
| QAP-R16 | Approve 日志不是不可变审批历史；未保存批准理由、证据、前后价格差异或确认令牌。 |

## 人工确认点

| 动作 | 人工点 | 业务结果 |
|---|---|---|
| 引导报价创建 | `human_confirm=1` | 创建 Draft 并进入 Approve 页 |
| Save Draft | 用户点击保存 | 保存行修订，不推进状态 |
| Quote Approve | 浏览器确认 + 隐藏字段 + 服务端校验 | Draft→Sent |
| Convert SO | 独立浏览器确认 | 建立 SO；不是 Approve 的附带效果 |
| 状态菜单 | 用户点击状态链接 | 直接覆盖状态；未见 Human Confirm |

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| QAP-V01 | GET 必须有 `Quotes.view` | Hard |
| QAP-V02 | POST 必须有 `Quotes.edit` | Hard |
| QAP-V03 | 报价必须存在 | Hard |
| QAP-V04 | Approve 时状态必须为 Draft | Hard |
| QAP-V05 | Approve 时至少有一行 | Hard |
| QAP-V06 | Approve 必须 `human_confirm=1` | Hard |
| QAP-V07 | 行数量必须大于零 | Hard |
| QAP-V08 | 行单价不得小于零 | Hard |
| QAP-V09 | 当前用户必须是指定中心审批人 | Missing/not modeled in Quote Approve |
| QAP-V10 | 中心审批记录必须 Approved | Missing |
| QAP-V11 | 最低毛利/最大折扣触发升级审批 | Missing |
| QAP-V12 | 批准理由和证据必填 | Missing |
| QAP-V13 | 状态直接写 Sent 必须走同一门 | Missing；状态菜单可绕过 |
| QAP-V14 | 防重复/并发批准需条件更新 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `human_confirm` | 当前页面动作的人类确认标志；非持久化审批身份 |
| `action=save_draft` | 保存行补丁，不发布 |
| `action=approve` | 尝试执行 Draft→Sent |
| `action=cancel` | 放弃动作并返回 |
| `can_approve` | 页面派生值：Draft 且有行 |
| `v18_ai_summary` | 供人核对的摘要，不是审批决定 |
| `risk` | 页面提示级别；无策略引擎证据 |
| `stock_notes` | 库存提示，不构成硬库存 gate |
| 操作日志 `Approve` | 记录动作人、对象和描述；不等于审批中心历史 |
| `quote_approval.approval_status` | 独立报价审批辅助表的 Pending 等状态 |
| `quote_approval.approver` | 辅助记录指定审批人；未接活动 Approve |
| `approval_records` | Approval Center 的横向审批记录，与本地 Quote Approve 分离 |
| `approval_history` | 中心批准/拒绝历史；未绑定报价 Sent |
| `Sent` | 本地 Approve 成功的业务状态 |
| `Human Approved` | 人工确认来源描述，不是统一数据库状态 |

## 与治理审批的边界

[`../governance/approval.md`](../governance/approval.md) 记录了中心流 Pending/Approved/Rejected、指定审批人和治理缺口。本页只补充报价侧事实：

- Quote Approve 没有读取中心状态；
- 中心批准没有观察到反向调用报价服务；
- `create_quote_approval()` 只是可用辅助函数，不能证明流程已接通；
- 多级、顺序、并行、条件审批是未实现元数据，不能推定报价已具备；
- 状态菜单可绕门是报价侧实际风险。

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QAP-E01 | Approve GET/POST 权限与表单处理 | 强 | `apps/quotation/router.py` |
| QAP-E02 | Draft、有行、human confirm 三门 | 强 | `apps/quotation/services.py` |
| QAP-E03 | 行数量/单价服务端校验 | 强 | `apps/quotation/services.py` |
| QAP-E04 | Draft 可编辑、非 Draft 只读 | 强 | `templates/quote_approve.html` |
| QAP-E05 | 浏览器确认后置 `human_confirm=1` | 强 | `templates/quote_approve.html` |
| QAP-E06 | Save Draft 与 Approve 操作日志 | 强 | `apps/quotation/services.py` |
| QAP-E07 | AI 提示与 Convert 分离文案 | 强 | `apps/quotation/services.py`、`quote_detail.html` |
| QAP-E08 | `quote_approval` 结构与 Pending helper | 强 | `apps/quotation/utils.py`、`runtime/v14/legacy_support.py` |
| QAP-E09 | helper 未见活动调用 | 强负向 | 全库 `create_quote_approval` 调用检索、`scripts/` 桥接清单 |
| QAP-E10 | 中心审批使用另一组表和动作 | 强 | `apps/approval/`、`templates/approval_detail.html` |
| QAP-E11 | Type A gate 静态验收与转单分离 | 中 | `docs/reports/V18_Quote_Approve_Gate_Report.md` |
| QAP-E12 | 治理横向边界 | 中 | `business_modules/quotation.md`、`business_modules/approval.md` |

## UNKNOWN + 已查路径

1. **哪些金额、毛利或客户风险应触发中心审批 UNKNOWN。** 已查：`apps/quotation/`、`apps/approval/`、`business_modules/`、`docs/reports/`。
2. **`quote_approval` 的活动消费者和处理页面 UNKNOWN。** 已查：全库 `quote_approval` / `create_quote_approval`、`templates/`、`apps/approval/`。
3. **Quote Approve 操作者是否必须是报价 owner/manager UNKNOWN。** 已查：`apps/quotation/router.py`、`validator.py`、权限调用；只见模块级 view/edit。
4. **批准理由、附件和证据保存位置 UNKNOWN。** 已查：Approve 模板/服务、`quote_history`、`approval_history`、文档附件路径。
5. **直接状态菜单写 Sent 是否属于获准旁路 UNKNOWN。** 已查：`quote_detail.html`、状态路由/服务、V18 报告。
6. **Approval Center 批准后如何释放报价 UNKNOWN。** 已查：`apps/approval/services.py`、`repository.py`、`router.py`、报价服务；未见回调。
7. **并发改价与批准的锁定/版本策略 UNKNOWN。** 已查：`apps/quotation/repository.py`、`services.py`、`quote_versions` 能力。

## 交叉引用

- 治理审批权威：[`../governance/approval.md`](../governance/approval.md)
- 报价状态：[`quote_lifecycle.md`](quote_lifecycle.md)
- 报价行改价：[`quote_lines_pricing.md`](quote_lines_pricing.md)
- 转 SO 第二人工点：[`quote_convert_gates.md`](quote_convert_gates.md)
