# ADR-0316 — Tax Invoice Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → future Finance / Locale Package Surface  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；仍不得凭本文件打开 CRUD / Kernel / Alembic

## 背景

Legacy 知识抽取表明：无可核销销售税务发票主账；DO「Invoice」实质为 AR 计提；NDE Invoice 为打印呈现；税设置/税记录多为字典碎片；单据税额计算与报税期间/税号未闭合；Credit Note 多为模板映射而无入账/红冲命令。本能力在 Legacy 中多为**缺席**，EAOS 须作为新建边界设计，而非映射继承。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/tax-invoice-deepen/**`
- `docs/knowledge/legacy-extract/tax-filing-deepen/**`
- `docs/knowledge/legacy-extract/locale-commerce/tax.md`
- `docs/knowledge/legacy-extract/finance/invoices.md`
- `docs/knowledge/legacy-extract/return-reversal-policy-deepen/ar_credit_cancel.md`

## 决策

1. **不得将 Legacy DO Post AR / NDE 打印发票 / 税字典 三者任一等同为「税务发票权威」。** EAOS 若提供税票能力，须独立建模税票实体（开立、作废、红冲/贷项）与生命周期。  
2. **税票 ≠ AR ≠ 收款 ≠ 经营打印件。** 命令与状态机必须可区分；交叉引用允许，静默混写禁止（与 [ADR-0315](ADR-0315-ar-ap-reconcile-rewrite-boundary.md) 交叉）。  
3. **单据税额**须有可引用的计算契约（税基/税率/税额/含税口径），并挂钩税码与（若启用）报税期间；缺字段须失败或显式降级，不得静默为 0 且称为已计税。  
4. **作废/红冲/贷项**须为可审计命令并挂钩原税票与（若已分配）AR/收款链；打印模板 alone 不构成冲销。  
5. **报税申报/归档**若进入范围，须与税票事件可追溯；不得仅靠 UI「Tax Center」导航暗示已具备申报引擎。  
6. **本 ADR 不打开** 税票/报税产品 CRUD、本地税局集成定案、Alembic、Brain execute、Twin authorize。

## 后果

- Finance Package Surface 须把税票列为可缺省启用的新建能力，默认不从 Legacy 发票词面迁移。  
- Research live 采集（税号/期间/红冲）仍 Hold；intake Complete 不因本提案改变。

## 非目标

- 不定案具体税种表或国家包实现顺序  
- 不规定电子发票通道供应商  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0315](ADR-0315-ar-ap-reconcile-rewrite-boundary.md) AR/AP 勾兑  
- [ADR-0310](ADR-0310-legacy-knowledge-extract-finance.md) Knowledge Finance  
- [legacy-extract README](../knowledge/legacy-extract/README.md)  
- Gap review canvas: `legacy-extract-gap-review`
