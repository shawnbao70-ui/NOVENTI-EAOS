# 收货前审批是否强制

**Evidence strength:** Strong  
**Verified:** 2026-07-23  
**Authority cross-ref:** [`../procurement-receipt-deepen/po_lifecycle_gates.md`](../procurement-receipt-deepen/po_lifecycle_gates.md)（生命周期权威；本页只深化「Approve 是否 Receive 前置」）

## Scope 与结论

本页核验 Approve 是否为 Receive 的服务端强制前置。结论为**否**：`PO_OPEN = {Draft, Open, Pending}` 均映射为 `open` stage，Receive 只要求 `stage == "open"`，因此 Draft/Pending 可绕过 Approve 直接收货。Approve 只把精确 `Draft` 写成 `Open`，并要求行与 `human_confirm=1`；Receive 不调用 Approve，不查 Approval Center。

## 业务规则（稳定 ID）

1. **MAP-R01** 新 PO 默认 `status='Draft'`（`add_purchase`）。
2. **MAP-R02** `Draft` / `Open` / `Pending` 均归一为 `po_stage → open`（`PO_OPEN` frozenset）。
3. **MAP-R03** `Received` / `已入库` / `Completed` 归一为 `received` stage（`PO_RECEIVED`）。
4. **MAP-R04** Approve 仅允许精确 `status == "Draft"`；非 Draft 返回 `v18_approve_draft_only`。
5. **MAP-R05** Approve 要求至少一行且 `human_confirm == "1"`。
6. **MAP-R06** Approve 成功只写 `Open`，不改库存、不写 ledger、不收货。
7. **MAP-R07** Receive 只要求 `stage == "open"`，因此 Draft/Pending 可收。
8. **MAP-R08** Receive 服务路径不调用 `apply_purchase_approve`。
9. **MAP-R09** Receive 不查询 `approval_records` / Approval Center 状态。
10. **MAP-R10** UI 在 `Draft`/`Open`/`Pending` 均显示 Receive（list/detail/360/`po_is_open`）。
11. **MAP-R11** Receive 要求 `Purchases.edit`，但无 `human_confirm` 字段或确认页。
12. **MAP-R12** Receive 路由为 **GET** `/receive_purchase/{purchase_id}`（状态变更写动作）。
13. **MAP-R13** Receive 检查：PO 存在、非 received、有行、无既有 `PO Receipt`+`PO-{id}` ledger。
14. **MAP-R14** 成功后 PO 直接 `update_purchase_status_received` → `Received`。
15. **MAP-R15** Inventory 扫码收货委托同一 `ProcurementPageService.receive_purchase`。
16. **MAP-R16** AI brief 对 open family 主键动作引导 `/receive_purchase/{id}`。
17. **MAP-R17** A-004 gate 用 `status="Draft"` 的 FakeRepo 验证 `receive ok`。
18. **MAP-R18** Finance 开采购发票不校验 PO 必须为 Received（服务端只查 PO 存在与发票查重）。
19. **MAP-R19** Approve 有专用确认模板 `purchase_approve.html`（`require_human_confirm=true`）；Receive 仅 `onclick=confirm`。
20. **MAP-R20** detail 上 Approvals 链接文案标明「not auto-submit from this PO」。

## 流程

1. Create PO → `Draft`。
2. 可选 Approve：`Draft` → `Open`（需行 + human_confirm）。
3. Receive 可从 `Draft` / `Open` / `Pending` 直接执行（`po_is_open`）。
4. Receive 过账库存与 ledger 后写 `Received`。
5. Approval Center（`apps/approval/`）不参与此链的强制门禁。

## 校验（强 / 弱 / 缺失）

1. **MAP-V01（强）** Create 需 `Purchases.add`。
2. **MAP-V02（强）** Approve POST 需 `Purchases.edit`。
3. **MAP-V03（强）** Approve 需 Draft、有行、`human_confirm=1`。
4. **MAP-V04（强）** Receive 需 `Purchases.edit`。
5. **MAP-V05（强 / 过宽）** Receive 需 open family（含 Draft/Pending）。
6. **MAP-V06（强）** Receive 需至少一行且无既有 PO Receipt ledger。
7. **MAP-V07（缺失）** Receive 不要求 `status=Open` / `approved_at`。
8. **MAP-V08（缺失）** Receive 无 `human_confirm`。
9. **MAP-V09（缺失）** Receive 使用 GET，无 POST/CSRF 语义的写门槛。
10. **MAP-V10（缺失）** 无 Approval Center 记录校验。
11. **MAP-V11（缺失）** 并发 Receive 无行锁 / DB unique（`trans_type+remark`）。
12. **MAP-V12（缺失）** 开票服务端不要求 Received。
13. **MAP-V13（弱 / UI）** Receive 按钮有浏览器 `confirm()`，非服务端门。
14. **MAP-V14（缺失）** Approve 与 Receive 之间无乐观锁 / 版本号。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `Draft` | 新建态，同时属于可收货 open family |
| `Open` | Approve 成功目标态；非 Receive 前置硬条件 |
| `Pending` | open 兼容态；活动写入入口未证实 |
| `Received` | 收货过账完成态 |
| `po_stage` | open / received / other 归一函数 |
| `po_is_open` | UI 可编辑 / 可收货布尔（`stage==open`） |
| `human_confirm` | **只用于 Approve**，Receive 不读 |
| `Purchases.edit` | Approve 与 Receive 共用动作权限 |
| `PO Receipt` | 收货 ledger `trans_type` |
| `PO-{id}` | 收货判重 / 软追溯 `remark` |
| `approval_records` | Approval Center 记录；未接 PO Receive |
| operation log | Approve 写 V18 日志；Receive 未见专用 `_write_log` |

## 状态词汇

| 词汇 | 判断 |
|---|---|
| Approved | 无独立 PO 状态；表现为 `Open` |
| Open family | `Draft` / `Open` / `Pending` |
| Received family | `Received` / `已入库` / `Completed` |
| Mandatory approval before receive | **Legacy 不成立** |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| MAP-E01 | `PO_OPEN` 含 Draft；`po_stage` / `receive_purchase` 只查 open | 强 | `apps/procurement/services.py` |
| MAP-E02 | `apply_purchase_approve`：Draft→Open + human_confirm | 强 | `apps/procurement/services.py` |
| MAP-E03 | GET `/receive_purchase/{id}` + `Purchases.edit` | 强 | `apps/procurement/router.py` |
| MAP-E04 | list：Draft/Open/Pending 显示 Receive | 强 | `templates/purchases.html` |
| MAP-E05 | detail：`po_is_open` 显示 Receive；Approvals 非自动提交 | 强 | `templates/purchase_detail.html` |
| MAP-E06 | A-004 FakeRepo `status="Draft"` 测 `receive ok` | 强 | `scripts/business_strong_a004_purchase_gate.py`；`docs/reports/Business_Strong_A004_Purchase_Report.md` |
| MAP-E07 | brief open→receive href | 强 | `v15/ai_operating_depth/brief.py` |
| MAP-E08 | Approval app 无 PO Receive gate | 强负向 | `apps/approval/services.py`、`router.py` |
| MAP-E09 | 开票不校验 Received | 强 | `apps/finance/services.py`（`_legacy_create_purchase_invoice`） |
| MAP-E10 | Inventory 扫码委托 receive_purchase | 强 | `apps/inventory/services.py` |
| MAP-E11 | Approve 确认页 require_human_confirm | 强 | `templates/purchase_approve.html` |

## UNKNOWN + 已查路径

1. **Draft 直接收货是政策还是缺陷 UNKNOWN。** 已查：`apps/procurement/services.py`、A-004、`docs/reports/Business_Strong_A004_Purchase_Report.md`、邻包 `po_lifecycle_gates.md`。
2. **Pending 的活动写入口 UNKNOWN。** 已查：procurement routes/services、templates status badges、repository updates。
3. **Approval 插件/外部钩子是否部署时拦截 UNKNOWN。** 已查：`apps/approval/`、bootstrap/hooks 命名面、purchase_detail Approvals 链接。
4. **旧 residual Receive 是否仍可达 UNKNOWN。** 已查：`apps/procurement/`、`apps/inventory/v14_residual.py`、supplier residual 命名面。
5. **并发 Approve/Receive 最终状态 UNKNOWN。** 已查：repository update/commit、DDL indexes、无锁语义。
6. **GET Receive 的 CSRF/预取保护 UNKNOWN。** 已查：middleware 命名面、router GET、templates confirm。
7. **Receive 是否应写 operation log UNKNOWN。** 已查：`receive_purchase` 无 `_write_log`；Approve 有；audit 命名面。
8. **多租户下 ledger 判重范围 UNKNOWN。** 已查：`count_inventory_ledger_for_po` SQL；tenant schema 边界。
9. **`apps/purchase/` 模块是否历史存在 UNKNOWN。** 已查：`apps/` 目录 — **当前不存在**；采购在 `apps/procurement/`。
10. **`core/` 是否另有强制审批拦截 UNKNOWN。** 已查：`core/` 检索遇超时；未见从 procurement receive 的调用链。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\approval\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`（purchase*.html）
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\brief.py`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\business_strong_a004_purchase_gate.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A004_Purchase_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- 已查不存在：`H:\Workspace\EZAM_CRM - 9.0\apps\purchase\`
