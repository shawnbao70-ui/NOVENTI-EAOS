# ADR-0018 — AI Employee Profile 持久化

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. AI Employee Profile 使用独立 `ai_employee_profiles` 表，与 AI Subject 一对一。
2. Profile 保存 `capabilities_profile_ref` 与 `owner_policy_ref`，两者均为受治理策略引用。
3. Identity 不解释 capability 内容，也不依据 Profile 授权；实际授权始终由 Permission Kernel 判定。
4. 注册 AI Employee 时 Subject 与初始 Profile 必须在同一事务创建。
5. 仅 active Platform Identity Governor 可更新 Profile。
6. 更新采用显式 `expected_version` 乐观锁；版本不匹配失败关闭。
7. Profile 不包含密钥、凭证、模型参数、租户知识、记忆或 Permission Grant。

## 后果

- Repository 增加 Profile 的 add/get/save 端口。
- RegisterAIEmployee 不再只把 Profile 输入写入审计，而是持久化。
- Profile 生命周期独立于 tenant assignment；改派不复制或改写 Profile。

## 关联

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [ADR-0017-ai-assignment-semantics.md](ADR-0017-ai-assignment-semantics.md)
- [../architecture/PERMISSION_INTERFACE.md](../architecture/PERMISSION_INTERFACE.md)
