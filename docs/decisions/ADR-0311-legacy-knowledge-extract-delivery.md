# ADR-0311 — Legacy Knowledge Extract Delivery Pack

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G292  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U165**

## 决策

接受 `docs/knowledge/legacy-extract/delivery/**`：SO→DO 不扣库存、Type A 出库双写、Complete、DO→AR 应计（非税票）。明确双 create 路径与 create_do 服务端权限缺口。不实现 Delivery 产品模块；包 `0.2.1`；Alembic `0029`。
