# ADR-0092 — Service Mesh AuthorizationPolicy Foundation

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G73  
**归属：** Platform Release / Operations boundary

## 背景

G71/G72 交付 mTLS PeerAuthentication 与 VS/DR。需最小 L7 授权声明：仅允许已认证 mesh 主体访问 Gateway。

## 决策

1. `mesh.authz.enabled`（默认 `false`）；启用时要求 `mesh.enabled=true`。  
2. Foundation 仅支持 `mesh.authz.vendor=istio`；渲染 `security.istio.io/v1beta1` `AuthorizationPolicy`：  
   - `action` 默认 `ALLOW`  
   - 默认规则：`from.source.principals=["*"]`（任一已认证 SPIFFE 主体）  
   - 可选 `paths`（默认 `["*"]`）限制 HTTP path  
3. **不**替代应用 JWT（`EAOS_REQUIRE_JWT`）；**不**安装控制面。  
4. 文档更新 `MESH.md`；契约断言；包版本仍 `0.2.0`。  
5. 细粒度租户/claim 规则、Linkerd、多区域、支付清算另批。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- JWT claim / 租户标签细粒度规则  
- Linkerd / 外部 KMS / 多区域  

## 关联

- [ADR-0090-mesh-policy-crd-foundation.md](ADR-0090-mesh-policy-crd-foundation.md)
- [ADR-0091-mesh-traffic-crd-foundation.md](ADR-0091-mesh-traffic-crd-foundation.md)
- [../project/PHX-G73_ARCHITECTURE_GATE.md](../project/PHX-G73_ARCHITECTURE_GATE.md)
- [../release/MESH.md](../release/MESH.md)
