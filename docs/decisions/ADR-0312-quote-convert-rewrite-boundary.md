# ADR-0312 — Quote→SO Convert Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → future Business Package Surface  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；仍不得凭本文件打开 CRUD / Kernel / Alembic

## 背景

Legacy 知识抽取（Phase-10…19）已对报价转换链形成可引用证据：Approve≠Convert、中英状态族不可安全归一、一报价一 SO 仅为应用层读后写、佣金与生命周期钩子可部分失败、商务条款多数不随 Convert 传播。MASTER_PLAN 禁止过早业务模块；本 ADR 只固定 **EAOS 重写边界**，不实现产品。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/quote-convert-policy-deepen/**`
- `docs/knowledge/legacy-extract/convert-atomicity-deepen/**`
- `docs/knowledge/legacy-extract/quotation-deepen/**`
- `docs/knowledge/legacy-extract/order-chain/so_convert.md`
- `docs/knowledge/legacy-extract/commission-ledger-deepen/**`
- 根索引矛盾表（Approve vs Convert、原子副作用、条款传播）

## 决策

1. **Legacy Convert 行为不得原样继承为 EAOS 默认策略。**  
2. EAOS 必须在实现前用独立状态词汇区分至少：草稿发布（publication）、赢单/确认（commercial win）、销售订单创建（SO create）、履约放行（fulfillment release）。禁止将 Quote `已确认` 直接映射为 `Won` 或 `Sent`。  
3. **Approve 与 Convert 必须可配置为分离门禁**：默认不得假设「本地 Human Confirm / Sent」是 Convert 的充分或必要条件；目标策略须在 Package/Workflow 中显式声明。  
4. **一报价一有效 SO** 必须由事务权威保证（唯一约束 / 幂等键 / 命令身份），不得仅依赖读后写。  
5. **Convert 的主结果与副作用分离建模**：SO 创建成功不得静默吞掉佣金/追溯失败而不留可观察失败；目标为同事务或明确补偿/重试队列（实现另 ADR）。  
6. **商务条款传播** 以显式快照契约为准（付款/信用/FX/折扣/Incoterms）；金额行快照 ≠ 完整商业合同。缺字段必须失败或显式降级策略，不得静默丢失。  
7. **本 ADR 不打开** CRM/Quote/SO 产品 CRUD、Terminal 业务面、Alembic、Brain execute、Twin authorize。

## 后果

- 后续 Industry/Business Package Surface（报价/订单）设计必须以本边界为输入。  
- Smart Terminal 演示移交（`product.sample` / `ops.order`）仍仅为演示，不构成本 ADR 的实现。  
- Research T2/T3 可将 Convert 异常路径作为 live 采集主题；intake Complete 不因本提案改变。

## 非目标

- 不规定具体 schema / API payload  
- 不选择佣金会计制度  
- 不替换中央审批 vs V18 本地确认的选型（见审批/鉴权相关 ADR）  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0309](ADR-0309-legacy-knowledge-extract-crm-sales.md) Knowledge CRM/Sales  
- [legacy-extract README](../knowledge/legacy-extract/README.md) Next candidates / contradictions  
- Gap review canvas: `legacy-extract-gap-review`（Cursor canvases）
