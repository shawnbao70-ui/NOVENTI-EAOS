# PHX-G115 Brain Status / Insight Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Brain  
**退出门禁：** Terminal Brain status/insight 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓；execute 另批  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0134 + Architecture Gate |
| B | `GET /v1/brain/status` + Terminal status/publish/get |
| C | 契约 `test_api_gateway_g115_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- execute 执行路径仍 fail-closed（本里程碑不接线）  
- insight 仅 advisory  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`718 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0134 |
| Constitution Review | 通过；Gateway 薄适配；建议与执行权分离 |
| Cross-reference Review | 通过；G28/G114 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | Brain execute Terminal、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Brain execute Terminal 薄探针（见 G116；仍 fail-closed）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 打开 Brain execute 执行权  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G115 Architecture Gate](PHX-G115_ARCHITECTURE_GATE.md)
- [ADR-0134](../decisions/ADR-0134-brain-status-insight-probe.md)
- [test_api_gateway_g115_brain_probe.py](../../tests/contracts/test_api_gateway_g115_brain_probe.py)
