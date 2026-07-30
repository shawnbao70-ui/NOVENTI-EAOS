# ADR-0315 — AR/AP Reconcile Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → future Finance Package Surface  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；仍不得凭本文件打开 CRUD / Kernel / Alembic

## 背景

Legacy 知识抽取表明：收款（`receipts` / SO 镜像）与应收（`ar_records` / DO Post AR）为并行事实，无 allocation/matching/write-off 作业；Customer360 与 Statement 可呈不同余额；`SO Paid`≠`ar_records Closed`；Treasury 付款与 `ap_records`/发票不分配、不清算；Invoice 复制 PO 头金额而无 PO–GR–Invoice 三单匹配；无唯一供应商余额权威。MASTER_PLAN 禁止过早业务模块；本 ADR 只固定 **EAOS 重写边界**。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/receipt-ar-reconcile-deepen/**`
- `docs/knowledge/legacy-extract/ap-payment-deepen/**`
- `docs/knowledge/legacy-extract/ap-settlement-deepen/**`
- `docs/knowledge/legacy-extract/finance/**`
- `docs/knowledge/legacy-extract/customer-deepen/ar_balance_view.md`
- 根索引矛盾表（Receipt≠AR、Payment≠AP clearing、三单匹配缺席）

## 决策

1. **Legacy 双轨余额视图不得原样继承为 EAOS 默认「已勾兑」语义。** 展示层可保留多视图，但必须标明权威口径与未分配差额。  
2. **客户侧：现金收款事件 ≠ 应收清算。** EAOS 必须显式建模至少：应收开立、收款登记、分配（allocation）、部分清账、核销/write-off、关闭；禁止「记一笔收款即等于 AR Closed」除非策略显式且可审计。  
3. **应收开立权威与履约/税票分离**：发运/完成可触发 AR 候选，但 Post AR、税票、经营余额计算不得混为同一命令的静默副作用而不留勾兑痕迹（与 ADR-0314 / 税票后续 ADR 交叉）。  
4. **供应商侧：银行/Treasury 付款 ≠ AP 清算。** 付款必须可分配到 AP/发票（含部分分配）；未分配付款不得更新「已付清」状态。  
5. **采购清算须具备可配置的匹配策略**（至少金额/数量/价差容差之一）；仅复制 PO 头金额到发票不得称为三单匹配完成。  
6. **每个主体（客户/供应商）在给定账本与币种下须有唯一可引用的余额权威**（或显式的「未对账多轨」产品状态）；禁止无说明地并列两套净额并都称为「余额」。  
7. **冲销与贷项**（Credit Note / AR cancel / 退款）须挂钩原单据与分配链；打印模板或状态标签 alone 不构成财务冲销（与 return/tax 后续 ADR 交叉）。  
8. **本 ADR 不打开** 收款/AR/AP/发票产品 CRUD、总账引擎选型定案、Alembic、Brain execute、Twin authorize。

## 后果

- 后续 Finance Package Surface 必须以「事件 + 分配 + 权威余额」为本输入，而非镜像字段同步。  
- Smart Terminal / 演示面不得宣称已实现勾兑。  
- Research 可将双余额、未分配付款作为 live 采集主题；intake Complete 不因本提案改变。

## 非目标

- 不规定具体会计科目表或 IFRS/本地 GAAP 选型  
- 不实现银行对账文件导入  
- 不定案税票引擎与 FX 重估（P2 候选）  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0310](ADR-0310-legacy-knowledge-extract-finance.md) Knowledge Finance  
- [ADR-0314](ADR-0314-fulfillment-rewrite-boundary.md) 履约边界（Accepted；AR 开立触发交界）  
- [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) / [ADR-0313](ADR-0313-command-authz-rewrite-boundary.md)  
- [legacy-extract README](../knowledge/legacy-extract/README.md)  
- Gap review canvas: `legacy-extract-gap-review`
