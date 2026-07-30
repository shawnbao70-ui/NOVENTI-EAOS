# PHX-E15 Enterprise Brain & Twin Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted；实现已验收（见 PHX-E15_ACCEPTANCE）  
**归属：** Shared Platform Capability / Enterprise Brain · Digital Twin  
**规范源：** BOOK14、BOOK18、BOOK19、BOOK22、BOOK23、ADR-0021、ADR-0030  
**退出门禁：** 建议与执行权分离

## 1. 门禁目标

交付 Twin Snapshot 与 Brain Insight 最小垂直切片：provenance、置信度、偏差标注、租户隔离，并证明 Brain/Twin 无法授予或执行副作用。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Twin ownership | `eaos_platform.twin` |
| Brain ownership | `eaos_platform.brain` |
| Twin | 受治理映像；≠ 执行授权 |
| Brain | advisory insight/recommendation/simulation |
| Execution | 禁止；须 AI Runtime / Terminal / Workflow |
| Provenance | Twin 与 Insight 均强制 |
| Secrets | 状态/洞察 payload 禁止 |

## 3. Action / Resource Contract

- `twin_snapshot:write|read`
- `brain_insight:publish|read`

资源：

- `twin_snapshot:{id}`
- `brain_insight:{id}`

## 4. 实现切片

### Slice A — Twin

- UpsertTwinSnapshot / GetTwinSnapshot
- provenance + confidence + secret reject

### Slice B — Brain

- PublishInsight / GetInsight
- request_execution → 失败关闭

### Slice C — Persistence

- SQLAlchemy + Transactional facades + Alembic `0019`

### Slice D — Contracts

- OpenAPI / 状态机 / PostgreSQL / 七步自审

## 5. Exit Criteria

1. Twin/Brain 输出不授予执行权。  
2. 缺少 provenance 或非法置信度失败关闭。  
3. `request_execution` 恒为 `BRAIN_EXECUTION_FORBIDDEN`。  
4. 租户隔离与秘密拒绝。  
5. OpenAPI / Data Model / Migration / Code 一致。  
6. PostgreSQL 与完整回归通过。  
7. 不宣称连续同步管线或 LLM 推理产品化已交付。

## 6. Explicit Defer

- 向量/多模型推理产品化
- 连续孪生同步与遥测
- Terminal Brain UX、Marketplace 洞察包
- FastAPI Router
