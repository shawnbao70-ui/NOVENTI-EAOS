# 知识蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-KNOWLEDGE  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS 知识蓝图

## 目的

定义企业记忆、知识图谱、受治理检索，以及与数字孪生对齐的知识资产架构。

## 范围

**范围内：** 知识域与所有权、图/文档知识边界、经 Kernel 权限的访问控制、与 AI 推理及企业脑的关系。  
**范围外：** 将遗留 ERP 数据无结构倾倒视为架构、未经验证知识作为权威真值、绕过平台治理的包私有知识。

## 当前状态

**基线已建立 — PHX-002**（Knowledge → PHX-K10；Enterprise Brain → PHX-E15）

## 未来扩展

规范实体与关系模型、出处与置信度、摄入管线、孪生同步规则、市场知识包契约。

---

## 知识原则

1. 知识是平台资产，而非模块孤岛  
2. 企业决策必须具备出处（provenance）  
3. 所有知识存储适用租户隔离  
4. AI 仅可访问权限策略允许的知识  
5. 可抽取遗留业务知识；不可继承遗留架构  

## 知识分层（概念）

| 层 | 说明 |
|----|------|
| Canonical | 平台规范实体与关系 |
| Operational | 运行时业务事实 |
| Documentary | 文档与制度知识 |
| Derived | AI/规则推导结果（须标注） |

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [KERNEL_BLUEPRINT.md](KERNEL_BLUEPRINT.md)
- [AI_BLUEPRINT.md](AI_BLUEPRINT.md)
- [EVENT_BLUEPRINT.md](EVENT_BLUEPRINT.md)
