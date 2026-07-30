# PHX-B14 Business Package Platform Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted；实现已验收（见 PHX-B14_ACCEPTANCE）  
**归属：** Shared Platform Capability / Package Platform  
**规范源：** BOOK08、BOOK11、BOOK19、BOOK22、BOOK23、ADR-0021、ADR-0029  
**退出门禁：** 不分叉 Kernel

## 1. 门禁目标

交付 Package Platform 最小垂直切片：Manifest 注册/发布、租户安装、Surface/Action 契约解析，并证明未声明能力与 Kernel 保留资源被拒绝。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Shared Capability；`eaos_platform.package` |
| Artifacts | `packages/<package_key>/` 声明式样例 |
| Manifest | package_key + version + type + surfaces/actions |
| Install | 租户级；仅 published 可装 |
| Resolve | 声明 + 安装 + Permission；无业务副作用 |
| Kernel guard | 禁止保留资源类型与 kernel.* 包键 |

## 3. Action / Resource Contract

- `package_manifest:register|publish|read`
- `package_installation:install|disable|read`
- `package_surface:read`
- `package_action:resolve`

资源：

- `package_manifest:{id}`
- `package_installation:{id}`
- `package_action:{action_key}`

## 4. 实现切片

### Slice A — Manifest Domain

- Register / Publish / GetManifest
- Surface / Action 声明校验

### Slice B — Install + Resolve

- Install / Disable
- ListSurfaces / ResolveAction

### Slice C — Persistence

- SQLAlchemy + Transactional facade + Alembic `0018`

### Slice D — Contracts

- OpenAPI / 状态机 / 样例包 / PostgreSQL / 七步自审

## 5. Exit Criteria

1. 包不能声明 Kernel 保留资源类型或 `kernel.*` 包键。  
2. 未发布不可安装；未安装不可解析。  
3. 未声明 action/surface 失败关闭。  
4. ResolveAction 经 Permission，不写入业务真相。  
5. OpenAPI / Data Model / Migration / Code 一致。  
6. PostgreSQL 与完整回归通过。  
7. 不宣称 Marketplace 或完整行业 ERP 已交付。

## 6. Explicit Defer

- Marketplace 签名/计费、Extension 沙箱执行
- 多租户共享全球目录产品化
- 具体行业业务实体实现
