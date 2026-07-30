# PHX-G41 Terminal Extension SQL Persistence Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Persistence  
**退出门禁：** SQL 持久化 register→activate→list→invoke→revoke；乐观锁；Alembic `0024`

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0059 + Architecture Gate |
| B | Alembic `0024` + `TerminalExtensionRecord` |
| C | SQLAlchemy 仓储四方法 + Transactional 转发 |
| D | 契约测试 + head 断言 |
| E | 七步自审 |

## 2. 核心不变量

- 无任意扩展脚本执行  
- Body 不可提升  
- SQL 模式不双写内存  
- 沙箱禁止能力规则不变  

## 3. 自动化证据

- 本地完整回归：`425 passed`（`tests/contracts`）  
- Alembic head：`0024_terminal_extension_sql_g41`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0059 |
| Constitution Review | 通过；Smart Terminal 边界 |
| Cross-reference Review | 通过；G39 内存路径仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；head/manifest/COMPAT 对齐 |
| Gap Analysis | iframe/Worker、热加载、签名密码学延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- iframe / Worker JS 运行时与 CSP  
- Marketplace 签名密码学校验  
- 跨进程热加载  

## 6. 证据索引

- [PHX-G41 Architecture Gate](PHX-G41_ARCHITECTURE_GATE.md)
- [ADR-0059](../decisions/ADR-0059-terminal-extension-sql.md)
