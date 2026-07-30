# AI 标准

**仓库：** `NOVENTI-EAOS`  
**阶段：** PHX-003  
**版本：** 2.0

---

## 标题

EAOS AI 标准

## 目的

规范 AI Runtime、智能体命名、权限、记忆、知识访问、推理、人工审批与审计。

## 范围

标准文档。本阶段不实现 AI Runtime。

## 当前状态

**已就绪 — PHX-003 基线**

## 未来扩展

工具白名单、模型路由策略、评估与红队流程。

---

## AI Runtime Rules

- AI 经 Runtime 执行，继承租户与身份上下文  
- 禁止绕过 Kernel 权限  
- 禁止静默跨租户访问  

## AI Agent Naming

- 稳定技术 ID + 可读显示名  
- 命名遵循 [NAMING_STANDARD.md](NAMING_STANDARD.md)  

## AI Permission

- 智能体权限显式授予，默认拒绝  
- 工具调用权限与数据访问权限分离评估  

## AI Memory

- 记忆分层：会话 / 租户长期 / 平台共享（若有）  
- 记忆读写受权限与保留策略约束  
- 不得将敏感秘密写入可导出记忆  

## Knowledge Access

- 仅访问授权知识集  
- 必须保留出处（provenance）以便审计与复核  

## Reasoning Policy

- 区分事实检索、推断与建议  
- 高影响结论须可解释到知识/工具依据  

## Human Approval Boundary

以下类别默认需要人工批准（可经 ADR 调整）：

- 资金/合同/合规相关写操作  
- 批量不可逆变更  
- 跨系统外部副作用  
- 权限提升相关操作  

## Audit Requirement

- 记录：主体、租户、关联 ID、工具调用、知识引用、批准状态、结果  
- 审计日志不可被智能体自行篡改  

## 关联文档

- [../blueprint/AI_BLUEPRINT.md](../blueprint/AI_BLUEPRINT.md)
- [NAMING_STANDARD.md](NAMING_STANDARD.md)
- [EVENT_STANDARD.md](EVENT_STANDARD.md)
