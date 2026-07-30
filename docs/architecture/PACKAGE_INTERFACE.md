# Package Platform 接口规格

**文档 ID：** IF-PKG-001  
**版本：** 1.0  
**阶段：** PHX-B14  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

## 目的

细化 Manifest、Install、Surface/Action 解析接口，确保「不分叉 Kernel」。

## 不变式

1. Package Platform 落点 `eaos_platform.package`；制品在 `packages/`  
2. `package_key` 不得以 `kernel.` / `eaos.kernel.` 开头  
3. Action `resource_type` 必须 `pkg.*`；禁止占用保留资源类型  
4. 仅 published 可安装；仅 installed 可解析  
5. ResolveAction 经 Permission，不产生业务副作用  
6. 未声明 surface/action 失败关闭  

## 接口

| 接口 | HTTP | 权限要点 |
|------|------|----------|
| RegisterManifest | `POST /packages/manifests` | `package_manifest:register` |
| PublishManifest | `POST .../publish` | `package_manifest:publish` |
| InstallPackage | `POST /packages/installations` | `package_installation:install` |
| ListSurfaces | `GET /packages/surfaces` | `package_surface:read` |
| ResolveAction | `POST /packages/actions/resolve` | `package_action:resolve` + 业务权限 |

## 错误

`PACKAGE_KERNEL_FORK_DENIED`、`PACKAGE_MANIFEST_INVALID`、`PACKAGE_NOT_FOUND`、`PACKAGE_NOT_PUBLISHED`、`PACKAGE_NOT_INSTALLED`、`PACKAGE_ALREADY_INSTALLED`、`PACKAGE_ACTION_UNDECLARED`、`PACKAGE_SURFACE_UNDECLARED`、`PACKAGE_VERSION_CONFLICT`

## 关联

- [PACKAGE_STATE_MACHINES.md](PACKAGE_STATE_MACHINES.md)
- [../api/package.openapi.yaml](../api/package.openapi.yaml)
- [../decisions/ADR-0029-business-package-platform.md](../decisions/ADR-0029-business-package-platform.md)
