# ADR-0010 — Foundation 切片使用内存仓储

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

PHX-004 启动最小垂直切片。ADR-0009 延后锁定具体数据库产品。

## 决策

Identity Kernel 首个可执行切片使用**进程内内存仓储**：

1. 验证执行上下文、错误码、接口语义与契约测试  
2. 不引入遗留 ERP 数据库依赖  
3. 后续以相同接口替换为持久化实现，不改变对外契约  

## 后果

- 重启进程数据丢失（可接受于 Foundation）  
- 契约测试必须不依赖外部 DB  
- 持久化实现另立迁移与选型 ADR  

## 关联

- [ADR-0009-kernel-persistence-tenancy.md](ADR-0009-kernel-persistence-tenancy.md)
- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
