# Runtime Foundation 契约测试计划

**文档 ID：** QA-RUNTIME-CONTRACT-001  
**阶段：** PHX-005  
**状态：** 已批准，待自动化

## 用例

| ID | 场景 | 期望 |
|----|------|------|
| R-01 | 租户数据面入站缺 tenant | `CTX_MISSING_TENANT` |
| R-02 | 平台治理入站无 tenant | 显式 platform scope 时允许 |
| R-03 | 传播更换 correlation / tenant / subject | `RT_PROPAGATION_VIOLATION` |
| R-04 | 传播补充 trace/package/locale/approval | 成功且安全字段不变 |
| R-05 | snapshot → JSON → restore | 全字段等价、UTC 保持 |
| R-06 | 未知快照版本或非法字段 | `RT_SNAPSHOT_INVALID` |
| R-07 | execute 接收非法上下文 | operation 零执行 |
| R-08 | execute 接收合法上下文 | operation 仅执行一次并收到原 ctx |
| R-09 | observability binding | 仅包含允许字段 |
| R-10 | Runtime → Permission Kernel 探针 | correlation/tenant/subject 原样贯通 |
| R-11 | Runtime → Identity SessionValidator | 无效/缺失校验器时 operation 零执行并返回 `CTX_INVALID` |

## 强制负面约束

- 不允许传播时提升平台作用域
- 不允许更换安全主体或租户
- 不允许 snapshot 接受额外未知字段
- 不允许 observability binding 输出 payload、credential 或 secret

## 完成定义

1. R-01～R-10 自动化通过
2. 相关 PHX-004 回归全部通过
3. Runtime 不依赖 FastAPI、AI、业务包或 Legacy
4. README、状态、任务与 CHANGELOG 同步

## 关联

- [RUNTIME_INTERFACE.md](RUNTIME_INTERFACE.md)
- [EXECUTION_CONTEXT.md](EXECUTION_CONTEXT.md)
- [../project/PHX-005_ACCEPTANCE.md](../project/PHX-005_ACCEPTANCE.md)
