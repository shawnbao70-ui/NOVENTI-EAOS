# PHX-G101 Marketplace Status + Listing Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Marketplace / Smart Terminal  
**退出门禁：** `/v1/marketplace/status` + Terminal listing Create/Get；支付清算仍 fail-closed；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0120 + Architecture Gate |
| B | `GET /v1/marketplace/status` 脱敏姿态 |
| C | Terminal Create/Get listing |
| D | 契约 `test_api_gateway_g101_*` |

## 2. 核心不变量

- payment_clearing / external_arbitration / metering = fail_closed  
- 不实现支付清算或仲裁  
- listing 薄操作不提升 body 上下文；不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`690 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0120 |
| Constitution Review | 通过；支付仍 fail-closed |
| Cross-reference Review | 通过；G34/M17 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 支付清算、WebAuthn 产品页、Role→grant 自动写另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G101 Architecture Gate](PHX-G101_ARCHITECTURE_GATE.md)
- [ADR-0120](../decisions/ADR-0120-marketplace-status-listing-probe.md)
- [test_api_gateway_g101_marketplace_status.py](../../tests/contracts/test_api_gateway_g101_marketplace_status.py)
