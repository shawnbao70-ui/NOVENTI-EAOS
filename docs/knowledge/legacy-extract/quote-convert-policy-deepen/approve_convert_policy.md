# 报价批准与转单政策（Approve vs Convert Policy）— Legacy Knowledge

**Evidence strength:** Strong for separate local gates; strong negative for central Approval Center enforcement  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述 Quote Approve、状态快捷更新、Convert SO 和中央 Approval Center 的真实门禁关系。Quote Approve 是 Draft→Sent 的 Type A 本地人工确认；Convert 是独立 GET 写动作，只要求 quote 存在且尚无 SO；中央审批记录未被两者消费。

交叉引用 `../quotation-deepen/quote_approve.md`、`../governance/approval.md` 和 `../order-chain/so_convert.md`，不重写这些正文。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| ACP-R1 | Quote Approve GET 需要 Quotes view | 只打开审阅页 |
| ACP-R2 | Quote Approve POST 需要 Quotes edit | 写权限与查看分离 |
| ACP-R3 | Approve 仅允许 Draft | 非 Draft 被拒绝 |
| ACP-R4 | Approve 必须至少一行 | 空报价不能 Sent |
| ACP-R5 | Approve 必须 `human_confirm=1` | 服务端硬门 |
| ACP-R6 | Approve 可在确认前修改 qty/price | 保存后重算金额与毛利 |
| ACP-R7 | Approve 成功只写 Sent 和操作日志 | 不创建 SO |
| ACP-R8 | Convert 是第二个独立动作 | Sent 不自动转单 |
| ACP-R9 | Convert 不检查 Draft/Sent/Won/Lost/已确认 | 可跳过 Quote Approve |
| ACP-R10 | Convert 不检查中央 Approved | 未读 approval records/history |
| ACP-R11 | Convert route 无服务端 Sales Orders add gate | UI 隐藏按钮可被直链绕过 |
| ACP-R12 | Convert 使用 GET 执行 SO/TC/quote mutation | 浏览器 confirm 不是服务端令牌 |
| ACP-R13 | 状态菜单可直接写 Sent | 可绕过 Type A Human Confirm |
| ACP-R14 | 状态菜单也可直接写 Won/Lost 等值 | 无中心审批或顺序门 |
| ACP-R15 | `quote_approval` helper/table 与 Type A Approve 分离 | Pending 辅助记录未接主链 |
| ACP-R16 | Approval Center 的 `approval_records/history` 与报价状态分离 | 中心结果无回调 |
| ACP-R17 | Type A 操作日志不等于不可变审批历史 | 不存理由、证据和中心 request ID |
| ACP-R18 | Convert 可建立空 SO | 行门延迟到 SO Approve |
| ACP-R19 | SO 建成后仍有独立 SO Approve→Open | Quote Sent/Convert/SO Open 是三道不同动作 |
| ACP-R20 | 客户信用、折扣、毛利、有效期和贸易条件未触发中心升级 | 未观察到政策引擎 |
| ACP-R21 | AI summary/warnings 只支持人审 | 不授予权限或自动批准 |
| ACP-R22 | EAOS 不得把 Human Approved 等价为中央多级审批 | 数据结构和操作者模型不同 |

---

## 3. Process

### 3.1 Quote Approve

1. 具备 view 权限的用户打开 Type A 页面。
2. 页面展示客户、行、币种、总额、毛利和提示。
3. 可提交行数量/价格修订；服务端重算。
4. action=approve 时检查 Draft、有行、human confirm。
5. 写 Sent 和操作日志，返回报价详情。

### 3.2 Convert

1. UI 在有 Sales Orders add 时显示 Convert 并用浏览器 confirm。
2. 直接 GET convert route 不接收 request/confirm token。
3. 服务只检查 quote 存在和未有 SO。
4. 建 SO、尝试佣金、复制行、写 quote 已确认、尝试 lifecycle。

### 3.3 可跳过路径

- 未 Approve 的 Draft/Lost 报价可直接 Convert。
- 状态菜单可直接写 Sent 而不走 Type A。
- Convert 不读取 `quote_approval` 或 Approval Center。
- 中央 Approved 不自动 Sent 或 Convert。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| ACP-V1 | Approve GET 需 Quotes.view | Hard | |
| ACP-V2 | Approve POST 需 Quotes.edit | Hard | |
| ACP-V3 | Approve 必须 Draft | Hard | |
| ACP-V4 | Approve 必须有行 | Hard | |
| ACP-V5 | qty > 0、price >= 0 | Hard in line patches | |
| ACP-V6 | Approve 必须 human confirm | Hard | |
| ACP-V7 | Convert quote 必须存在 | Hard | |
| ACP-V8 | Convert quote 不得已有 SO | Hard application guard | |
| ACP-V9 | Convert 必须已 Sent/Won | Missing | |
| ACP-V10 | Convert 必须有中心 Approved | Missing | |
| ACP-V11 | Convert 必须有 Sales Orders.add 服务端权限 | Missing | |
| ACP-V12 | Convert 必须 POST/CSRF/确认令牌 | Missing | GET mutation |
| ACP-V13 | 直接写 Sent 必须走同一人审门 | Missing | |
| ACP-V14 | 高折扣/低毛利/超信用必须升级审批 | Missing | |
| ACP-V15 | owner/指定 approver 必须匹配操作者 | Missing | 仅模块权限 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `human_confirm` | 当前 Type A 表单的确认值 |
| `action=approve` | 尝试 Draft→Sent |
| `action=draft` | 保存/停留，不发布 |
| `action=cancel` | 放弃表单，不改变业务状态 |
| `can_approve` | Draft 且有行的 UI 派生值 |
| Sent | Quote Approve 写结果 |
| `已确认` | Convert 写结果 |
| Approve operation log | 本地动作日志 |
| `quote_approval` | 未接主链的报价辅助审批表 |
| `quote_approval.approval_status` | 辅助 Pending/其他状态 |
| `approval_records` | 中央横向审批记录 |
| `approval_history` | 中央批准/拒绝历史 |
| `sales_orders.quote_id` | Convert 结果与防重键 |
| SO Open | Convert 后另一道 Human Approved 结果 |
| AI warnings | 建议/风险提示，不是 gate |
| browser confirm | 客户端交互，不是审计证据 |

---

## 6. State Vocabulary

| State / term | Layer | Meaning |
|--------------|-------|---------|
| Draft→Sent | Quote Type A | 本地人工发布 |
| Pending/Approved/Rejected | Approval Center | 横向中心记录，与 quote 未接 |
| `quote_approval.Pending` | 辅助表 | 未证实主流程消费者 |
| `已确认` | Convert | 已转单后的 quote 写回 |
| Open | SO Type A | 订单批准，非 quote 批准 |
| Human Approved | 交互约束 | 不等于中央审批状态 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 哪些金额/毛利/折扣/信用应触发中心审批 | quotation/approval/customer/pricing paths、reports |
| `quote_approval` 的活动消费者 | quotation utils/services、approval apps、templates |
| 指定 approver/owner 是否应限制 Quote Approve | quotation router/service、permissions |
| 批准理由、附件和价格差异证据的保存位置 | approve template/service、history/document paths |
| 直接状态写 Sent 是获准旁路还是缺陷 | status routes/templates、V18 reports |
| 中央 Approved 如何释放 Sent/Convert | approval services/repository、quotation/sales callbacks |
| Convert GET 的 CSRF/重放控制 | router/middleware/security reports |
| Draft/Lost 可转单的正式业务意图 | business modules、reports、service gates |
| 并发改价、Approve 与 Convert 的锁定顺序 | repositories/transactions/version paths |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/quotation/router.py` | Approve GET/POST 权限与状态 routes |
| `apps/quotation/services.py` | Draft/lines/human confirm 门和日志 |
| `apps/quotation/repository.py` | 行修订、状态直接更新 |
| `apps/quotation/utils.py` | `quote_approval` helper |
| `apps/sales/router.py` | Convert GET 无服务端 gate |
| `apps/sales/services.py` | Convert 仅两道硬门 |
| `templates/quote_approve.html` | Type A 表面 |
| `templates/quote_detail.html` | 状态旁路与 Convert CTA |
| `templates/quotes.html` | UI add 权限/confirm |
| `apps/approval/services.py` | 中央审批独立流 |
| `apps/approval/repository.py` | 中央 records/history |
| `business_modules/approval.md` | 中央治理边界 |
| `docs/reports/V18_Quote_Approve_Gate_Report.md` | Approve/Convert 分离 |
| `docs/reports/Business_Strong_A013_Quote_Ops_Report.md` | 报价门禁审计 |
| `docs/knowledge/legacy-extract/governance/approval.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/order-chain/so_convert.md` | EAOS 只读转单交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
