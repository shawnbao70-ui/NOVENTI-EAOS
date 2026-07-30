# ADR-0259 — OpenAPI WebAuthn PublicKeyCredentialCreationOptions Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G240  
**归属：** OpenAPI Inventory / Auth / WebAuthn  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U113**；PO cue「充分授权…自主开发…加快」

## 背景

`WebauthnRegisterOptionsResponse.publicKey` 与 verify request credential/response
仍为 opaque，而 `mint_registration_options` / `verify_and_mint_registration`
live 键已稳定。

## 决策

1. 新增 `PublicKeyCredentialCreationOptions` + nested RP/User/Param/Selection。  
2. Options request/response `additionalProperties: false`；publicKey → `$ref`。  
3. Verify request credential/response → named `$ref`（residual browser keys allowed）。  
4. auth **1.3.24**；ops **1.0.46**；inventory PHX-G240。  
5. **不**打开 attestation-crypto HARD HOLD。

## Explicit Out

Attestation crypto verify；ContextEcho.echo / free-form invent；Brain/Twin/PSP。
