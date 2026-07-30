# PHX-G172 Marketplace Listing Host Acquire Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Marketplace / Smart Terminal Extension Host  
**退出门禁：** allowlisted host-acquire；无任意脚本；≠ package install；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U045**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0191 + Architecture Gate |
| B | `host_acquire.py` + marketplace route + OpenAPI 1.2.2 |
| C | Demo published listing + bootstrap fields |
| D | Terminal Acquire → Host CTA |
| E | tip/status/Manifest/DAL-U045 + `test_api_gateway_g172_*` |

## 2. 核心不变量

- Allowlist fail-closed  
- 不执行 Marketplace 任意脚本  
- acquire ≠ purchase / ≠ package install  
- 不打开 HARD HOLDS  

## 3. 自动化证据

- `tests/contracts/test_api_gateway_g172_marketplace_host_acquire.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0191 |
| Constitution Review | 通过；无 BOOK 编辑 |
| Cross-reference Review | 通过；DAL-U045 |
| Documentation Review | 通过 |
| Consistency Review | 通过；`0.2.1` / `0029` |
| Gap Analysis | 非 allowlist catalog；listing↔ext crypto bind；package auto-install 仍 defer |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Non-allowlist Marketplace catalog → host  
- Package install auto-wire  
- External PSP / attestation crypto / Brain / Twin  

## 6. 证据索引

- [PHX-G172 Architecture Gate](PHX-G172_ARCHITECTURE_GATE.md)  
- [ADR-0191](../decisions/ADR-0191-marketplace-listing-host-acquire.md)  
- [host_acquire.py](../../api/gateway/host_acquire.py)  
