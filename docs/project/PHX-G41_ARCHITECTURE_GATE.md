# PHX-G41 Terminal Extension SQL Persistence Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Persistence  
**规范源：** ADR-0059  

## 1. 门禁目标

将 G39 Extension Host 登记状态持久化到 PostgreSQL/SQLAlchemy，保持沙箱与无任意代码执行不变。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Smart Terminal；无业务真相 |
| Persistence | `kernel.terminal_extensions`；SQL 模式替换内存 |
| Runtime | 仍无 iframe/Worker 执行 |
| Gateway | 薄适配不变；注入 Transactional 即可 SQL |

## 3. Exit Criteria

1. ADR-0059 Accepted。  
2. 四仓储方法 + Transactional 转发可用。  
3. Alembic head `0024`；契约与 head 断言绿。  
4. iframe runtime / 热加载仍显式延后。
