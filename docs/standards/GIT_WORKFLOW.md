# Git 工作流标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS Git 工作流

## 目的

规范分支策略、提交约定、发布标签、热修复与回滚规则。

## 范围

仅适用于 `NOVENTI-EAOS`。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

保护分支规则、必选 CI 检查清单。

---

## Branch Strategy

| 分支 | 用途 |
|------|------|
| `main` | 稳定主线 |
| `develop`（可选） | 集成线 |
| `feature/*` | 功能开发 |
| `fix/*` | 缺陷修复 |
| `hotfix/*` | 生产紧急修复 |
| `docs/*` | 纯文档变更（可选） |
| `phx/*` | Phoenix 里程碑工作（可选） |

- 禁止向遗留仓库推送 EAOS 开发  
- 大型架构变更经评审后合并  

## Commit Convention

推荐格式：

```text
<type>(<scope>): <summary>
```

常用 type：`docs` · `feat` · `fix` · `refactor` · `test` · `chore` · `adr`

- 摘要说明“为什么/意图”，而非堆砌文件列表  
- 文档里程碑可用：`docs(phx-003): ...`  

## Release Tags

- 形式：`vMAJOR.MINOR.PATCH`  
- 预发布：`vX.Y.Z-rc.N`  
- 标签必须对应可复现状态与 CHANGELOG 条目  

## Hotfix Rules

- 从发布标签拉出 `hotfix/*`  
- 仅含最小修复  
- 合并回主线并补回归说明  
- 热修复不得夹带重构  

## Rollback Rules

- 优先可逆发布（前向修复或回滚部署）  
- 数据迁移回滚必须有书面计划  
- 回滚操作记入 CHANGELOG 与 IMPLEMENTATION_LOG  

## 关联文档

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [../project/CHANGELOG.md](../project/CHANGELOG.md)
