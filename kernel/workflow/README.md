# kernel/workflow/

Workflow Kernel 模块边界。

## 职责

流程定义/实例、审批、信号、升级、取消、补偿；支撑 AI 人工审批双闸门。

## 状态

PHX-K09 已完成并验收：

- Definition 版本与 Deprecate
- Approve / Reject / Escalate / Cancel
- Signal 幂等（complete / compensation_complete）
- 批准绑定：principal + action + resource + 可选 plan/scope/expiry
- Task `due_at` SLA fail-closed
- Instance/Task `expected_version`
- Compensate 最小状态机
- SQLAlchemy + Alembic `0013_workflow_k09`
- OpenAPI 3.1、状态机与事件目录

## 测试

```bash
python -m pytest tests/contracts/test_workflow_service.py tests/contracts/test_workflow_k09.py tests/contracts/test_workflow_openapi.py -p no:cacheprovider
```

## 规格

- [../../docs/architecture/WORKFLOW_INTERFACE.md](../../docs/architecture/WORKFLOW_INTERFACE.md)
- [../../docs/architecture/WORKFLOW_STATE_MACHINES.md](../../docs/architecture/WORKFLOW_STATE_MACHINES.md)
- [../../docs/api/workflow.openapi.yaml](../../docs/api/workflow.openapi.yaml)
- [../../docs/decisions/ADR-0024-workflow-approval-truth.md](../../docs/decisions/ADR-0024-workflow-approval-truth.md)
