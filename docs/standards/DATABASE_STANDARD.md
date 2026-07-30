# 数据库标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS 数据库标准

## 目的

规范未来 schema 的命名、键、审计字段、软删除、UUID 与索引策略。

## 范围

标准与持久化基础设施。当前已建立 SQLAlchemy metadata、Alembic `0001`～`0010` 与 Kernel/Identity Foundation 表；业务包表尚未创建。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

业务包表映射、租户索引模板与迁移部署流程。

---

## Naming Convention

- 表名：复数、snake_case（例：`organizations`）  
- 列名：snake_case  
- 布尔列：`is_` / `has_` 前缀  
- 禁止使用遗留库表命名作为本平台规范来源  

## Primary Keys

- 优先使用 UUID 作为对外/跨系统主键  
- 单表内主键列名统一为 `id`  

## Foreign Keys

- 外键列：`{referenced_singular}_id`  
- 必须声明引用完整性策略（实现期）  
- 跨租户外键禁止  

## Soft Delete

- 业务实体默认软删除：`deleted_at`（可空时间戳）  
- 查询默认排除已软删记录  
- 物理删除需显式策略与审计  

## Audit Fields

所有持久化业务实体应包含审计能力（谁在何时变更）。

## Created At / Updated At

- `created_at`：创建时间（UTC）  
- `updated_at`：最后更新时间（UTC）  

## Version

- `version`：乐观并发控制整型或等价版本令牌  

## Status

- `status`：生命周期状态（枚举受控，禁止自由文本泛滥）  

## UUID Policy

- 对外标识使用 UUID  
- 生成策略在实现期统一（ADR 锁定）  
- UUID 不得承载业务语义  

## Index Strategy

- 为高频过滤字段建立索引（tenant_id、外键、状态、常用查询键）  
- 复合索引必须匹配真实查询顺序  
- 避免过度索引；写入热点表需评审  

## Migration Tooling

- ORM：SQLAlchemy 2
- 迁移：Alembic
- 驱动：`postgresql+psycopg`
- 生产环境禁止运行时自动建表
- 真实连接凭据只能通过安全环境变量或 Secret Manager 注入
- 每次 schema 变更必须具有可审查的 upgrade/downgrade 迁移

## 多租户

- 租户作用域数据必须包含 `tenant_id`  
- 所有查询默认带租户谓词  

## 关联文档

- [NAMING_STANDARD.md](NAMING_STANDARD.md)
- [API_STANDARD.md](API_STANDARD.md)
