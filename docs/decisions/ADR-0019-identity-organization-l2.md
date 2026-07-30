# ADR-0019 — Identity ↔ Organization L2 一致性边界

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. `Org.AddMembership` 必须通过注入的 Identity Membership Eligibility Port 校验主体资格。
2. 缺少 eligibility port、主体不存在、非 active 或不具备同租户资格时失败关闭。
3. 租户主体仅能加入其 `Subject.tenant_id` 对应租户。
4. AI Employee 仅在存在同租户 active AI assignment 时具备 membership 资格。
5. 跨租户 AI 改派使用 Identity-Organization L2 Coordinator，在同一 Unit of Work 中：
   - 结束旧租户全部 active memberships；
   - 执行 `Identity.ReassignAI`；
   - 提交领域变更与审计。
6. Coordinator 不自动创建目标租户 membership；目标组织结构归属仍需显式调用 AddMembership。
7. membership role label 不产生 Permission Grant。

## 边界

- Identity 是主体状态与 AI assignment 真相源。
- Organization 是 membership 真相源。
- Permission 是动作授权真相源。
- API/application 层不得把跨租户 AI 改派直接暴露为未协调的领域原语。

## 关联

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [../architecture/ORGANIZATION_INTERFACE.md](../architecture/ORGANIZATION_INTERFACE.md)
- [ADR-0017-ai-assignment-semantics.md](ADR-0017-ai-assignment-semantics.md)
