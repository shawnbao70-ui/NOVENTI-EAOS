# Legacy Knowledge Extract — Governance Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/governance/**`  
**Date:** 2026-07-23

## Purpose

提炼 Legacy 中跨业务模块的审批、文档与海关治理知识。这里只记录可验证的业务规则、流程、校验、数据语义和诚实缺口，不复制源码，不把元数据注册表或规划文档包装成已运行能力。

## Modules

| 模块 | 文件 |
|------|------|
| 审批中心 | [approval.md](approval.md) |
| 文档中心 | [documents.md](documents.md) |
| 海关与贸易中心 | [customs.md](customs.md) |

详见 [INDEX.md](INDEX.md)。

## Pack boundaries

- Approval Center 的审批记录，与 V18 各业务页面的 Human Approved 确认并非同一套持久化流程。
- Document Center V15.1 主要是默认关闭的元数据基础；上传、预览、版本回滚、分享和归档执行不能按注册名称推定为已实现。
- `contract` 在 Document Center 中只是模块标签；未发现商业合同 CRUD、状态机或合同主数据。
- Customs Center V15.1 主要是默认关闭的元数据注册中心；Incoterms、国家规则、运输方式、申报与清关均未替代 Legacy 运行流程。
- UNKNOWN 一律附已检索路径，不用设计意图填补实现缺口。
