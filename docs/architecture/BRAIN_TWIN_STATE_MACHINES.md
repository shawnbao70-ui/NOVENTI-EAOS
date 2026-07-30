# Enterprise Brain & Digital Twin 状态机

**文档 ID：** SM-BRAIN-001  
**版本：** 1.0  
**阶段：** PHX-E15

## Twin Snapshot

```text
active ──upsert(同 entity_ref)──► superseded
active ──archive────────────────► archived
```

## Brain Insight

Insight 无执行状态机。生命周期仅为已发布 advisory 记录：

```text
published (advisory=true, immutable authority)
```

`request_execution` 不产生状态迁移，恒失败关闭。
