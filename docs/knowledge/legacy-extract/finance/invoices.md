# 发票（Invoice）— Legacy Knowledge

**Evidence strength:** Medium — purchase invoice behavior is strong; sales invoice identity is fragmented  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. 范围与证据强度

Legacy 中“发票”至少指向三种不同对象：

1. **采购发票**：`purchase_invoices`，由采购单创建，并同步生成 AP；
2. **交付后的 Invoice 动作**：只写 `ar_records`，明确声明不是税务或商业发票；
3. **NDE/打印商业发票**：文档呈现能力，可从业务数据组装并打印，但不等同于已建立可核销的销售发票主账。

Finance 模块元数据与仓储声明了 `invoices` 主表及发票路由目标，但 DDL 中未发现该表，完整销售发票 CRUD、状态机、税额和核销闭环也无运行证据。EAOS 不应据此虚构一个成熟的 Legacy 销售发票域。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / 矛盾 | EAOS 重写备注 |
|----|----------|----------|--------------|----------------|
| IV-R1 | 采购发票只能从已存在的采购单生成 | 创建采购发票 | 入口为 GET 型动作，缺少明确人工确认页 | 改为有权限、幂等、可审计命令 |
| IV-R2 | 每张采购单最多生成一张采购发票 | 创建前检查 | 服务层检查，未见数据层唯一约束 | 对 `purchase_id` 建唯一约束 |
| IV-R3 | 采购发票金额取采购单总额 | 创建时 | 不读取逐行税额、运费或差异 | 支持三单匹配与发票差异 |
| IV-R4 | 采购发票号使用 `PINV` + 时间戳 | 创建时 | 无法体现法定供应商发票号 | 区分系统编号与供应商票号 |
| IV-R5 | 新采购发票已付为 0、余额为全额、状态 `Unpaid` | 创建成功 | 无草稿、审核、作废状态 | 设计采购发票生命周期 |
| IV-R6 | 采购发票与 AP 同步建立，AP 引用发票 ID | 创建成功 | 未观察到部分失败回滚的显式异常处理 | 单事务提交并记录领域事件 |
| IV-R7 | 交付单上的 Invoice 批准动作只产生全额未收 AR | Human Approved | 名称容易误导为正式发票 | UI 与 API 改名为“记应收” |
| IV-R8 | 交付未发运仍允许记应收，只显示警告 | Post AR | 业务确认点不强制 | 收入/应收确认政策应配置 |
| IV-R9 | 同一交付单重复记应收仅警告，不阻止 | Post AR | 可重复计提 | 来源唯一、冲销与重开必须显式 |
| IV-R10 | NDE 可生成/打印 Invoice 文档，并展示商业与付款信息 | 文档预览/打印 | 文档生成不等于发票入账 | 分离 Document、Invoice、AR 三个聚合 |
| IV-R11 | 发票、收款和应收在权限目录中属于 Finance/Invoices/Receipts 等不同能力 | 访问页面/动作 | 标识存在混用 | EAOS 采用统一资源与操作权限 |
| IV-R12 | AI 不得静默创建发票或应收 | 建议/确认页面 | 旧辅助挂载失败时可能静默忽略 | 所有财务事实写入均需人类授权 |
| IV-R13 | 采购页面叙事要求收货后开票 | 采购详情操作 | 创建服务未校验采购单已收货 | 三单匹配条件必须由服务端强制 |
| IV-R14 | AR 打印编号在应收编号为空时可退化使用来源单号 | 打印 Invoice | DO 记应收流程未填写 `ar_no` | 系统应生成独立、不可重复的应收/发票编号 |

---

## 3. 流程

### 3.1 采购发票

1. 用户从采购单发起开票。
2. 系统校验采购单存在。
3. 检查相同采购单是否已有采购发票。
4. 以采购单供应商和总额建立采购发票。
5. 初始化为全额未付。
6. 同步建立同额 AP。
7. 跳转至 AP Dashboard。

### 3.2 交付记应收（名称含 Invoice，但不是发票）

1. 用户从交付单进入确认页。
2. 系统展示客户、交付号、订单号、明细和金额。
3. 页面明确提示“创建应收计提，不是税务/NDE 商业发票”。
4. 系统提示重复来源及未发运状态，但不硬拦截。
5. 人工确认后写一条 `Unpaid` AR。

### 3.3 商业发票文档

1. 文档引擎从报价、订单、交付等上下文读取抬头、产品、金额、付款条件等信息。
2. 选择 Invoice 文档类型并生成预览/打印内容。
3. 打印能力服务于对外文件；未观察到它自动建立销售发票主账或参与收款核销。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| IV-V1 | 采购单必须存在 | Hard | 不存在则返回采购中心 |
| IV-V2 | 同采购单不得已有采购发票 | Hard at service | 已存在则不重复创建 |
| IV-V3 | 供应商必须有效存在 | Weak | 通过采购单引用，未见显式校验 |
| IV-V4 | 发票金额必须大于零 | Missing | 直接取采购总额 |
| IV-V5 | 税率、税额、含税/未税一致性 | Missing | 活跃创建流程未见 |
| IV-V6 | 供应商法定发票号唯一 | Missing | 当前只有系统号 |
| IV-V7 | DO 记应收必须 Human Confirm | Hard | 取消/草稿不入账 |
| IV-V8 | 同一 DO 只能记一次应收 | Warning only | 页面告警但仍可批准 |
| IV-V9 | DO 必须发运/完成 | Warning only | 开放状态仍可计提 |
| IV-V10 | 正式销售发票状态机 | Not evidenced | `invoices` 域声明不足以证明运行能力 |
| IV-V11 | 文档打印后自动入账 | Not present | 文档与主账分离 |
| IV-V12 | 采购单已收货才允许开票 | UI only | 创建服务端未强制 |
| IV-V13 | AR 编号必填且唯一 | Missing | DO 记应收未写 `ar_no` |

---

## 5. 数据含义

### 5.1 采购发票

| Field | 含义 |
|-------|------|
| `invoice_no` | Legacy 系统生成的采购发票编号 |
| `purchase_id` | 唯一业务来源采购单 |
| `supplier_id` | 开票供应商 |
| `invoice_date` | 系统创建日期 |
| `invoice_amount` | 取自采购单总额的发票金额 |
| `paid_amount` | 累计已付；创建时为 0 |
| `balance_amount` | 未付余额；创建时等于发票金额 |
| `status` | 创建时 `Unpaid` |

### 5.2 交付记应收

| Field | 含义 |
|-------|------|
| `source_no` | 交付单号，是应收来源标识 |
| `ar_no` | 独立应收编号；当前 DO 记应收流程可能为空 |
| `customer_id` / `customer_name` | 债务客户及名称快照 |
| `ar_date` | 应收计提日期 |
| `amount` | 交付单总额 |
| `balance` | 初始等于全额 |
| `status` | 初始 `Unpaid` |

### 5.3 易混淆对象

| 名称 | Legacy 实际含义 |
|------|-----------------|
| `invoices` | Finance 仓储/模块边界声明的主表；未发现 DDL，属于规划/幽灵表风险 |
| `purchase_invoices` | 可确认运行的采购发票表 |
| `/delivery_order/{id}/invoice` | 交付记应收确认页，不是正式发票 |
| Invoice print / NDE document | 对外文档呈现，不自动等于财务入账 |
| Proforma Invoice | 报价/形式发票类商业文件，不是应收主账 |

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `business_modules/finance.md` | 发票域边界、目标路由、表声明与 phantom-table 风险 |
| `apps/finance/services.py` | 采购发票创建与 AP 同步 |
| `apps/finance/router.py` | 采购发票入口及交付记应收别名 |
| `apps/finance/repository.py` | `invoices` 主表声明及缺乏对应页面业务实现 |
| `apps/inventory/services.py` | DO Invoice 的真实 AR 语义、确认与重复告警 |
| `apps/inventory/router.py` | DO Invoice GET/POST 入口 |
| `runtime/v14/legacy_support.py` | `purchase_invoices`、`ar_records` 字段 |
| `document/nde_engine.py` | Invoice 文档组装及付款字段 |
| `templates/print/invoice_document.html` | 商业发票打印呈现 |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | “AR accrual — not tax invoice”边界 |
| `docs/reports/NDE_INVOICE_DO_UPGRADE_REPORT.md` | Invoice/DO 文档能力证据 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
