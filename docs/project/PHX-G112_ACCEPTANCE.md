# PHX-G112 Knowledge Link / Provenance Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Knowledge  
**退出门禁：** Terminal link/provenance 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0131 + Architecture Gate |
| B | Terminal Create link / Get provenance |
| C | 契约 `test_api_gateway_g112_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：见验收时 `tests/contracts` 全绿计数  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0131 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G24/G111 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | Twin/Brain Terminal、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Twin authorize / Brain Terminal 薄探针（status/snapshot 见 G113）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G112 Architecture Gate](PHX-G112_ARCHITECTURE_GATE.md)
- [ADR-0131](../decisions/ADR-0131-knowledge-link-provenance-probe.md)
- [test_api_gateway_g112_knowledge_link_provenance.py](../../tests/contracts/test_api_gateway_g112_knowledge_link_provenance.py)
