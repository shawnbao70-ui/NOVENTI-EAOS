# ADR-0009 — Kernel 持久化与逻辑多租户策略

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

Kernel 即将进入实现准备。必须先锁定：

1. 多租户是逻辑隔离还是物理分库  
2. 持久化技术选型边界  
3. 与遗留 ERP 数据库的关系  

若不定，实现将漂移并可能继承遗留库结构。

## 决策

### 1. 多租户：逻辑隔离（Logical Tenancy）为默认

- 租户作用域数据在同一逻辑库/模式中以 `tenant_id` 强制隔离  
- 所有查询默认带租户谓词  
- 跨租户访问默认拒绝（失败关闭）  
- 物理分库/分模式可作为**未来企业版增强**，不得作为 Kernel v1 前置依赖  

### 2. 持久化：平台自有模型，不映射遗留表

- Kernel 使用 `NOVENTI-EAOS` 自有概念模型（见 `KERNEL_DATA_MODEL.md`）  
- **禁止**将遗留 ERP 表结构作为 Kernel schema 来源  
- 遗留库仅可只读抽取业务知识，不得成为运行时依赖  

### 3. 迁移与演进

- Schema 变更必须版本化迁移  
- 破坏性变更需 ADR + 主版本  
- 软删除与审计字段遵循 `DATABASE_STANDARD.md`  

### 4. 实现期技术绑定（有意延后）

本 ADR **不**锁定具体数据库产品或 ORM。  
实现启动时另立短 ADR（例如 PostgreSQL + 选定 ORM），但不得违反本决策第 1–3 条。

## 后果

| 方面 | 影响 |
|------|------|
| 数据模型 | 所有租户实体含 `tenant_id` |
| 测试 | 强制跨租户负面用例 |
| 遗留 | 零运行时耦合 |
| 扩展 | 日后可加物理隔离而不改宪法语义 |

## 关联文档

- [ADR-0007-tenant-isolation.md](ADR-0007-tenant-isolation.md)
- [../architecture/KERNEL_DATA_MODEL.md](../architecture/KERNEL_DATA_MODEL.md)
- [../standards/DATABASE_STANDARD.md](../standards/DATABASE_STANDARD.md)
- [../constitution/BOOK04.md](../constitution/BOOK04.md)
