# PHX-G65 OIDC Refresh Fernet Key Rotation Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**退出门禁：** 主密钥加密 + 旧密钥解密窗口；status 暴露 key_count；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0084 + Architecture Gate |
| B | MultiFernet 主/旧密钥环 |
| C | status `refresh_encrypt_key_count` |
| D | 契约 `test_api_gateway_g65_*` |

## 2. 核心不变量

- 写入仅用 `EAOS_OIDC_REFRESH_FERNET_KEY`  
- `EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS` 仅解密  
- 永不回传密钥材料；无效密钥 fail-closed  
- 无 Alembic 变更  

## 3. 自动化证据

- 本地完整回归：`540 passed`（`tests/contracts`）  
- Alembic head：仍为 `0026_oidc_refresh_bindings_g63`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0084 |
| Constitution Review | 通过；Gateway 边界 |
| Cross-reference Review | 通过；G64 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0026` |
| Gap Analysis | 读时重加密/KMS、支付清算、组织联邦 UI 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 读时重加密 / 外部 KMS  
- 组织级联邦 UI / 网格 CRD / 多区域  

## 6. 证据索引

- [PHX-G65 Architecture Gate](PHX-G65_ARCHITECTURE_GATE.md)
- [ADR-0084](../decisions/ADR-0084-oidc-refresh-key-rotation.md)
