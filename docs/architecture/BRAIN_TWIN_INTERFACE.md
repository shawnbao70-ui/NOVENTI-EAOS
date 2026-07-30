# Enterprise Brain & Digital Twin 接口规格

**文档 ID：** IF-BRAIN-001  
**版本：** 1.0  
**阶段：** PHX-E15  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

## 目的

细化 Twin Snapshot 与 Brain Insight 接口，确保「建议与执行权分离」。

## 不变式

1. Twin / Brain 落点 `eaos_platform.twin` / `eaos_platform.brain`  
2. Twin 与 Insight 强制 provenance 与置信度 ∈ [0,1]  
3. Insight 永久 `advisory=true`  
4. `authorize_from_twin` / `request_execution` 恒失败关闭  
5. 执行必须改走 AI Runtime / Terminal / Workflow + Permission  
6. 禁止秘密字段  

## 接口

| 接口 | HTTP | 权限要点 |
|------|------|----------|
| UpsertTwinSnapshot | `POST /twin/snapshots` | `twin_snapshot:write` |
| GetTwinSnapshot | `GET /twin/snapshots/{id}` | `twin_snapshot:read` |
| AuthorizeFromTwin | `POST .../authorize` | 恒 `TWIN_EXECUTION_FORBIDDEN` |
| PublishInsight | `POST /brain/insights` | `brain_insight:publish` |
| GetInsight | `GET /brain/insights/{id}` | `brain_insight:read` |
| RequestExecution | `POST .../execute` | 恒 `BRAIN_EXECUTION_FORBIDDEN` |

## 错误

`TWIN_*`、`BRAIN_*`（见 ERROR_CODES §12）

## 关联

- [BRAIN_TWIN_STATE_MACHINES.md](BRAIN_TWIN_STATE_MACHINES.md)
- [../api/brain.openapi.yaml](../api/brain.openapi.yaml)
- [../decisions/ADR-0030-enterprise-brain-twin-boundary.md](../decisions/ADR-0030-enterprise-brain-twin-boundary.md)
