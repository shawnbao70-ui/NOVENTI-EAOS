# 事件标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS 事件标准

## 目的

规范事件命名、发布/订阅职责、载荷、关联 ID、时间戳、租户与重放规则。

## 范围

标准文档。本阶段不实现消息中间件。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

投递保证、死信、schema 注册中心。

---

## Event Naming

- `domain.entity.action`  
- 只描述已发生事实，不描述命令意图（命令走 API/工作流）  

## Publisher

- 对事件事实负责  
- 必须填充租户、时间戳、关联 ID、schema_version  
- 不得发布越权可见的跨租户数据  

## Subscriber

- 必须幂等  
- 失败可重试；副作用需防重  
- 不得假设严格全局顺序（除非契约声明）  

## Event Payload

- 最小必要字段  
- 敏感字段脱敏或引用化  
- 包含 schema_version  

## Correlation ID

- 全链路必传  
- 用于日志、审计与跨事件追踪  

## Timestamp

- UTC，RFC3339 兼容表达（实现期锁定）  

## Tenant ID

- 必填  
- 订阅处理必须校验租户上下文一致  

## Replay Rule

- 重放必须显式授权与审计  
- 重放不得破坏幂等假设  
- 生产重放需可追溯操作者  

## 关联文档

- [../blueprint/EVENT_BLUEPRINT.md](../blueprint/EVENT_BLUEPRINT.md)
- [NAMING_STANDARD.md](NAMING_STANDARD.md)
- [API_STANDARD.md](API_STANDARD.md)
