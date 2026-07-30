# ADR-0008 — AI 人工审批边界（Human Approval Boundary）

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

AI Native 要求提高自动化，但宪章要求人的责任不可转移，且 AI 不得越权。

## 决策

### 可自动执行（在权限内）

- 只读推理与检索  
- 草稿/建议生成  
- 无外部副作用的内部辅助计算  

### 默认需要人工批准

- 资金、合同、合规相关写操作  
- 批量不可逆变更  
- 跨系统外部副作用（消息群发、支付、对外法律承诺等）  
- 权限提升或安全策略变更  
- 数字人对外高影响承诺  

### 强制机制

1. AI Runtime 提供 `RequestApproval` / `CommitAction`  
2. 未批准不得 `CommitAction`  
3. 批准人、时间、范围、关联 ID 必须审计  
4. 业务包不得关闭审批闸门  

## 后果

- AI 标准与 AI 蓝图必须引用本 ADR  
- 审批工作流应复用 Workflow Kernel，不平行实现  
- 详见 [../standards/AI_STANDARD.md](../standards/AI_STANDARD.md)、[../architecture/KERNEL_INTERFACES.md](../architecture/KERNEL_INTERFACES.md)
