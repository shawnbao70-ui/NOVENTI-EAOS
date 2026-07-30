# Smart Terminal 状态机

**文档 ID：** SM-TERM-001  
**版本：** 1.0  
**阶段：** PHX-T13

## Terminal Session

```text
open ──close──► closed
```

## Intent

```text
draft ──build_preview──► previewed
draft ──cancel────────► cancelled
```

## Plan Preview

```text
active ──rebuild（同 intent 新 preview）──► invalidated
active ──commit─────────────────────────► committed
```

## Approval（真相源：Workflow）

Terminal 不维护平行审批状态机。`approval_ref` 指向 Workflow Instance；`PresentApproval` 映射 Workflow 当前状态。

## Commit

仅当 Preview=`active` 且（非高影响 或 Workflow 已批准且绑定匹配）时产生 `CommitReceipt`，并将 Preview 置为 `committed`。
