# PHX-G39 Terminal Extension Host Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation Host）  
**归属：** Smart Terminal  
**退出门禁：** 清单注册；签名激活；沙箱拒绝；无任意代码执行

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0057 + Architecture Gate |
| B | register / activate / revoke / list / invoke |
| C | Gateway `/v1/terminal/extensions*` + OpenAPI |
| D | UI Extensions 表面 |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- Extension 非业务真相源  
- 未签名不可激活  
- 禁止 hide_approval / elevate_context / bypass_audit / mutate_shell_controls / network.*  
- invoke 仅审计声明动作（`executed=false`）  

## 3. 自动化证据

- 本地完整回归：`421 passed`（`tests/contracts`）  
- 无 schema 变更；Alembic head 仍为 `0023_event_webhook_hmac_e22`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0057 |
| Constitution Review | 通过；BOOK23 |
| Cross-reference Review | 通过；G36 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | iframe/Worker runtime、SQL 持久化、Marketplace 验签显式延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- iframe / Worker JS 运行时与 CSP  
- Extension SQL 持久化  
- Marketplace 签名密码学校验  
- OIDC 登录页  

## 6. 证据索引

- [PHX-G39 Architecture Gate](PHX-G39_ARCHITECTURE_GATE.md)
- [ADR-0057](../decisions/ADR-0057-terminal-extension-host.md)
