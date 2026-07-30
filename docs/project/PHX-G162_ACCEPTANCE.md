# PHX-G162 Marketplace Payment Clearing Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Marketplace / Smart Terminal  
**退出门禁：** Eng `4` opened；default 503；env ON = internal record only；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G007 + DAL-G003 + DAL-G004；Usage **DAL-U035**；cue「继续Eng 4 支付清算」

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0181 + Architecture Gate |
| B | `payment_clearing.py` + marketplace router + `record_internal_payment_clearing` |
| C | marketplace OpenAPI **1.2.0**；status posture；inventory fence；Terminal thin |
| D | PROJECT_STATUS / CHANGELOG / TASKS / ENG tip / Manifest G162 / DAL-G007/U035 |
| E | `test_api_gateway_g162_*` + soften G101/G141/Held contracts |

## 2. 核心不变量

- Default：`POST …/payment-clearing` → 503 `GATEWAY_PAYMENT_CLEARING_DISABLED`  
- Env ON：internal clearing only；`external_psp=false`；绑定 issued invoice  
- External PSP / metering / external arbitration 仍 fail-closed  
- 不打开 Brain execute / Twin authorize / Cap→grant invent  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`  
- 不回归并行 G160 WebAuthn / G161 Role→grant / G163 Research intake  

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g162_payment_clearing.py`  
- 回归：`test_api_gateway_g101_*` · `test_api_gateway_g141_*` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0181 |
| Constitution Review | 通过；fail-closed default；无 BOOK 编辑 |
| Cross-reference Review | 通过；G101/G141 软化；DAL-G007/U035 |
| Documentation Review | 通过；OpenAPI 1.2.0 + tip |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | External PSP / arbitration / metering 另批；Brain/Twin 关闭 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- External PSP capture / refund  
- Subscription metering / external arbitration  
- Brain execute / Twin authorize  
- 新 Alembic  

## 6. 证据索引

- [PHX-G162 Architecture Gate](PHX-G162_ARCHITECTURE_GATE.md)  
- [ADR-0181](../decisions/ADR-0181-marketplace-payment-clearing.md)  
- [marketplace.openapi.yaml](../api/marketplace.openapi.yaml)  
- [test_api_gateway_g162_payment_clearing.py](../../tests/contracts/test_api_gateway_g162_payment_clearing.py)  
