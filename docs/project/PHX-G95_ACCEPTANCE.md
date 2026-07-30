# PHX-G95 Terminal Effective Permissions Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**退出门禁：** Terminal effective-permissions 只读探针；包版本仍 `0.2.0`；Alembic 仍 `0029`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0114 + Architecture Gate |
| B | Terminal Admin List effective permissions |
| C | 契约 `test_api_gateway_g95_*` |

## 2. 核心不变量

- 仅调用既有 effective-permissions  
- path principal 独立输入；禁止 body 提升  
- 鉴权沿用 self-or-auditor；不写 grant；不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`677 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0114 |
| Constitution Review | 通过；无 body 提升 |
| Cross-reference Review | 通过；G22/G94 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 自动写 grant、WebAuthn 产品页、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G95 Architecture Gate](PHX-G95_ARCHITECTURE_GATE.md)
- [ADR-0114](../decisions/ADR-0114-terminal-effective-permissions.md)
- [test_api_gateway_g95_terminal_effective_permissions.py](../../tests/contracts/test_api_gateway_g95_terminal_effective_permissions.py)
