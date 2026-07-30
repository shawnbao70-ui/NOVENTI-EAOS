# PHX-G43 Terminal Extension Worker Runtime Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**退出门禁：** 首方 Worker + 共享桥接；无 schema 变更

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0061 + Architecture Gate |
| B | `extension_runtime` Worker channel 策略 |
| C | demo-worker + UI 启停 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 仅首方 Worker；无 Marketplace 任意脚本  
- Bridge 不可提升上下文  
- `executed` 仍为 false  
- 复用 G42 CSP 路径  

## 3. 自动化证据

- 本地完整回归：`431 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0061 |
| Constitution Review | 通过；BOOK23 沙箱边界 |
| Cross-reference Review | 通过；G42 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | CDN Worker / SharedWorker / 签名密码学延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace / CDN Worker 包  
- SharedWorker / ServiceWorker  
- Marketplace 签名密码学  

## 6. 证据索引

- [PHX-G43 Architecture Gate](PHX-G43_ARCHITECTURE_GATE.md)
- [ADR-0061](../decisions/ADR-0061-terminal-extension-worker.md)
