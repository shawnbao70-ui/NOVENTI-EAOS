# ADR-0210 — OpenAPI Brain/Twin/AI/Workflow Status Body Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G191  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U064**；PO cue「充分授权…自主开发…加快」

## 背景

Auth status 已逐层对齐到 G190，但 Brain/Twin/AI/Workflow status 仍为宽松
`additionalProperties`，无法契约核对 fail-closed 围栏字段。

## 决策

1. Brain OpenAPI **1.0.4**：拆分 `TwinStatusData` / `BrainStatusData`
   （`authorize_execution` / `execute_execution` / `advisory_required` const）。  
2. AI OpenAPI **1.0.4**：`FoundationStatusData` emitted field parity
   （`ai_subject_required` / `commit_requires_approval`）。  
3. Workflow OpenAPI **1.0.5**：`FoundationStatusData` emitted field parity
   （`approval_source_of_truth=workflow_kernel`）。  
4. Inventory：`milestone=PHX-G191`；
   `t0188_status=mount_parity_complete_brain_twin_ai_workflow_status_body_field_parity`。  
5. Ops OpenAPI **1.0.18** 同步 inventory const。  
6. **不打开** Brain execute / Twin authorize；`full_openapi_http_complete=false`。  
7. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- Brain execute / Twin authorize invent  
- Full OpenAPI semantic parity  
- Identity/Org/Knowledge status deepen（后置）  

## 关联

- [../project/PHX-G191_ARCHITECTURE_GATE.md](../project/PHX-G191_ARCHITECTURE_GATE.md)  
