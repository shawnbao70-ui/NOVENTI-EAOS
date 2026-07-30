# ADR-0273 — OpenAPI PaymentClearing Success Schemas Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G254  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U127**

## 决策

`PaymentClearingRequest` / `Envelope` / `Result` → `additionalProperties: false`；
`payment_cleared` const true；`audit_id` type `[string,null]`。marketplace **1.2.13**；
ops **1.0.52**；inventory PHX-G254。external PSP HARD HOLD 仍关。
