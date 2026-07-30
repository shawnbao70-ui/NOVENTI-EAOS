# ADR-0059 — Terminal Extension SQL Persistence (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G41  
**归属：** Smart Terminal / Persistence

## 背景

ADR-0057 交付进程内 Extension Host；SQLAlchemy 仓储对扩展方法显式 deferred。Gateway/多进程部署需要租户级登记可持久化，且不得引入任意脚本运行时。

## 决策

1. 新增表 `kernel.terminal_extensions`（Alembic `0024`），字段对齐 `TerminalExtension`；JSON 列存 capabilities / actions / surfaces。  
2. 实现 `SQLAlchemySmartTerminalRepository` 的 `add/get/save/list_extension(s)`；乐观锁映射 `version` ↔ `version_num`。  
3. `TransactionalSmartTerminalService` 转发 register / activate / revoke / list / invoke。  
4. 默认 Gateway 仍可用内存仓储；SQL 模式替换而非双写。  
5. 业务规则仍在 `SmartTerminalService`；本切片不改沙箱策略。

## Explicit Defer

- Worker JS 运行时（Foundation iframe/CSP 见 ADR-0060 / PHX-G42）  
- Marketplace 签名密码学校验（Foundation 见 ADR-0062 / PHX-M18）  
- 跨进程热加载 / 扩展包分发  

## 关联

- [ADR-0057-terminal-extension-host.md](ADR-0057-terminal-extension-host.md)
- [../project/PHX-G41_ARCHITECTURE_GATE.md](../project/PHX-G41_ARCHITECTURE_GATE.md)
