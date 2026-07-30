# ADR-0317 — FX Propagation & Revaluation Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → future Finance / Locale Package Surface  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；仍不得凭本文件打开 CRUD / Kernel / Alembic

## 背景

Legacy 知识抽取表明：报价头可持有币种/汇率快照，但 Convert 不写入 SO；收款路径可硬编码币种；付款/转账缺交易汇率；资金账户币种不驱动折算；期间重估、期末关账、已实现/未实现汇兑损益实体为强缺口。多币种在 Legacy 多为展示碎片，非闭合会计传播链。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/fx-propagation-deepen/**`
- `docs/knowledge/legacy-extract/fx-revaluation-deepen/**`
- `docs/knowledge/legacy-extract/locale-commerce/currency.md`
- 与 Convert / 收款 / AP 清算邻包交叉（只读）

## 决策

1. **不得将 Legacy「单据上有 currency 字段」等同为 FX 已传播或已入账。**  
2. **交易链快照契约**：若启用多币种，Quote→SO→履约/应收→现金事件须显式传播或重算 **交易币种、记账币种、汇率、汇率时点**；Convert 省略写入视为缺陷策略，不得默认继承。  
3. **现金事件（收款/付款/转账）必须携带或解析交易汇率**（相对记账币种）；禁止硬编码单一币种作为隐藏默认而不留审计（与 [ADR-0315](ADR-0315-ar-ap-reconcile-rewrite-boundary.md) 分配链交叉）。  
4. **期间重估与关账**若启用，须为可调度、可审计作业，产出可引用的重估分录或等价事件；不得仅有汇率表而无重估结果实体。  
5. **已实现 / 未实现汇兑损益**须可区分建模（或显式声明产品不支持并阻断跨币种清算）；跨币种清账不得静默吞掉汇差。  
6. **本 ADR 不打开** 多币种总账 CRUD、汇率源集成定案、Alembic、Brain execute、Twin authorize。

## 后果

- 商务条款快照（[ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md)）中的 FX 字段以本边界为会计传播下游约束。  
- Research 可将 Convert 丢汇率、收款硬编码币种作为 live 主题；intake 不因本提案 Complete。

## 非目标

- 不定案浮动/固定汇率政策细节  
- 不选择具体会计制度下的汇兑科目  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) Convert 条款快照  
- [ADR-0315](ADR-0315-ar-ap-reconcile-rewrite-boundary.md) 勾兑与跨币种清账交界  
- [legacy-extract README](../knowledge/legacy-extract/README.md)  
- Gap review canvas: `legacy-extract-gap-review`
