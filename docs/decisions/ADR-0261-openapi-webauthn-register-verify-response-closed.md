# ADR-0261 — OpenAPI WebAuthn RegisterVerifyResponse Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G242  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U115**

## 决策

`WebauthnRegisterVerifyResponse.additionalProperties=false`；live 键已命名；
`attestation_verified`/`next_action` const 对齐 live emit。不打开 attestation-crypto HARD HOLD。
auth **1.3.25**；ops **1.0.47**；inventory PHX-G242。
