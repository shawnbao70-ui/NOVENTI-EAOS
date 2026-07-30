# ADR-0363 — Finance PSP Live Network Boundary

**状态：** Accepted（PHX-G331 / PSP-NET）  
**日期：** 2026-07-26  
**里程碑：** PHX-G331  
**归属：** Business Package / Finance  
**授权源：** [Coding Authorization](../project/FIN_PSP_NETWORK_LIVE_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

F3 仅交付 stripe_like stub（无 I/O）。PO 授权打开 PSP live：在 provider + network flag + URL 齐全时允许出站 HTTP apply_receipt，默认仍 OFF。

## 决策

1. Flag：`EAOS_PSP_NETWORK` / `ENABLE_PSP_NETWORK`（默认 false）。  
2. Provider：`EAOS_PSP_PROVIDER=stripe_like`（或未来扩展）才可选 live；`fake` 仍本地 Fake；`off` → RejectAll。  
3. Endpoint：`EAOS_PSP_URL` 必填才 `live_transport=true`；缺省 → stub fail-closed。  
4. Optional bearer：`EAOS_PSP_BEARER`；不得写入日志。  
5. 不得通过 API 打开网络；无 Alembic。

## 关联

- [ADR-0358](ADR-0358-finance-psp-provider-adapter.md)  
- [ADR-0360](ADR-0360-finance-tax-network-live-boundary.md)（Tax-NET 模式参考）  
- [Coding Authorization](../project/FIN_PSP_NETWORK_LIVE_CODING_AUTHORIZATION_SUMMARY.md)
