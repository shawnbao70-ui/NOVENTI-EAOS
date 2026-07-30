# ADR-0042 — Gateway Package Platform HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G27  
**归属：** Platform API Gateway

## 背景

PHX-B14 已交付 Package Platform（manifest / install / surface / resolve）。OpenAPI `package.openapi.yaml` 定义租户面 HTTP；网关需薄适配，不托管包经济或业务规则。

## 决策

### 1. 租户面上下文

- 全部 `/v1/packages*` 使用 `derive_tenant_context`
- Body 经 `reject_context_override`
- 权限仍由 `PackageService` + `PermissionService` 裁决

### 2. 本切片路由

| Method | Path | Kernel |
|--------|------|--------|
| POST | `/v1/packages/manifests` | `register_manifest` |
| GET | `/v1/packages/manifests/{id}` | `get_manifest` |
| POST | `/v1/packages/manifests/{id}/publish` | `publish_manifest` |
| POST | `/v1/packages/installations` | `install_package` |
| POST | `/v1/packages/installations/{id}/disable` | `disable_installation` |
| GET | `/v1/packages/surfaces` | `list_surfaces` |
| POST | `/v1/packages/actions/resolve` | `resolve_action` |

### 3. Explicit Defer

- Marketplace 商业/法律门禁
- JWT/OIDC 产品化
- 包热更新 / 多版本并存策略变更

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G27_ARCHITECTURE_GATE.md](../project/PHX-G27_ARCHITECTURE_GATE.md)
- [../api/package.openapi.yaml](../api/package.openapi.yaml)
