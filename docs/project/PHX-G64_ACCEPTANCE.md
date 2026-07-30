# PHX-G64 OIDC Refresh Token Field Encryption Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** `EAOS_OIDC_REFRESH_ENCRYPT` 可切换；缺密钥 fail-closed；默认 off；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0083 + Architecture Gate |
| B | Fernet seal/open + store 接线 |
| C | status `refresh_encrypt` |
| D | 契约 `test_api_gateway_g64_*` |

## 2. 核心不变量

- 默认 `off`；启用需 `EAOS_OIDC_REFRESH_FERNET_KEY`  
- 密文前缀 `eaos1:`；API 不回传 refresh/id_token  
- 无 Alembic 变更；复用 `0026`  
- memory 与 sql 均加密  

## 3. 自动化证据

- 本地完整回归：`536 passed`（`tests/contracts`）  
- Alembic head：仍为 `0026_oidc_refresh_bindings_g63`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0083 |
| Constitution Review | 通过；Gateway/Persistence 边界 |
| Cross-reference Review | 通过；G61/G63 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0026` |
| Gap Analysis | 密钥轮换见 G65；KMS/支付清算/组织联邦 UI 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 密钥轮换与外部 KMS  
- 组织级联邦 UI / 网格 CRD / 多区域  

## 6. 证据索引

- [PHX-G64 Architecture Gate](PHX-G64_ARCHITECTURE_GATE.md)
- [ADR-0083](../decisions/ADR-0083-oidc-refresh-encrypt.md)
