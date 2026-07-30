# Object360 Knowledge Extract — Index

**Source root:** `H:\Workspace\EZAM_CRM - 9.0`（只读） · **Verified:** 2026-07-23

| Topic | File | Evidence strength |
|---|---|---|
| Customer360 | [customer360.md](customer360.md) | Strong：客户详情查询、十二区块、商业统计与集合；Medium：并行 runtime context；Missing：统一事件、附件和全对象权限模型 |
| Sample360 | [sample360.md](sample360.md) | Strong：旧 Sample360 分析页面；Medium：Sample detail 并行 runtime bundle；Missing：申请/审批/发样/POD 与统一生命周期 |
| History / Audit | [history_audit.md](history_audit.md) | Strong：Sample log 与通用 audit 表形；Weak/Missing：对象写入覆盖、不可篡改、保留及导出保证 |

## Evidence model

- **Operational:** 页面或 API 实际查询、计算、保存和跳转。
- **Parallel context:** 从 Legacy page context 派生，但不取代 Legacy renderer。
- **Metadata/scaffold:** registry、history facade 或 schema 声明，未证明完整写入闭环。
- **UNKNOWN:** 已检索仍未找到足够运行证据。

## Cross references

- 跟进实体与 Customer360 时间线：[../followup/followup.md](../followup/followup.md)
- CRM 客户/商机边界：[../crm/](../crm/)
- 样品主流程、追溯和物化：[../sample/sample.md](../sample/sample.md)
- 样品发样与 POD 缺口：[../sample/outbound.md](../sample/outbound.md)、[../sample/pod.md](../sample/pod.md)
