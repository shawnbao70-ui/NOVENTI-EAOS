# ADR-0376 — Tax Invoice ↔ Credit Note Link Boundary

**状态：** Accepted（PHX-G344）  
**日期：** 2026-07-26  
**里程碑：** PHX-G344  
**授权源：** [Coding Authorization](../project/FIN_TAX_CREDIT_LINK_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 税票与贷项须显式受控链接；状态/谱系 fail-closed。  
2. 不扩大 live tax NETWORK 行为面。  
3. 不因链接自动 void 税票或打款。
