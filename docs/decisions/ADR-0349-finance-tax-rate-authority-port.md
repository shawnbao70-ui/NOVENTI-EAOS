# ADR-0349 — Finance Tax Rate + TaxAuthorityPort Boundary

**状态：** Accepted（design + coding boundary for PHX-G317 / Tax2）  
**日期：** 2026-07-26  
**里程碑：** PHX-G317  
**归属：** Business Package / Finance（非 Kernel）  
**授权源：** [Coding Authorization Summary](../project/FIN_TAX_RATE_AUTHORITY_PORT_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Tax1（PHX-G316）交付了税票 shell（draft→issued→voided），但未提供可引用税率字典，也未引入税局/权威校验端口。ADR-0316 要求单据税额可挂钩税码；F2 PspPort 已建立「策略 opt-in + fail-closed Port + Fake 仅测」模式。Tax2 将该模式落到税率与权威校验，且**不**打开实网申报。

## 决策

1. **TaxRate** 是租户内税率字典（tax_code / name / rate_percent / active|archived），不是交易快照引擎，也不是报税期间模型。  
2. **TaxAuthorityPort** 是 fail-closed 校验端口；默认 `RejectAllTaxAuthority`；仅允许测试用 Fake；本切片禁止 live filing / network adapter。  
3. **TenantTaxAuthorityPolicy.tax_authority_required** 默认 `false`；仅当开启时，税票 issue 必须绑定 active TaxRate 并调用 Port，成功后可持久化 `authority_ref` / `authority_status`。  
4. HTTP 暴露在 `/v1/finance/tax-rates` 与 `/v1/finance/policies/tax-authority`；不得在本切片暴露 filing、`ENABLE_*_NETWORK`、GL/journal。  
5. Tax3 adapter、实网启用、Brain/Twin 均 Out。

## 后果

- Tax1 生命周期保持；Tax2 仅加深 rate + authority gate。  
- OpenAPI / 合同测试须证明无申报与无网络开关表面。

## 非目标

- 电子发票通道供应商、法域自动申报、税基引擎完整化  
- Tax3 Authority adapter、`ENABLE_TAX_NETWORK`  
- GL/CoA/journal/period

## 关联

- [ADR-0316](ADR-0316-tax-invoice-rewrite-boundary.md)  
- [ADR-0348](ADR-0348-finance-receipt-psp-port.md)（若存在；F2 PspPort 模式）  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)  
- [Coding Authorization](../project/FIN_TAX_RATE_AUTHORITY_PORT_CODING_AUTHORIZATION_SUMMARY.md)
