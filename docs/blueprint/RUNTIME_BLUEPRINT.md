# 运行时蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-RUNTIME  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS 运行时蓝图

## 目的

定义 Kernel 服务、业务包、AI 智能体与事件处理器如何在企业级规模下安全、可观测地执行。

## 范围

**范围内：** 运行时生命周期、租户/包隔离模型、执行上下文（身份、租户、关联 ID）、可观测性与失败边界。  
**范围外：** 依赖安装、FastAPI 路由实现、业务包逻辑。

## 当前状态

**PHX-005 Foundation 切片已实现**

## 未来扩展

启动/关闭序列、上下文传播规则、调度与作业模型、健康/指标/追踪契约、包与 AI 工具沙箱规则。

---

## 运行时原则

1. Kernel 提供不变量；Runtime 在执行时强制执行  
2. 每次执行携带租户、身份与关联上下文  
3. 包不得绕过 Kernel 权限检查  
4. AI 动作经 Runtime 执行并具备审计能力  
5. 授权与租户隔离错误采取失败关闭（fail closed）

## 执行上下文（概念）

| 字段 | 含义 |
|------|------|
| tenant_id | 租户边界 |
| subject_id | 人类或数字主体 |
| correlation_id | 跨调用/事件关联 |
| package_id | 可选：发起包 |
| capability_scope | 有效权限范围摘要（Foundation 延后；Permission Kernel 仍为真相源） |

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [KERNEL_BLUEPRINT.md](KERNEL_BLUEPRINT.md)
- [EVENT_BLUEPRINT.md](EVENT_BLUEPRINT.md)
- [AI_BLUEPRINT.md](AI_BLUEPRINT.md)
- [PACKAGE_BLUEPRINT.md](PACKAGE_BLUEPRINT.md)
- [../standards/CODING_STANDARD.md](../standards/CODING_STANDARD.md)
