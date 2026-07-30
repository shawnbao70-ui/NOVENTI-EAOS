# PHX-G168 Demo Signed Extension Seed Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Demo Gateway / Smart Terminal Extensions  
**封口门禁：** demo HMAC seed + activate；bootstrap 无 secret；生产未挂载；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U041**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0187 + Architecture Gate |
| B | Demo `ExtensionSigningSettings(hmac)` + `_seed_signed_extension` |
| C | Bootstrap optional extension fields；Terminal autofill |
| D | tip/status/Manifest/DAL-U041 |
| E | `test_api_gateway_g168_*` |

## 2. 核心不变量

- 生产 `api.gateway.app` 不挂载 `/v1/demo/*`，不嵌入 demo HMAC  
- Bootstrap / UI 不含 HMAC secret / token  
- 不打开 HARD HOLDS；不执行 Marketplace 任意脚本  

## 3. 自动化证据

- `tests/contracts/test_api_gateway_g168_demo_signed_extension.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0187 |
| Constitution Review | 通过；dev-only；无 BOOK 编辑 |
| Cross-reference Review | 通过；DAL-U041 |
| Documentation Review | 通过 |
| Consistency Review | 通过；`0.2.1` / `0029` |
| Gap Analysis | Signed host productization → **PHX-G169** |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace listing acquire → host install（见 G169 Explicit Defer）  
- Production demo surface（永不）  
- Attestation crypto / Brain execute / Twin authorize  

## 6. 证据索引

- [PHX-G168 Architecture Gate](PHX-G168_ARCHITECTURE_GATE.md)  
- [ADR-0187](../decisions/ADR-0187-demo-signed-extension-seed.md)  
- [demo.py](../../api/gateway/demo.py)  
- [demo_bootstrap.py](../../api/gateway/routers/demo_bootstrap.py)  
