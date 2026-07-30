# 事件蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-EVENT  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS 事件蓝图

## 目的

定义跨 Kernel、Runtime、AI 与 Packages 的事件驱动架构：发布、订阅、关联、重放与租户安全流。

## 范围

**范围内：** 事件分类与命名意图、发布者/订阅者职责、载荷治理、关联/时间戳/租户要求、重放策略边界。  
**范围外：** 具体消息中间件产品锁定、全部行业包业务事件目录、用同步 API 完全替代 Kernel 调用。

## 当前状态

**PHX-002 基线已建立；PHX-004 Foundation 切片已实现**  
完整生产级 Event Bus 仍归属 PHX-P11；其规范技术层是 Shared Platform Capability。现有 `kernel/event_bus/` 为 PHX-004 兼容路径，不改变所有权。

## 未来扩展

生产级持久化、投递保证、死信策略、跨包事件契约、AI/工作流集成模式与事件管线可观测性。

---

## 事件原则

1. 事件是一等集成织物  
2. 每条事件携带租户、时间戳与关联身份  
3. 订阅者设计意图为幂等  
4. 重放受控且可审计  
5. 事件副作用不得绕过权限边界  

## 概念信封字段

| 字段 | 要求 |
|------|------|
| event_name | 稳定、版本化命名 |
| tenant_id | 必填 |
| correlation_id | 必填 |
| timestamp | UTC，必填 |
| producer | 服务/包标识 |
| payload | 结构化、最小必要 |
| schema_version | 必填 |

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [RUNTIME_BLUEPRINT.md](RUNTIME_BLUEPRINT.md)
- [KERNEL_BLUEPRINT.md](KERNEL_BLUEPRINT.md)
- [PACKAGE_BLUEPRINT.md](PACKAGE_BLUEPRINT.md)
- [../standards/EVENT_STANDARD.md](../standards/EVENT_STANDARD.md)
