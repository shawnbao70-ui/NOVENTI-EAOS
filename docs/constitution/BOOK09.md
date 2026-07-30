# BOOK09 — 开发者宪法

**仓库：** `NOVENTI-EAOS`  
**版本：** EAOS Charter v2.1  
**状态：** 生效

---

## 标题

开发者宪法

## 目的

确立开发者义务、工程质量、扩展边界与对宪法/标准的遵从。

## 范围

开发者宪政。对齐开发标准与 Git 工作流。

## 当前状态

**规范正文生效**

## 未来扩展

贡献者协议与评审门禁细则。

---

## 核心条款

1. 开发必须遵循 BOOK22 统一工程顺序：Constitution → Ownership Classification → Blueprint → Standards → ADR → Interfaces → Data Models → Implementation → Testing → Documentation → Review → Release / Optimization。  
2. 开发顺序不得倒置。  
3. 功能完备定义：架构 + 接口 + 数据模型 + 实现 + 测试 + 文档 + 评审。  
4. 禁止在遗留仓库进行 EAOS 开发。  
5. 禁止业务逻辑写入路由；禁止包内重复实现内核能力。  
6. 公共接口必须类型化、文档化、可测试。  
7. 安全与权限缺陷优先于功能交付。  
8. 破坏性变更必须版本化并记录 ADR。  

## 关联文档

- [BOOK01.md](BOOK01.md)
- [BOOK21.md](BOOK21.md)
- [BOOK22.md](BOOK22.md)
- [../standards/CODING_STANDARD.md](../standards/CODING_STANDARD.md)
- [../standards/GIT_WORKFLOW.md](../standards/GIT_WORKFLOW.md)
