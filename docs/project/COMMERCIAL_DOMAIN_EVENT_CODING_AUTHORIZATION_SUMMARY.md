# Coding Authorization Summary — Commercial Domain-Event Honesty (G380)

## Milestone

**PHX-G380** — emit domain events for **SO.confirm** and **DO.ship** only.

## Alembic

**none** if outbox tables already exist; otherwise next free revision and document.

## Authorized

1. On successful `confirm_sales_order`: enqueue fact e.g. `crm.sales_order.confirmed`
   via DomainEventEmitter (same UoW pattern as Knowledge).
2. On successful `ship_delivery_order`: enqueue `inventory.delivery_order.shipped`.
3. Wire emitter in TransactionalCRMService / TransactionalInventoryService.
4. Update event catalog / WIRED list tests; gateway contracts can assert emit via
   in-memory/outbox spy or service-level unit as house style allows.
5. No other commercial commands; no silent Brain writes.

## Out

Baseline (G381), Marketplace PSP, host installs.

## Product Owner response

**Approve — batch; auto-continue G381.**
