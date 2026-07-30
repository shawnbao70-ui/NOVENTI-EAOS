# ADR-0370 — GL AP Bridges Boundary

**状态：** Accepted（PHX-G338）  
**日期：** 2026-07-26  
**里程碑：** PHX-G338  
**授权源：** [Coding Authorization](../project/FIN_GL_AP_BRIDGES_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 扩展 GL3 bridge map：`ap_control` + `ap_expense`；付款侧复用 `cash`。  
2. 仅 bridge 已 posted 的 ApBill / 已 applied 的 ApPayment；开账期 + 幂等。  
3. 不打开银行文件导入或 Brain/Twin 写财务。
