# Commercial Domain Event Catalog



**文档 ID：** EVT-COMMERCIAL-001  

**版本：** 1.1  

**里程碑：** PHX-G380 / PHX-G384 / PHX-G385  

**命名：** ADR-0006 `domain.entity.action`（ADR-0406 / ADR-0409 边界）



## Ownership



CRM / Inventory Package 产生商业事实；Shared Event Capability 负责持久化、outbox、投递、重试与 DLQ。本切片不在 Core Kernel 内复制 Event Bus，也不静默写入 Brain。



## Event Names



| Event | 触发事实 |

|-------|----------|

| `crm.sales_order.confirmed` | `confirm_sales_order` 状态转换成功（非幂等重放） |

| `inventory.delivery_order.shipped` | `ship_delivery_order` 发运过账成功（非幂等重放） |

| `crm.quote.converted` | `convert_quote` 创建转换指令成功（非幂等重放） |

| `crm.delivery_order.released` | `release_delivery_order` 放行成功（非幂等重放） |



## Required Envelope



使用 ADR-0006 immutable event envelope，并至少包含：



- `event_id`, `event_name`, `schema_version`

- `tenant_id`, `correlation_id`

- `producer`（`crm.package` / `inventory.package`）

- payload 资源引用：`sales_order_id` / `delivery_order_id` / `quote_id` /

  `conversion_id` 与 `tenant_id`



不得在 payload 中放置凭证、秘密、完整行项目或跨租户标识细节。事件与审计并存，不替代 Permission / Workflow。



## Delivery Gate



商业目录事件接到同事务 outbox（TransactionalCRMService / TransactionalInventoryService）；投递可靠性仍依赖 worker `dispatch_due`，不等同于同步 publish。

