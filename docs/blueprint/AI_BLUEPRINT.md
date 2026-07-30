# AI 蓝图

**仓库：** `NOVENTI-EAOS`  
**文档 ID：** BP-AI  
**阶段：** PHX-002  
**版本：** 2.0

---

## 标题

EAOS AI 蓝图

## 目的

定义数字员工、AI 劳动力、智能体、推理边界与人工审批控制的 AI 原生运行模型。

## 范围

**范围内：** AI Runtime 概念边界、智能体/数字员工角色、权限与记忆约束、知识访问与推理策略、人工审批与审计要求。  
**范围外：** 将模型厂商选择锁定为产品战略、将提示词库当作生产业务逻辑、未经审计的自治写操作。

## 当前状态

**基线已建立 — PHX-002**（AI Runtime → PHX-A12；Enterprise Brain → PHX-E15）

## 未来扩展

智能体分类与生命周期、工具使用治理、记忆分层与保留、与 Workflow Kernel 的劳动力编排、面向市场的 AI 包契约。

---

## AI 原则

1. **AI Native** — AI 是一等平台能力  
2. **Knowledge Driven** — 推理消费受治理知识  
3. **Permissioned** — AI 继承 Kernel 授权  
4. **Human Approval Boundary** — 高影响动作需显式批准  
5. **Fully Auditable** — 实质性 AI 动作必须记录  

## 能力边界（概念）

| 类别 | 规则 |
|------|------|
| 只读推理 | 可在权限内自动执行 |
| 建议性动作 | 产出建议，默认不落库变更 |
| 写操作 / 外部副作用 | 必须权限 + 审计；高影响需人工批准 |
| 跨租户 | 禁止，除非宪法级例外并经 ADR |

## 关联文档

- [BLUEPRINT_INDEX.md](BLUEPRINT_INDEX.md)
- [KNOWLEDGE_BLUEPRINT.md](KNOWLEDGE_BLUEPRINT.md)
- [RUNTIME_BLUEPRINT.md](RUNTIME_BLUEPRINT.md)
- [EVENT_BLUEPRINT.md](EVENT_BLUEPRINT.md)
- [../standards/AI_STANDARD.md](../standards/AI_STANDARD.md)
