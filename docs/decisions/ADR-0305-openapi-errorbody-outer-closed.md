# ADR-0305 — OpenAPI ErrorBody Outer Closed

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G286  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U159**

## 决策

七域 `ErrorBody` 外层补 `additionalProperties: false`（对齐 identity）。
`details` 仍保留 anyOf/$ref + residual object（intentional；≠ invent close）。
顺带修复 Admin OpenAPI inventory 双重 bind。ops **1.0.68**；inventory PHX-G286。
