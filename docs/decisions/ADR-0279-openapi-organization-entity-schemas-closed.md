# ADR-0279 — OpenAPI Organization Entity Schemas Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G260  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U133**

## 决策

Tenant/Enterprise/OrganizationUnit/Membership/IdResponse → `additionalProperties: false`；
live serialize keys only。organization patch bump；ops **1.0.55**；inventory PHX-G260。
