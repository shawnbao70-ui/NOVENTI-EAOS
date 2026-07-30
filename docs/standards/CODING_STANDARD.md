# 编码标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS 编码标准

## 目的

为未来 EAOS 实现定义统一编码规则，确保可维护性、可测试性与架构一致性。

## 范围

Python 风格意图、目录职责、导入、分层、文档、类型、错误与日志。本阶段不产生生产代码。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

与具体 linter/formatter 配置、CI 门禁对齐（实现期）。

---

## Python Style

- 遵循可读性优先；公开 API 保持清晰命名  
- 模块保持小而聚焦；避免“上帝模块”  
- 禁止在实现期把遗留 ERP 代码风格与目录习惯带入本仓库  

## Folder Organization

- 顶层布局服从 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)  
- 业务包逻辑位于 `packages/`，不得写入 `kernel/`  
- 路由/API 入口位于 `api/`，不得承载业务规则  

## Maximum File Responsibility

- 单文件单一主要职责  
- 超过合理复杂度时应拆分为模块，而非继续堆叠  

## Import Rules

- 依赖方向：`api/ui` → `services` → `repositories/models` → Kernel/Platform  
- 禁止业务包反向依赖未公开的 Kernel 内部实现  
- 禁止从遗留仓库导入代码  

## Dependency Rules

- 新增第三方依赖需说明用途与风险，并记录于决策或变更说明  
- Kernel 依赖面保持最小  

## Service Layer

- 编排用例与事务边界  
- 调用 Repository / Kernel 能力  
- 不直接处理传输层细节（HTTP 细节留在 API 层）  

## Repository Layer

- 封装持久化访问  
- 不包含业务流程决策  
- 查询与写入接口稳定、可测试  

## No Business Logic inside Routes

- 路由仅负责：校验输入形态、调用服务、映射响应  
- 业务规则、权限决策、工作流推进不得写在路由内  

## Single Responsibility Principle

- 每个模块/类/函数只做一件事  
- 交叉切割关注点下沉到平台能力  

## Documentation Requirement

- 公共接口必须有文档说明（用途、前置条件、错误）  
- 架构级变更同步蓝图/ADR  

## Type Hint Requirement

- 公共函数与跨边界 API 必须具备类型标注  
- 禁止用无类型 `Any` 掩盖边界契约（确有需要须注释理由）  

## Error Handling Standard

- 领域错误与基础设施错误分层  
- 对外错误响应遵循 [API_STANDARD.md](API_STANDARD.md)  
- 禁止吞异常；失败路径必须可观测  

## Logging Standard

- 结构化日志优先  
- 必含：correlation_id、tenant_id（如可得）、subject 摘要  
- 禁止记录密钥、令牌、敏感个人信息明文  

## 关联文档

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [NAMING_STANDARD.md](NAMING_STANDARD.md)
- [../architecture/SYSTEM_PRINCIPLES.md](../architecture/SYSTEM_PRINCIPLES.md)
