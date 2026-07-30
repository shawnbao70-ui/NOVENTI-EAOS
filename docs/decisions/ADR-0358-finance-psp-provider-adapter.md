# ADR-0358 — Finance PSP Provider Adapter Boundary

**状态：** Accepted（PHX-G326 / F3）  
**日期：** 2026-07-26  
**里程碑：** PHX-G326  
**归属：** Business Package / Finance  
**授权源：** [Coding Authorization](../project/FIN_PSP_PROVIDER_ADAPTER_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

F2 已交付 opt-in `receipt_psp_required` + fail-closed `PspPort`（RejectAll / Fake）。F3 加深 provider 选型与网络门闩，镜像 Tax3：默认 OFF，无实网 I/O。

## 决策

1. `resolve_psp_port()` 按 `EAOS_PSP_PROVIDER` + network flag 选择 RejectAll / Fake / StripeLike stub。  
2. Network 默认 OFF；ON 且无配置时仍 fail-closed，禁止 live HTTP。  
3. 只读 adapter status HTTP；不得通过 API 打开实网。  
4. 无 Alembic（无新表）；实网启用须另开 `ENABLE_PSP_NETWORK` 治理。

## 关联

- [ADR-0348](ADR-0348-finance-receipt-psp-port.md)  
- [ADR-0350](ADR-0350-finance-tax-authority-adapter.md)（Tax3 模式参考）  
- [Coding Authorization](../project/FIN_PSP_PROVIDER_ADAPTER_CODING_AUTHORIZATION_SUMMARY.md)
