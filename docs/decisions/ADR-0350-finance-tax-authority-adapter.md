# ADR-0350 — Finance Tax Authority Adapter (NETWORK OFF)

**状态：** Accepted（design + coding boundary for PHX-G318 / Tax3）  
**日期：** 2026-07-26  
**里程碑：** PHX-G318  
**归属：** Business Package / Finance（非 Kernel）  
**授权源：** [Coding Authorization Summary](../project/FIN_TAX_AUTHORITY_ADAPTER_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Tax2（PHX-G317）交付了税率字典与 fail-closed `TaxAuthorityPort`（RejectAll 默认 + 测试 Fake）。Tax3 引入可切换的 Network adapter **骨架**，但必须保持 `ENABLE_*_NETWORK` / `EAOS_TAX_NETWORK` 默认 OFF，且本切片禁止实网 HTTP。

## 决策

1. **Env gate：** `EAOS_TAX_NETWORK`（别名 `ENABLE_TAX_NETWORK`）；仅 `1/true/yes/on` 为真；默认 false。  
2. **解析：** flag OFF → `RejectAllTaxAuthority`；ON → `NetworkTaxAuthorityAdapter` stub，仍 fail-closed（无 endpoint / 无 live transport）。  
3. **`live_transport` 恒为 false**（Tax3）；不得发起真实税局 HTTP。  
4. **可选只读状态：** `GET /v1/finance/adapters/tax-authority` 反射 env；不得提供 API 启用网络。  
5. **无 Alembic**；配置不落库。GL / 实网申报 / F3 PSP network 均 Out。

> **Note（PHX-G328）：** live HTTP transport 边界由 [ADR-0360](ADR-0360-finance-tax-network-live-boundary.md) 承接。Tax3 行为保留：flag ON 且无 `EAOS_TAX_AUTHORITY_URL` 时仍为 `network_stub` / `live_transport=false`。

## 后果

- Tax2 Fake 注入行为不变；生产默认仍 RejectAll。  
- 打开 flag 仅切换到 stub，issue 在 authority-required 时仍 COMMON_CONFLICT。

## 非目标

- 电子发票通道、实网申报、endpoint 配置表  
- GL1+、Brain/Twin、F3

## 关联

- [ADR-0349](ADR-0349-finance-tax-rate-authority-port.md)  
- [ADR-0360](ADR-0360-finance-tax-network-live-boundary.md)（Tax-NET live）  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)  
- [Coding Authorization](../project/FIN_TAX_AUTHORITY_ADAPTER_CODING_AUTHORIZATION_SUMMARY.md)
