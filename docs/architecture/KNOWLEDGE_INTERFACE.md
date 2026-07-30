# Knowledge Shared Capability 接口规格

**文档 ID：** IF-KNOWLEDGE-001  
**版本：** 1.0  
**阶段：** PHX-K10  
**状态：** Architecture / Interface Gate Accepted  
**仓库：** `NOVENTI-EAOS`

---

## 标题

Knowledge Shared Platform Capability 接口规格

## 目的

细化 Entity / Link / Provenance / Retention / Share / 授权检索接口，作为 PHX-K10 实现依据，并固定 Shared 所有权与 Core 治理端口边界。

## 范围

图谱写入、出处、归档、关键词检索与租户内共享。向量引擎、Twin、Brain、AI Memory、Marketplace、可靠 outbox 显式延后。

## 当前状态

**PHX-K10 Knowledge 授权检索与出处基线已接受**

## 未来扩展

向量检索、摄入管线、Digital Twin 同步、Enterprise Brain（E15）、AI Memory（A12）、Marketplace 知识包（M16）、可靠事件投递（P11）。

---

## 不变式

1. Knowledge 技术归属 Shared Platform Capability；Core 不抢占所有权  
2. Permission.Evaluate 是唯一授权真相；缺租户/缺权限默认拒绝  
3. 每次写入必须携带 `source_ref` + `reason` 并 append provenance  
4. `layer=derived` 必须标注；不得原地伪装为 canonical  
5. Entity 更新使用 `expected_version` 乐观锁  
6. archived / retain_until 到期后读取 fail-closed  
7. 跨租户默认拒绝；Share 仅租户内可见性扩展记录  
8. API 不接受客户端声明 `tenant_id`、`session_id`、`platform_scope` 或 `execution_context`  

---

## 核心概念

| 概念 | 说明 |
|------|------|
| Entity | 租户作用域节点；layer ∈ canonical/operational/documentary/derived |
| Link | 同租户有向边；禁止自环 |
| Provenance | append-only 出处；含 actor / source_ref / reason / derived |
| Retention | active → archived；可选 retain_until |
| Share | 租户内 `shared_with_subject_ids` 扩展记录 |

---

## Ports（外部真相源）

| Port | 职责 | 归属 |
|------|------|------|
| `PermissionEvaluator` | Upsert / Link / Query / Search / Provenance / Archive / Share | Permission |
| Tenant boundary | 租户隔离与 fail-closed | Organization / Context |

缺失、未知或 error 时全部 fail closed。

---

## 接口明细

### Knowledge.UpsertEntity

- **HTTP：** `POST /knowledge/entities`  
- **输入：** entity_type、name、layer、attributes?、labels?、retain_until?、source_ref、reason、entity_id?、expected_version?  
- **输出：** entity_id  
- **约束：** provenance 必填；secrets 禁止；derived 不得伪装为 canonical  
- **审计：** 是  
- **错误：** `KNOWLEDGE_PROVENANCE_REQUIRED`、`KNOWLEDGE_SECRET_FORBIDDEN`、`KNOWLEDGE_DERIVED_MISLABELLED`、`KNOWLEDGE_VERSION_CONFLICT`、`PERMISSION_DENIED`

### Knowledge.Link

- **HTTP：** `POST /knowledge/links`  
- **输入：** from_entity_id、to_entity_id、relation_type、attributes?、source_ref、reason  
- **输出：** link_id  
- **约束：** 禁止自环；两端须同租户且可读可写  
- **错误：** `KNOWLEDGE_LINK_INVALID`、`KNOWLEDGE_ENTITY_NOT_FOUND`、`PERMISSION_DENIED`

### Knowledge.GetEntity / Query / Search

- **HTTP：** `GET /knowledge/entities/{entityId}`、`GET /knowledge/entities`、`GET /knowledge/search`  
- **约束：** Permission + tenant；archived / expired fail-closed  
- **错误：** `KNOWLEDGE_ENTITY_NOT_FOUND`、`KNOWLEDGE_ARCHIVED`、`KNOWLEDGE_RETENTION_EXPIRED`、`PERMISSION_DENIED`

### Knowledge.GetProvenance

- **HTTP：** `GET /knowledge/provenance/{subjectKind}/{subjectId}`  
- **输出：** 按时间排序的 provenance 列表  
- **错误：** `KNOWLEDGE_ENTITY_NOT_FOUND`、`KNOWLEDGE_LINK_NOT_FOUND`、`PERMISSION_DENIED`

### Knowledge.ArchiveEntity / Share

- **HTTP：** `POST .../archive`、`POST .../share`  
- **输入：** source_ref、reason、expected_version?；（Share 另需 share_with_subject_id）  
- **约束：** 乐观锁；Share 仅同租户  
- **错误：** `KNOWLEDGE_ARCHIVED`、`KNOWLEDGE_VERSION_CONFLICT`、`PERMISSION_DENIED`

---

## 关联

- [KNOWLEDGE_STATE_MACHINES.md](KNOWLEDGE_STATE_MACHINES.md)
- [KNOWLEDGE_EVENTS.md](KNOWLEDGE_EVENTS.md)
- [ERROR_CODES.md](ERROR_CODES.md)
- [../api/knowledge.openapi.yaml](../api/knowledge.openapi.yaml)
- [../decisions/ADR-0025-knowledge-shared-capability.md](../decisions/ADR-0025-knowledge-shared-capability.md)
- [../project/PHX-K10_ARCHITECTURE_GATE.md](../project/PHX-K10_ARCHITECTURE_GATE.md)
