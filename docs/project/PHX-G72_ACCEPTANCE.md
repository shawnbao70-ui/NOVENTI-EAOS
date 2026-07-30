# PHX-G72 Service Mesh Traffic CRD Foundation Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform Release / Operations  
**退出门禁：** opt-in Istio VS+DR；默认关；不装控制面；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0091 + Architecture Gate |
| B | VirtualService + DestinationRule 模板 |
| C | MESH/HELM/Runbook |
| D | 契约 `test_ops_g72_*` |

## 2. 核心不变量

- `mesh.traffic.enabled` 默认 false；需 `mesh.enabled`  
- vendor 仅 `istio`；DR TLS 默认 `ISTIO_MUTUAL`  
- 无 AuthorizationPolicy / 权重分流  

## 3. 自动化证据

- 本地完整回归：`568 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0091 |
| Constitution Review | 通过；Ops 边界 |
| Cross-reference Review | 通过；G71 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | Authz 见 G73；权重分流/KMS、支付清算、多区域另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- AuthorizationPolicy / Istio Gateway / 权重分流  
- 外部 KMS / 多区域  

## 6. 证据索引

- [PHX-G72 Architecture Gate](PHX-G72_ARCHITECTURE_GATE.md)
- [ADR-0091](../decisions/ADR-0091-mesh-traffic-crd-foundation.md)
- [MESH.md](../release/MESH.md)
