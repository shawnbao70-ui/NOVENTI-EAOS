# PHX-G42 Terminal Extension iframe + CSP Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**退出门禁：** 首方 iframe + CSP + postMessage 桥接；无 schema 变更

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0060 + Architecture Gate |
| B | `extension_runtime` 桥接/CSP 策略 |
| C | demo-panel + UI iframe 宿主 |
| D | Gateway CSP 中间件 |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- 不执行 Marketplace 任意上传脚本  
- Body / bridge 不可提升上下文  
- `executed` 仍为 false  
- 禁止能力集合不变  

## 3. 自动化证据

- 本地完整回归：`428 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024_terminal_extension_sql_g41`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0060 |
| Constitution Review | 通过；BOOK23 沙箱边界 |
| Cross-reference Review | 通过；G39/G41 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | Worker / CDN / 签名密码学延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Worker 运行时  
- CDN / 第三方包加载  
- Marketplace 签名密码学  

## 6. 证据索引

- [PHX-G42 Architecture Gate](PHX-G42_ARCHITECTURE_GATE.md)
- [ADR-0060](../decisions/ADR-0060-terminal-extension-iframe-csp.md)
