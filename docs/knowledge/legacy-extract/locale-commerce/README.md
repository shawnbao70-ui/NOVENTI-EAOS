# Legacy Knowledge Extract — Locale Commerce Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/locale-commerce/**`  
**Verified:** 2026-07-23

## Scope

本包提炼 Legacy 中影响跨地区交易与展示的三类知识：币种/汇率、税务，以及语言/地区本地化。内容只描述可观察到的规则、流程、校验、数据语义与诚实缺口，不复制源码。

## Modules

- [Currency / FX](currency.md)
- [Tax](tax.md)
- [Locale / i18n](locale_i18n.md)
- 汇总见 [INDEX.md](INDEX.md)

## Hard boundaries

- `currency_settings` 与单据上的 `currency`/`exchange_rate` 是不同层次；存在字段不代表已实现统一汇率服务或自动重估。
- `tax_settings` 是国别税率字典，`tax_records` 是税务事项台账；两者之间未观察到自动计算或过账关系。
- 含税价、未税价、税额拆分以及税务发票闭环未被可靠实现，不从税率主数据推断这些能力。
- UI 语言只改变显示，不应改变业务状态、金额、权限或数据关系；Legacy 中仍有硬编码与状态词混用。
- 币种格式化只负责展示，不能替代汇率换算；国家默认币种也不能静默覆盖单据币种。
- 本包不打开或推导 external PSP 能力。
