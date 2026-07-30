# PHX-G62 Platform IdP Registry Terminal Ops Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Platform API Gateway  
**退出门禁：** Admin 薄操作复用平台 IdP API；platform 上下文；无组织联邦引擎；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0081 + Architecture Gate |
| B | Terminal Admin List/Register/Disable/Discovery sync |
| C | platform 受信头（无 tenant） |
| D | 契约 `test_terminal_g62_*` |

## 2. 核心不变量

- 仅平台面 API；无租户面 IdP CRUD  
- body 禁止 `tenant_id` / `platform_scope`  
- UI 不展示完整 JWKS / secret  
- 无新 Alembic  

## 3. 自动化证据

- 本地完整回归：`529 passed`（`tests/contracts`）  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0081 |
| Constitution Review | 通过；BOOK23 薄壳 |
| Cross-reference Review | 通过；G55/G56/G60 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0` |
| Gap Analysis | 组织联邦 UI、支付清算、网格 CRD 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 组织级联邦策略 UI / social login  
- Refresh SQL 持久化  
- 多区域 / 网格 CRD  

## 6. 证据索引

- [PHX-G62 Architecture Gate](PHX-G62_ARCHITECTURE_GATE.md)
- [ADR-0081](../decisions/ADR-0081-platform-idp-registry-terminal-ops.md)
