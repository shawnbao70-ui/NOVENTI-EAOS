# PHX-G169 Signed Extension Host Productization Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal Extensions  
**退出门禁：** Hydrate signed path；无 Marketplace 任意脚本；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U042**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0188 + Architecture Gate |
| B | `hydrateSignedExtensionHost` + host status + Hydrate button |
| C | Boot/tab auto-hydrate after G168 bootstrap |
| D | tip/status/Manifest/DAL-U042 |
| E | `test_api_gateway_g169_*` |

## 2. 核心不变量

- 不执行 Marketplace 任意脚本  
- 不在 UI/bootstrap 暴露 HMAC secret  
- 不打开 HARD HOLDS  

## 3. 自动化证据

- `tests/contracts/test_api_gateway_g169_signed_extension_host.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0188 |
| Constitution Review | 通过；无 BOOK 编辑 |
| Cross-reference Review | 通过；DAL-U042 |
| Documentation Review | 通过 |
| Consistency Review | 通过；`0.2.1` / `0029` |
| Gap Analysis | Marketplace catalog→host acquire 仍 defer |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace listing acquire → terminal extension install  
- Attestation crypto / Brain execute / Twin authorize  

## 6. 证据索引

- [PHX-G169 Architecture Gate](PHX-G169_ARCHITECTURE_GATE.md)  
- [ADR-0188](../decisions/ADR-0188-signed-extension-host-productization.md)  
- [smart_terminal/ui/app.js](../../smart_terminal/ui/app.js)  
