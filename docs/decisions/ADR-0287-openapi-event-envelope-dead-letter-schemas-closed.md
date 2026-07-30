# ADR-0287 — OpenAPI Event Envelope/DeadLetter Schemas Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G268  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U141**

## 决策

EventEnvelope + DeadLetterEntry → `additionalProperties: false`；payload 仍 free-form。
event bump；ops **1.0.59**；inventory PHX-G268。
