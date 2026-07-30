# 权限空洞与危险直链风险编目

**Evidence strength:** Strong for listed route signatures and gates; deployment middleware/CSRF behavior is UNKNOWN unless explicitly cited  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本文件只编目跨域授权缺口，不重写 [Approval Center](../governance/approval.md)。

分类：

- **Confirmed permission hole**：活动写路由没有 request、permission gate 或对象授权；
- **Confirmed unsafe method**：写操作使用 GET；即使有 RBAC，也可能被链接、预取、爬虫或跨站请求触发；
- **Object-scope hole**：列表按 owner 过滤，按 ID 详情/动作不复验同一范围；
- **Possible / UNKNOWN**：静态路由未见 gate，但全局中间件、反向代理或部署策略可能另有限制。

浏览器 `confirm()`、按钮隐藏和菜单权限只属于 UI 提示，不是服务端授权。Human Confirm 只证明提交者在 Type A 页面勾选确认，不自动证明其为 Approval Center approver。

---

## 2. 风险目录

| 风险ID | 触发条件 | 影响 | 缓解备注（EAOS） |
|--------|----------|------|------------------|
| PH-001 | 任意可达用户直访 Approval GET `/approve*` 或 `/reject*`；route 不校验 RBAC、指定 approver、Pending 原状态 | 越权批准/拒绝；重复决策；备用路径无完整历史；中心治理失效 | POST command + CSRF + approver/tenant/object gate + Pending 条件更新 + 不可变理由/历史 |
| PH-002 | 直访 Sales GET `convert_so`、`create_do` 或无 request 的 create_sales_order | 未授权创建 SO/DO；绕过报价批准、owner 和目标状态；可产生重复履约 | 命令端点必须持有 request principal；校验 Quote/SO owner、状态、权限和幂等键 |
| PH-003 | 直访 Quote/SO status URL；Quote 有状态枚举但无 request/gate，SO 有 edit gate但非 Open 转换仍由 GET 直写 | 越权 Quote 状态推进，或 SO 绕开完整状态转换/Human Approved 语义 | 只允许显式 command；每次转换校验角色、owner、旧状态和审批证据 |
| PH-004 | 直访 Finance `create_purchase_invoice`、`approve_expense`，或提交 `add_expense`；handler 无 request gate | 未授权建立采购发票/AP、费用或批准费用；造成财务事实影响 | 财务写入统一 POST + CSRF + Finance/Treasury policy + Human Approved/Approval reference |
| PH-005 | 调用无 gate 的 Customer follow-up、Finance clear_followups、Marketing Distributor delete、Platform Organization delete 等 residual/页面动作 | 任意写入/清除 CRM 跟进或删除跨域主数据；审计主体缺失 | 所有 mutation 由统一 policy enforcement point 保护；删除改为受审计命令和软删除 |
| PH-006 | 普通用户通过已知 ID 访问 Customer/SO/Receipt 等详情或动作；列表有 owner filter，但详情只做粗粒度 view 或无 gate | IDOR；读取或操作其他销售人员/租户对象；KPI 泄露全局数据 | Repository 查询必须同时带 tenant_id + owner scope；对象授权不可依赖列表过滤 |
| PH-007 | Customer/Product/Supplier/Purchase/Inventory delete、DO Complete/Reopen 等有 RBAC 的写操作仍使用 GET | 被预取、历史重放、图片/链接嵌入或 CSRF 触发；浏览器确认可绕过 | GET 永远只读；使用 POST/DELETE、CSRF、一次性 intent、幂等和服务端确认 |
| PH-008 | Document Designer save、部分 residual update/delete 与同域 Brand save 使用不同 gate | 相邻功能可绕过更严格的管理员策略；模板/文档品牌被未授权改变 | 对资源定义统一 permission policy；canonical 与 residual alias 必须调用同一 guard |

---

## 3. 风险明细

### PH-001 — Approval Center 直链决策

- **触发条件：** 请求 `/approve/{id}`、`/reject/{id}`、`/approve_record/{id}` 或 `/reject_record/{id}`。
- **确认事实：** 四条均为 GET；活动 router 未见 `has_permission`；备用 record action 甚至不接收 request。Service 更新也未以“当前用户=approver、旧状态=Pending”作为条件。
- **影响：** 登录用户可能按 ID 决策非本人审批；重复 GET 可再次写状态；拒绝理由和业务释放仍缺失。
- **缓解备注（EAOS）：** 将“谁能决定、对哪个 tenant/object、从什么状态、基于什么证据”放在单一审批策略中。
- **交叉引用：** [Governance Approval](../governance/approval.md)。

### PH-002 — Sales 创建链无 route gate

- **触发条件：** 直访 `/convert_so/{quote_id}`、`/create_do/{so_id}`，或直接提交创建订单。
- **确认事实：** handler 不接收 request，无法执行当前用户 RBAC/owner 检查；服务层主要校验对象存在和重复，不等同授权。
- **影响：** 未授权转换报价、创建交付；同一 SO 无硬唯一约束时可重复建 DO。
- **缓解备注（EAOS）：** Quote→SO 与 SO→DO 均需 command permission、对象范围和来源唯一键。

### PH-003 — URL 状态写入

- **触发条件：** 访问 `/quote_status/{quote_id}/{status}` 或 `/so_status/{so_id}/{status}`。
- **确认事实：** Quote route 不接收 request、未见 permission gate，service 只限制为 Draft/Sent/Negotiating/Won/Lost，但不校验当前状态；SO route 有 edit gate，但 Open 以外状态可直接写入，转换规则较弱。
- **影响：** Quote 可被越权改状态；SO 可进入非法/不可审计字符串状态。
- **缓解备注（EAOS）：** URL 不接受任意 status；显式 Submit、Approve、Cancel、Reopen 命令各自定义前置条件。

### PH-004 — Finance GET 写入

- **触发条件：** 访问 `/create_purchase_invoice/{purchase_id}`、`/approve_expense/{expense_id}`，或提交 `/add_expense`。
- **确认事实：** handler 无 request 参数和 route gate；服务方法无法据此验证当前主体。`create_receipt` 与 Type A AR 路径已有显式权限，显示同模块策略不一致。
- **影响：** 发票/AP 和费用状态可被直链改变。
- **缓解备注（EAOS）：** 所有金额/应收应付/费用动作由 Finance application policy 统一校验，不允许无主体调用。

### PH-005 — 无 gate 的跨域写操作

- **已确认示例：**
  - Customer `add_followup` POST 不接收 request，无 permission/owner gate；
  - Finance residual `clear_followups` GET 无 gate，删除特定 followup 行；
  - Marketing `delete_distributor` GET 直接删除，无 request；
  - Platform organization company/department/team/position 删除 GET 未见 route gate；
  - 多个 residual 的系统设置、消息、文件、API connection 删除需逐项复核。
- **影响：** 主数据、沟通历史和平台配置可能被越权修改/删除。
- **缓解备注（EAOS）：** 以资源+动作定义 policy，不按“页面属于管理员菜单”推断授权。
- **UNKNOWN：** 全局 middleware 是否对这些具体 path 实施额外策略；已检索对应 routers/residuals，未见本地证据。

### PH-006 — 列表过滤不等于对象授权

- **触发条件：** 普通销售用户猜测或获得其他对象 ID 后直接访问详情。
- **确认事实：**
  - Customer detail 未见 Customers.view 或 owner 复验；
  - Sales list 按 salesperson 过滤，但 detail 只做粗粒度 view；
  - Receipt list 有销售归属过滤，detail 只检查 Receipts.view；
  - Delivery 列表与 KPI 的数据范围也不一致。
- **影响：** 跨 owner 读取、数据泄露，继而利用其他写入口。
- **缓解备注（EAOS）：** 所有 get_by_id 使用授权查询；无匹配统一返回 not found，避免泄露对象存在性。

### PH-007 — 有 RBAC 但 GET 仍危险

- **触发条件：** 已授权会话加载删除/完成/重开 URL。
- **确认事实：** Customer、Product、Supplier、Purchase、Inventory 删除、PO Receive 和 DO Complete/Reopen 均为 GET；这些示例有 route/service RBAC，但页面确认不改变 HTTP 风险。
- **影响：** CSRF 与非交互触发；缓存/预取语义不安全；审计无法区分用户意图。
- **缓解备注（EAOS）：** RBAC 不能替代安全 HTTP method、CSRF 和服务端 intent。

### PH-008 — 相邻功能策略不一致

- **触发条件：** 用户不能保存 Brand profile，却可调用 `/document_designer/save` 或其他 residual alias。
- **确认事实：** Brand save/upload 显式检查管理员；Document Designer save 直接更新模板，未见同等 gate。Canonical/residual alias 也可能具有不同检查。
- **影响：** 文档 Logo、QR、签名、水印和布局策略可绕开 Brand 管理边界。
- **缓解备注（EAOS）：** BrandAsset、DocumentTemplate 等资源分别定义 policy，但共享 tenant/admin 要求和审计。

---

## 4. 风险分级与确认状态

| Risk ID | Severity | Confirmation |
|---------|----------|--------------|
| PH-001 | Critical | Confirmed route/service gap |
| PH-002 | Critical | Confirmed route gap |
| PH-003 | High | Quote confirmed; SO partial protection |
| PH-004 | Critical | Confirmed route gap |
| PH-005 | High | Listed examples confirmed; global middleware UNKNOWN |
| PH-006 | Critical | Confirmed on listed detail paths |
| PH-007 | High | Confirmed unsafe HTTP method |
| PH-008 | Medium/High | Confirmed policy inconsistency |

---

## 5. 只读来源路径

| Path | Risk IDs | Why cited |
|------|----------|-----------|
| `apps/approval/router.py` / `services.py` / `repository.py` | PH-001 | GET decision、无 route gate、状态更新条件 |
| `templates/approvals.html` | PH-001, PH-007 | 浏览器确认仅 UI 层 |
| `apps/sales/router.py` / `services.py` | PH-002, PH-003, PH-006 | 转单、建 DO、状态和 owner 范围 |
| `apps/quotation/router.py` / `quote_pages.py` | PH-003, PH-007 | Quote status、删除和 residual aliases |
| `apps/finance/router.py` / `services.py` / `v14_residual.py` | PH-004, PH-005, PH-006 | 财务写入口、clear_followups 与不一致 gate |
| `apps/customer/router.py` / `services.py` | PH-005, PH-006, PH-007 | follow-up、详情、删除 |
| `apps/marketing/v14_residual.py` | PH-005 | Distributor 直接 GET 删除 |
| `apps/platform/org_pages.py` / `v14_residual.py` | PH-005 | Organization/security 等 GET 删除 |
| `apps/product/router.py` | PH-007 | GET 删除有 RBAC |
| `apps/supplier/router.py` | PH-007 | GET 删除有 RBAC |
| `apps/procurement/router.py` | PH-007 | Receive/Delete GET 与 RBAC |
| `apps/inventory/router.py` / `services.py` | PH-006, PH-007 | DO Complete/Reopen、数据范围和服务内 gate |
| `apps/brand_center/v14_residual.py` | PH-008 | Brand 管理与 Document Designer gate 差异 |
| `apps/document_center/knowledge_pages.py` / `v14_residual.py` | PH-005, PH-007 | GET 删除与局部 knowledge policy |
| `bootstrap/v14_residual.py` | PH-008 | duplicate route winner 对实际 guard 的影响 |
| `docs/reports/Business_Strong_A022_Approval_Ops_Report.md` | PH-001 | Approval Hub 诚实性审计 |
| `docs/reports/Route_Ownership_Registry.md` | PH-008 | 重复 owner 与 runtime winner |
| `docs/knowledge/legacy-extract/governance/approval.md` | PH-001 | 中央审批与 Human Approved 交叉引用 |

**UNKNOWN 检索范围：** `core/security/`、全局 middleware、部署反向代理 policy、实际 route table；未发现可证明上述 path 全部被统一补强的全局资源级授权层。

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
