# 双写与并行事实源风险编目

**Evidence strength:** Strong for listed active paths; production data divergence remains UNKNOWN without database reconciliation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本编目区分四类风险：

1. **镜像双写**：同一业务量保存在两个字段/表，正常路径同时更新；
2. **顺序多写**：一个动作依次修改多个对象，部分成功会留下中间状态；
3. **并行口径**：不同页面用不同事实集表达同一业务概念；
4. **并行模型**：Legacy 与新增 foundation 表同时存在，但无迁移或同步。

本文件只列风险，不重复 [Ops](../ops/) 和 [Finance](../finance/) 的完整业务规则。是否已有生产数据漂移为 **UNKNOWN**；需对生产快照执行只读差异核对才能确认。

---

## 2. 风险目录

| 风险ID | 类型 | 触发条件 | 影响 | 缓解备注（EAOS） |
|--------|------|----------|------|------------------|
| DW-001 | 库存镜像双写 | Adjust、PO Receive、DO Ship 同时更新 `inventory.stock_qty` 与 `products.stock_qty` 并追加 ledger；产品编辑可只写产品镜像 | 两表漂移；缺库存行时又可能以已漂移的产品值重新种子；低库存、可发量和估值矛盾 | 选定单一库存余额源；ledger 保持审计事实；镜像改为可重建读模型并持续对账 |
| DW-002 | 收款汇总镜像 | Receipt 写入后再回写 SO 的 `received_amount`、`balance_amount`、`payment_status`；详情也可实时汇总 receipts | 中途失败、旁路导入或人工修复后，SO 头与 Receipt 合计不一致 | Receipt 作为收款事件源；订单余额事务内派生或异步可重建；禁止直接写镜像 |
| DW-003 | 活动双轨 AR + 遗留 DDL | 客户 AR360 用 SO−Receipts；Receivable Center 用 DO→`ar_records`；`receivables`/`collections` 仅见未启用结构 | 同一客户出现两个活动“应收余额”；同屏 KPI 也可能混用；收款不降低正式 AR | 明确权责 AR 主账；Receipt Allocation 逐笔核销；遗留 DDL 不按活动第三轨迁移 |
| DW-004 | 发票/AP/付款分离 | 采购发票与 AP 在同次提交复制金额；付款与银行扣账另在同次提交，但不关联 AP/发票 | 发票/AP 已付与余额长期不动；银行资金已减但应付仍 Unpaid；付款无法追溯清算对象 | 单一 AP clearing 服务；付款分配表；保持各 posting 原子并建立跨对象清算审计 |
| DW-005 | 库存顺序多写 | 一次收货/出库逐行更新库存、产品镜像、台账，再于末尾提交并推进 PO/DO 状态 | 读改写无并发保护，幂等仅靠应用查询；并发可超发/重复过账；早退回滚行为 UNKNOWN | 一个幂等 posting command；来源单+行建立数据库唯一键；条件更新余额；明确整体回滚 |
| DW-006 | SO/DO 并行 owner 与状态 | Sales、Inventory 都可从 SO 建 DO，编号/日期/SO 副作用不同；Ship、Complete、Reopen 又分别改 DO/SO | 重复 DO、状态组合非法；历史旧创建扣库存逻辑可能造成二次扣减 | 单一 Fulfillment owner；来源 SO+拆分序号唯一；状态由领域事件推进；迁移识别历史双扣 |
| DW-007 | Brand 并行存储 | 活动 `brand_profiles` 保存/上传；V15.1 `platform_brand`/`company_profiles`/`brand_assets` seed；另有 JSON 锁/主题/审计 | 页面、文档、API 返回不同公司身份/资产；一边修改另一边不更新 | 明确活动 source of truth；一次性迁移并冻结旧写方；主题/锁/审计作为关联治理记录而非第三主数据 |
| DW-008 | 审批并行模型 | Approval Center 更新 `approval_records`；V18 Human Approved 在报价/SO/PO/DO/AR 本地直接推进；早期 `approvals` 结构仍存在 | “已人工确认”与“已中心审批”混淆；中心批准不释放业务、本地释放无中心历史 | 统一 Approval Decision contract；本地动作引用不可变 approval_id；释放与审批结果原子/幂等编排 |

---

## 3. 风险明细

### DW-001 — 库存镜像

- **触发条件：** 正常库存动作同时写两份数量，或 Product update 旁路只写 `products.stock_qty`。
- **影响：** `inventory` 列表、Product 详情、补货判断、发货校验和估值可能读取不同数值。
- **证据强度：** Confirmed。
- **缓解备注（EAOS）：** `inventory_ledger` 保存不可变变动事实，当前余额由一个库存账户模型维护；产品域不得拥有库存写权限。
- **交叉引用：** [Ops Inventory](../ops/inventory.md)。

### DW-002 — SO 收款镜像

- **触发条件：** 活动 Receipt 路径先显式提交 Receipt，再以第二次提交回写 SO aggregate；或其他路径只写任一侧。
- **影响：** 列表/KPI 读取 SO 头、详情读取 Receipt 汇总时出现差异。
- **证据强度：** Confirmed；生产差额 UNKNOWN。
- **缓解备注（EAOS）：** 提供可重复执行的重建与差异告警，不以显示层截零掩盖超收。

### DW-003 — 活动双轨 AR 与遗留结构

- **触发条件：** SO 收款与 DO 应收各自独立发生。
- **影响：** Receipt 使订单 Paid，但 `ar_records` 仍 Unpaid；同一 DO 还可重复记 AR。
- **证据强度：** 两条活动口径 Confirmed，且全库未发现 Receipt→`ar_records` allocation；`receivables`/`collections` 只见 DDL/计数，无活动写入。
- **缓解备注（EAOS）：** 迁移前分别导出 SO、Receipt、DO、AR，保留来源并人工处置不平差项；Dashboard 同时展示两种口径时必须明确标签。
- **交叉引用：** [AR/Receipt Reconciliation](../finance/ar_receipt_reconciliation.md)。

### DW-004 — AP 与资金链断开

- **触发条件：** 采购开票以单次 commit 建立发票和 AP；随后从 Treasury 以另一独立链登记付款和银行扣账。
- **影响：** 资金余额变化不能证明 AP 已清算，也不能证明外部银行执行。
- **证据强度：** Confirmed。
- **缓解备注（EAOS）：** 区分 Payment Instruction、Execution、Allocation、Clearing、Bank Reconciliation。
- **交叉引用：** [AP/Payment Clearing](../finance/ap_payment_clearing.md)。

### DW-005 — 跨行库存过账

- **触发条件：** 多行 PO/DO 过账并发发生，或应用层台账查重与余额读写之间被另一事务插入。
- **影响：** 库存可超发、重复过账或结余快照错误。循环内无 commit、末尾单 commit；中途早退时共享连接是否可靠回滚为 UNKNOWN。
- **证据强度：** Strong for concurrency/idempotency gap。
- **缓解备注（EAOS）：** 事务边界和数据库幂等键必须属于业务命令，不依赖页面查重或重试。

### DW-006 — 履约双入口

- **触发条件：** 同一 SO 分别走 Sales `create_do`、Inventory `convert_do` 或历史旧实现。
- **影响：** 重复履约、不同 DO 编号、SO 状态漂移；历史数据可能被再次出库。
- **证据强度：** Confirmed。
- **缓解备注（EAOS）：** 迁移不能仅按状态判断是否扣库，应以库存台账和来源号交叉验证。
- **交叉引用：** [Ops Order](../ops/order.md)、[Ops Delivery](../ops/delivery.md)。

### DW-007 — Brand 双轨

- **触发条件：** Legacy 页面保存 `brand_profiles`，V15.1 API/seed 读取独立三表。
- **影响：** 文档与 Foundation API 对“默认公司/Logo”回答不同。
- **证据强度：** Confirmed；未发现双向同步。
- **缓解备注（EAOS）：** 迁移必须标注每个消费方当前读取源，不能直接合并同名字段。

### DW-008 — 审批双轨

- **触发条件：** 用户在业务 Type A 页面确认，或对既有 Approval Center 记录批准；活动业务 apps 未见建立中心审批记录。
- **影响：** 两种动作均可被口头称为“approved”，但审计、释放副作用和责任主体不同。
- **证据强度：** Confirmed。
- **缓解备注（EAOS）：** 状态词必须区分 Confirmed、Approved、Released、Executed。
- **交叉引用：** [Governance Approval](../governance/approval.md)。

---

## 4. 只读来源路径

| Path | Risk IDs | Why cited |
|------|----------|-----------|
| `apps/inventory/services.py` / `repository.py` | DW-001, DW-005, DW-006 | 库存、产品镜像、台账、DO 状态多写 |
| `apps/product/services.py` / `repository.py` | DW-001 | 产品库存旁路 |
| `apps/procurement/services.py` | DW-005 | PO 收货逐行过账 |
| `apps/sample/services.py` | DW-001, DW-005 | Sample 入库复用库存镜像与台账多写 |
| `apps/sales/services.py` / `repository.py` | DW-002, DW-006 | SO 镜像与 Sales 建 DO |
| `apps/finance/services.py` / `repository.py` | DW-002, DW-003, DW-004 | Receipt、AR、AP、付款链 |
| `runtime/v14/legacy_support.py` | DW-003, DW-004, DW-007, DW-008 | 并行表结构和旧 helper |
| `apps/brand_center/v14_residual.py` | DW-007 | 活动 Legacy 品牌写入口 |
| `apps/brand_center/repository.py` | DW-007 | V15.1 并行三表 |
| `v15/enterprise_branding/` | DW-007 | JSON 锁、主题、审计 |
| `apps/approval/services.py` / `repository.py` | DW-008 | 中心审批记录流 |
| `apps/ui_center/domain_dashboards.py` | DW-003 | 同一 Dashboard 混用 SO−Receipts 与 `ar_records` 口径 |
| `apps/quotation/services.py` / `apps/sales/services.py` / `apps/procurement/services.py` / `apps/inventory/services.py` | DW-008 | 本地 Human Approved |
| `docs/reports/Business_Strong_A002_Inventory_Report.md` | DW-001, DW-005 | 库存镜像与台账审计 |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | DW-006 | DO 创建/出库历史边界 |
| `MODULE_BOUNDARY_REPORT.md` | All | 跨模块 owner 与 posting/reconciliation 缺口 |
| `docs/knowledge/legacy-extract/ops/` | DW-001, DW-005, DW-006 | 已有 Ops 知识交叉引用 |
| `docs/knowledge/legacy-extract/finance/` | DW-002, DW-003, DW-004 | 已有 Finance 知识交叉引用 |

**UNKNOWN 检索范围：** 上述目录及生产数据库差异核对；静态仓库不能证明现有数据是否已漂移。

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
