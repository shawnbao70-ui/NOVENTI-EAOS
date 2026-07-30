# ADR-0015 — Identity Credential 生命周期与 Session 绑定

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. 新增 `Identity.ValidateCredential` 与 `Identity.RevokeCredential`。
2. `CreateSession` 移除 `auth_factors_ok` 布尔信任，改为必填 `credential_id`。
3. 有效凭证必须为 active、未过期，并同时匹配当前 tenant 与 subject。
4. 跨租户或主体不匹配按 credential invalid/not found 处理，不泄露存在性。
5. 新会话记录绑定 `credential_id`；迁移列允许旧会话为空，新代码创建时必须非空。
6. 撤销凭证立即阻止新会话，但不级联撤销既有会话；Session 保持独立生命周期。
7. Credential 返回视图不得包含 `secret_handle`。

## 后果

- 调用方必须先完成外部认证因子校验并选择已绑定 Credential。
- 已有会话如需终止，必须显式调用 RevokeSession。
- 本决策不实现密码/OIDC/JWT 协议或 Secret Vault。

## 关联

- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [ADR-0014-identity-session-validation.md](ADR-0014-identity-session-validation.md)
