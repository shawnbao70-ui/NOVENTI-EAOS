# PHX-G127 Platform Tenant Lifecycle Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Platform Organization  
**退出门禁：** Terminal platform tenant lifecycle 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0146 + Architecture Gate |
| B | Terminal Create / Suspend / Reactivate platform tenant |
| C | 契约 `test_api_gateway_g127_*` |

## 2. 核心不变量

- 平台面不下发 Tenant 头；禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`742 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0146 |
| Constitution Review | 通过；Gateway 薄适配；platform 上下文 |
| Cross-reference Review | 通过；G25/G126 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | permission write 见 G128；支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Permission policy/grant 手工写入 Terminal 探针（见 G128；≠ Role→grant 自动写入）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G127 Architecture Gate](PHX-G127_ARCHITECTURE_GATE.md)
- [ADR-0146](../decisions/ADR-0146-platform-tenant-lifecycle-probe.md)
- [test_api_gateway_g127_platform_tenant_lifecycle.py](../../tests/contracts/test_api_gateway_g127_platform_tenant_lifecycle.py)
