# Organization Kernel State Machines

**文档 ID：** SM-ORG-001  
**版本：** 1.0  
**里程碑：** PHX-K07  
**状态：** Accepted

## 1. Tenant

```text
CREATE → ACTIVE
ACTIVE → SUSPENDED
SUSPENDED → ACTIVE
ACTIVE | SUSPENDED → CLOSED
CLOSED → (terminal)
```

- Suspend / Reactivate 要求 Platform Identity Governor、reason 与 `expected_version`。
- CLOSED 执行命令延后至 Workflow 人工审批与跨 Kernel 清理协调。
- SUSPENDED / CLOSED 时 Organization 数据面写操作失败关闭。

## 2. Enterprise

```text
CREATE → ACTIVE
ACTIVE ↔ SUSPENDED
ACTIVE | SUSPENDED → CLOSED
CLOSED → (terminal)
```

- Enterprise 永远属于一个 Tenant，不得跨 Tenant 移动。
- 每个 Tenant 必须且仅能有一个 primary Enterprise。
- Enterprise close 存在 active Unit / Membership 时拒绝。

## 3. Organization Unit

```text
CREATE → ACTIVE | INACTIVE
ACTIVE ↔ INACTIVE
ACTIVE | INACTIVE → CLOSED
CLOSED → (terminal)
```

- Unit 永远属于同一 Tenant 与 Enterprise。
- parent 必须 active、同 Tenant、同 Enterprise，且不得形成 self/cycle。
- CLOSED Unit 不得成为 parent 或 Membership transfer 目标。
- Unit close 存在 active descendants / Membership 时拒绝。

## 4. Membership

```text
CREATE → ACTIVE
ACTIVE → SUSPENDED
SUSPENDED → ACTIVE
ACTIVE | SUSPENDED → ENDED
ENDED → (terminal)
```

- 创建前必须通过 Identity eligibility。
- AI Employee 必须具有同 Tenant active assignment。
- 仅 ACTIVE Membership 可在同 Enterprise 内转移 Unit。
- ENDED 后可创建新的 Membership 历史段，但旧记录不可修改。
- `membership_role_label` 不产生 Permission Grant。

## 5. 并发

所有更新命令要求 `expected_version >= 1`：

```text
stored.version == expected_version
  → apply transition
  → version = expected_version + 1
  → commit domain + audit atomically

stored.version != expected_version
  → ORG_VERSION_CONFLICT
  → rollback
```

## 6. 错误映射

| 条件 | 错误码 |
|------|--------|
| 非法状态转换 | `ORG_INVALID_STATE_TRANSITION` |
| stale version | `ORG_VERSION_CONFLICT` |
| Tenant suspended / closed | `ORG_TENANT_SUSPENDED` / `ORG_TENANT_CLOSED` |
| Unit self/cycle | `ORG_UNIT_CYCLE_DETECTED` |
| Unit / Membership Enterprise 不一致 | `ORG_UNIT_ENTERPRISE_MISMATCH` |
| ended / non-active Membership 修改 | `ORG_MEMBERSHIP_NOT_ACTIVE` |
| active dependencies 阻止 close | `ORG_ACTIVE_DEPENDENCIES` |

## 7. 关联

- [Organization Interface](ORGANIZATION_INTERFACE.md)
- [Kernel Data Model](KERNEL_DATA_MODEL.md)
- [ADR-0022](../decisions/ADR-0022-organization-lifecycle-hierarchy.md)
- [PHX-K07 Architecture Gate](../project/PHX-K07_ARCHITECTURE_GATE.md)
