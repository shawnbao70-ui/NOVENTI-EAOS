# ADR-0297 — Contract Softener Wave3 + Ops Tip-Parity Guard

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G278  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U151**

## 决策

第三波 Foundation 契约 tip/version softener（g174/g180/g181）；
常驻守卫：ops OpenAPI `milestone` / `t0188_status` const 必须等于 live inventory tip。
≠ invent JWKS/WebAuthn residual / nested free-form。ops **1.0.64**；inventory PHX-G278。
