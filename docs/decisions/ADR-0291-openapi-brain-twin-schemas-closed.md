# ADR-0291 — OpenAPI Brain/Twin Outer Schemas Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G272  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U145**

## 决策

UpsertTwinSnapshot/PublishInsight Request + TwinSnapshot/BrainInsight →
`additionalProperties: false`；`state` 仍 free-form。**不**打开 Twin authorize / Brain execute。
brain bump；ops **1.0.61**；inventory PHX-G272。
