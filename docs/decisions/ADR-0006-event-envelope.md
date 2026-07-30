# ADR-0006 — 事件信封（Event Envelope）

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

EAOS 采用事件驱动集成。若无统一信封，将导致租户泄漏风险、无法关联审计、无法安全重放。

## 决策

所有平台事件必须使用统一概念信封，至少包含：

| 字段 | 要求 |
|------|------|
| `event_id` | 全局唯一 |
| `event_name` | `domain.entity.action` |
| `schema_version` | 必填 |
| `tenant_id` | 必填 |
| `correlation_id` | 必填 |
| `timestamp` | UTC 必填 |
| `producer` | 服务/包标识 |
| `payload` | 最小必要结构化数据 |

附加规则：

1. 事件不可变  
2. 重放必须显式授权并审计  
3. 订阅者必须幂等  
4. 禁止跨租户投递（除非未来经宪法级例外 + ADR）  

## 后果

- Event Bus 实现必须校验信封完整性  
- 不符合信封的事件不得进入总线  
- 详见 [../standards/EVENT_STANDARD.md](../standards/EVENT_STANDARD.md) 与 [../blueprint/EVENT_BLUEPRINT.md](../blueprint/EVENT_BLUEPRINT.md)
