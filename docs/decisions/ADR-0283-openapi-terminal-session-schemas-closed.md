# ADR-0283 — OpenAPI Terminal Session Schemas Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G264  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U137**

## 决策

OpenSession/ComposeIntent/BuildPreview/RequestApproval/RegisterExtension/
InvokeExtension Request + Session/Intent/PlanPreview/ApprovalPresentation/
CommitReceipt → `additionalProperties: false`；live keys only。
terminal patch bump；ops **1.0.57**；inventory PHX-G264。
