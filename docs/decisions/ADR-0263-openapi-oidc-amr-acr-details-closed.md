# ADR-0263 — OpenAPI OIDC Amr/Acr Details Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G244  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U117**

## 背景

`OidcAmrRequiredDetails` / `OidcAcrRequiredDetails` 已命名 live 键（G210/G214），
但仍 `additionalProperties: true`。live emit 仅
`required_amr`/`present_amr`/`mfa_enrollment_url` 与
`required_acr`/`present_acr`/`mfa_enrollment_url`。

## 决策

两 schema `additionalProperties: false`；auth **1.3.26**；ops **1.0.48**；
inventory PHX-G244。不 invent free-form；不打开 HARD HOLD。
