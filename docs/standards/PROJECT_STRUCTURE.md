# 项目结构标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

正式 EAOS 项目结构

## 目的

规定 `NOVENTI-EAOS` 的权威目录布局与放置规则。

## 范围

仓库结构治理。

## 当前状态

**已就绪并已应用 — PHX-000 / PHX-003**

## 未来扩展

实现期子目录细则（services/repositories/models 落位规则）。

---

## 官方顶层结构

```text
NOVENTI-EAOS/
  docs/
    constitution/
    blueprint/
    standards/
    architecture/
    decisions/
    project/
  kernel/
  platform/
  runtime/
  packages/
  api/
  sdk/
  ui/
  tests/
  tools/
  scripts/
```

## 目录职责

| 目录 | 职责 |
|------|------|
| `docs/` | 宪法、蓝图、标准、架构、决策、项目治理 |
| `kernel/` | 内核不变量与内核域 |
| `platform/` | 共享平台能力 |
| `runtime/` | 执行、隔离、可观测性 |
| `packages/` | 行业/业务/AI/集成包 |
| `api/` | API 面 |
| `sdk/` | 客户端与扩展 SDK |
| `ui/` | 操作界面 |
| `tests/` | 测试 |
| `tools/` | 开发与平台工具 |
| `scripts/` | 自动化脚本 |

## 实现期逻辑分层（未来）

在不破坏顶层布局前提下，代码组织可增加：

- `services/` — 应用服务  
- `repositories/` — 持久化  
- `models/` — 领域/数据模型  

具体落位目录将在 Kernel Foundation 前以 ADR 确认。

## 禁止事项

- 在遗留仓库创建 EAOS 结构  
- 将遗留目录结构复制为本仓库规范  
- 在 `kernel/` 放置业务包逻辑  

## 关联文档

- [CODING_STANDARD.md](CODING_STANDARD.md)
- [GIT_WORKFLOW.md](GIT_WORKFLOW.md)
- [../project/DIRECTORY_TREE.md](../project/DIRECTORY_TREE.md)
