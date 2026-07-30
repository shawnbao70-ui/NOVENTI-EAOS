# ADR-0265 — OpenAPI IdP JWKS Document Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G246  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U119**

## 背景

`CreateIdpIssuerRequest.jwks_json` object arm 为 opaque；live JWT verify
消费 `keys[]` 与 RSA `kty`/`kid`/`n`/`e`。

## 决策

1. 新增 `IdpJwksDocument` / `IdpJwksKey`；object arm → `$ref`。  
2. **保持** `additionalProperties: true`（RFC residual / 存储透传）。  
3. platform **1.0.10**；ops **1.0.49**；inventory PHX-G246。  
4. 不关闭 JWKS bag；不 invent attestation-crypto / free-form。
