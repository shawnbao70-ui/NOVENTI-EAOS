# API 蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-API  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS API 蓝图

## 目的

定义 EAOS 内外部 API 面的架构原则：稳定契约、版本化、权限贯通与一致性响应模型。

## 范围

**范围内：** API 分层意图、版本策略、认证授权边界、与 Kernel/Event 的关系。  
**范围外：** FastAPI/路由实现、具体资源清单的完整实现、数据库表创建。

## 当前状态

**基线已建立 — PHX-002**

## 未来扩展

公开/内部 API 目录、OpenAPI 规范位置、错误码体系与 API 标准对齐、包级 API 贡献模型。

---

## API 原则

1. API 是契约，不是业务规则宿主  
2. 所有 API 默认多租户与权限检查  
3. 破坏性变更必须版本化并经 ADR  
4. 写操作可审计；高影响操作可对接审批  
5. UI / SDK / 包均通过正式 API 面访问平台  

## API 分层（概念）

| 层 | 消费者 |
|----|--------|
| Public API | 外部集成、合作伙伴 |
| Platform API | UI、SDK、一等客户端 |
| Package API | 包间受控协作 |
| Internal API | Kernel/Runtime 内部（不对外承诺） |

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [KERNEL_BLUEPRINT.md](KERNEL_BLUEPRINT.md)
- [UI_BLUEPRINT.md](UI_BLUEPRINT.md)
- [PACKAGE_BLUEPRINT.md](PACKAGE_BLUEPRINT.md)
- [../standards/API_STANDARD.md](../standards/API_STANDARD.md)
