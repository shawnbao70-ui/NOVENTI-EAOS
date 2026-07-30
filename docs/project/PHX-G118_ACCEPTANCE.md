# PHX-G118 AI Tools / Memory Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / AI Runtime  
**退出门禁：** Terminal AI tools/memory 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓；approval/commit 另批  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0137 + Architecture Gate |
| B | Terminal Register/Invoke tool + Write/Read memory |
| C | 契约 `test_api_gateway_g118_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- Invoke/Memory 仍要求 AI subject（trusted header）  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`724 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0137 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G29/G117 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | AI approval/commit、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- AI approvals / commits Terminal 薄探针（见 G119）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G118 Architecture Gate](PHX-G118_ARCHITECTURE_GATE.md)
- [ADR-0137](../decisions/ADR-0137-ai-tools-memory-probe.md)
- [test_api_gateway_g118_ai_tools_memory.py](../../tests/contracts/test_api_gateway_g118_ai_tools_memory.py)
