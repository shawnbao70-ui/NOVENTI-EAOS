# ADR-0307 — OpenAPI Outer-Close Regression Guard

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G288  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U161**

## 决策

常驻契约：除 intentional residual allowlist 外，全部 named `type:object` 外层必须
`additionalProperties: false`。Allowlist = WebAuthn attestation 三袋 + IdP JWKS 两袋
+ `ContextEchoRequest`（命名原匿名 echo body；仍 AP:true；≠ invent 域语义）。
锁定 Natural Pause；≠ softener 空环；≠ close residuals。ops **1.0.69**；inventory PHX-G288。
