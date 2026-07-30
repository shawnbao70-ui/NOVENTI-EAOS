# ADR-0421 — Remediation Docker noventi Packaging Boundary

**状态：** Accepted（PHX-G407）  
**日期：** 2026-07-27  
**里程碑：** PHX-G407  
**授权源：** [Coding Authorization](../project/REMEDIATION_P0_DOCKER_NOVENTI_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Gateway 镜像必须包含运行时业务包目录 `noventi/`（与 `pyproject` include `noventi*` 一致）。  
2. 提供 import smoke：`api.gateway.app`、`noventi.crm`、`noventi.finance`（及 purchase/inventory）。  
3. 本切片仅为 **image packaging**；不等于宿主机软件安装，不等于 Marketplace host-acquire /
   Industry package host-install runtime invent。  
4. 无 Alembic；包版本仍为 `0.2.3`；外部 PSP / ENABLE_*_NETWORK 仍默认 OFF。
