# 单据编号与序列

## Scope与证据强度

本页覆盖 Quote、SO、DO、PO、Receipt、Payment、Transfer、采购 Invoice、AR/AP、Sample、客户/供应商/产品编码，以及 NDE 展示编号。

- **强证据：** 活跃写入路由、服务、DDL 和打印引擎。
- **中证据：** Legacy 或工具层生成器存在，但未证明被主写入流程调用。
- **弱证据：** 统一编号服务和全球 ID 仅见于规划或宪章，未接入当前单据写入。
- **核心结论：** 系统没有统一业务序列表；业务编号列普遍无数据库唯一约束。

## 业务规则

- **NUM-R01 Quote：** 新建使用日期加当日计数序号；复制使用秒级时间戳。工具层另有时间戳生成器，但新建主流程不调用。
- **NUM-R02 SO：** Quote 转 SO 时主要由 Quote 主键派生；同一 Quote 重复转换有存在性守卫。工具层时间戳规则未接线。
- **NUM-R03 DO：** 销售路径使用秒级时间戳，库存转换路径由 SO 主键派生；两条活跃路径规则不同。
- **NUM-R04 PO：** 新建采购单使用秒级时间戳。
- **NUM-R05 Receipt：** 由 SO 主键和该 SO 已有收款笔数派生，是 SO 内序列而非全局序列。
- **NUM-R06 Payment/Transfer：** 活跃路径分别使用 `PAY`、`TRF` 加秒级时间戳；Legacy 生成器使用不同前缀。
- **NUM-R07 采购 Invoice/AP：** 采购发票使用 `PINV` 加时间戳；AP 依赖采购发票关联，没有独立 AP 业务号。
- **NUM-R08 AR：** 创建时主要保留 DO 来源号，独立 AR 号常为空；打印时回退到来源号。此 AR 是应收记录，不应自动等同于税务发票。
- **NUM-R09 Sample：** 活跃路径使用 `SP` 加时间戳，Legacy 生成器使用不同的 `SM` 前缀。
- **NUM-R10 主数据编码：** Customer、Supplier、Product 的 code 由表单手工输入；相应自动生成工具存在但未接入新增主流程。
- **NUM-R11 展示派生号：** Invoice、Packing List、Proforma Invoice、Statement、Certificate 可在 NDE 打印语境中由来源号或来源 ID 拼接；这不证明存在对应持久化单据。
- **NUM-R12 编号在插入时确定，状态变化不重算编号。**
- **NUM-R13 主键自增序列与业务编号分离；数据库自增机制不承担业务单号生成。**

## 流程

1. 新建 Quote 时查询当日/现有计数并形成编号；复制 Quote 改走时间戳规则。
2. Quote 转 SO 时使用 Quote ID 派生编号，并检查是否已有 SO。
3. SO 转 DO 可进入销售或库存路径，分别形成时间戳号或 SO ID 派生号。
4. SO 收款按该 SO 已有收款记录形成分笔号。
5. DO 经人工确认形成 AR 时，AR 沿用 DO 来源号，不建立可靠的独立 AR 序列。
6. PO 使用时间戳号；PO 转采购发票时形成 PINV 号，AP 通过发票 ID 关联。
7. 打印时 NDE 读取持久化业务号，或为派生文档临时形成展示号。

## 校验

- **NUM-V01** `quote_no`、`so_no`、`do_no`、`po_no`、`receipt_no` 及主要手工 code 未见数据库 UNIQUE 约束。
- **NUM-V02** 多数编号列允许空值，非空主要依赖应用层。
- **NUM-V03** Quote 的计数加一不是原子序列；并发请求可能取得相同结果，且计数未证明按租户隔离。
- **NUM-V04** 秒级时间戳生成无随机尾码、唯一约束或碰撞重试；同秒写入可静默重复。
- **NUM-V05** Quote 转 SO 有重复转换守卫；两条 DO 路径没有统一重复守卫。
- **NUM-V06** 库存 DO 路径固定由 SO ID 派生，重复调用可插入同号多行。
- **NUM-V07** Receipt 在余额不大于零时停止创建，但其分笔序号不是数据库序列。
- **NUM-V08** 同一 PO 的采购发票存在应用层重复检查。
- **NUM-V09** 新 DO→AR 流程要求人工确认；旧创建入口与残留路径仍需区分。
- **NUM-V10** 销售订单索引使用的列名与主要业务号列存在错位风险，不能视为 SO 号唯一保护。
- **NUM-V11** Customer、Supplier、Product 的手工编码无数据库唯一保护。

## 数据含义

| 字段/概念 | 含义 |
|---|---|
| `quote_no` | 对外报价单号；新增与复制格式不同 |
| `so_no` | 销售订单号，主路径由 Quote ID 派生 |
| `do_no` | 发货/出库单号，存在时间戳和 SO ID 两套规则 |
| `po_no` | 采购订单号 |
| `receipt_no` | 收款分笔号，不是税务发票号 |
| `payment_no` / `transfer_no` | 付款和资金转账编号 |
| `invoice_no` | 采购发票编号；销售侧打印 Invoice 可能只是 AR/来源号展示 |
| `ar_no` / `source_no` | 独立应收号与应收来源号；前者常空、后者通常为 DO 号 |
| AP | 无独立 `ap_no`，通过采购发票 ID 关联 |
| `sample_no` | 样品编号 |
| `customer_code` / `supplier_code` / `product_code` | 手工主数据编码 |
| `document_number` | NDE 打印语境中的展示编号，不是统一业务主键 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Draft` | Quote、PO 等新建草稿态 |
| `Pending` / `Open` | DO 或订单待处理语境；不同模块用词不统一 |
| `Shipped` | 已发货 |
| `Paid` / `Partial` / `Unpaid` | 收付款完成度 |
| `New` | Sample 初始状态 |
| `Active` / `Inactive` | 主数据启停状态 |

状态词不参与编号重算，也不能弥补编号唯一性缺口。

## 冲突风险

- Quote 新增与复制使用不同格式；迁移、排序和外部解析不能假设单一长度。
- 同一 SO 可经两条 DO 路径得到不同格式，也可能产生重复行。
- 时间戳仅精确到秒，批量或并发创建存在碰撞。
- 计数加一缺少原子锁，且跨租户计数可能互相影响。
- 活跃与 Legacy 前缀不一致，迁移脚本若调用未接线工具可能制造第三套格式。
- 打印派生号可能被误当作真实 Invoice、Statement 或 Certificate 主数据。

## UNKNOWN

- `knowledge_documents.doc_no` 的实际生成器 **UNKNOWN**。已检索 Python 写入路径和 `v15/knowledge/`，未发现插入生成链。
- 独立销售税务 Invoice 编号 **UNKNOWN/未证明存在**。已检索 `apps/finance/` 和 `document/`，观察到的是 AR 与 NDE 展示派生。
- 统一 `services/shared/numbering.py` **UNKNOWN/规划未落地**。已检索 `services/`，目标文件不存在。
- BOOK22 全球 `DOC-*` ID 写入现有 ERP 单据的链路 **UNKNOWN/未接线**。已检索 `core/identity/` 和各业务插入路径。
- DO 多单是否为明确允许的部分发货业务规则 **UNKNOWN**；编号实现本身没有给出该业务判定。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\supplier\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\upgrade_patch.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\phase3_indexes.sql`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\v14_platform.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\design\v18\V18_IMPLEMENTATION_ROADMAP.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\constitution\volume-02-eaos\BOOK22.md`
