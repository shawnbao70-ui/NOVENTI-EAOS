# PHX-A03 Architecture Realignment Acceptance

**日期：** 2026-07-18  
**状态：** Accepted  
**依据：** EAOS Charter v2.1、ADR-0021、Roadmap v3、二次宪法合规报告

## 退出门禁

Roadmap v3 要求：EAOS 分层、Smart Terminal Blueprint 与 ownership map 完成，且每项能力具有唯一技术归属。

## 验收结果

| 能力 | 唯一技术归属 |
|------|--------------|
| Identity / Organization / Permission / Workflow | Core Kernel |
| AI execution / Agent execution / Plugin runtime | Platform Runtime |
| Data / Knowledge / Event / Integration / Configuration | Shared Platform Capability |
| Security / Audit / Monitoring | Cross-cutting Shared Capability |
| Smart Terminal shell、session、intent、preview、commit UX | Smart Terminal |
| Business truth 与业务规则 | Business Package / 其受治理真相源 |
| Package distribution、签名、计量与商业治理 | Marketplace |
| Insight、reasoning、simulation | Enterprise Brain |
| Governed enterprise state representation | Digital Twin |

## 兼容说明

- `kernel/event_bus/` 是 PHX-004 形成的兼容物理路径，不改变 Event Bus 的 Shared Platform Capability 所有权。
- Core Kernel 可持有 Knowledge 授权、租户与 provenance 治理端口，但不拥有 Knowledge 服务实现。
- Smart Terminal 消费 API、Runtime 与 Package surface，不持有身份、权限、审批、知识或业务真相。

## 审查证据

- [EAOS Architecture](../architecture/EAOS_ARCHITECTURE.md)
- [Kernel Blueprint](../blueprint/KERNEL_BLUEPRINT.md)
- [Smart Terminal Blueprint](../blueprint/SMART_TERMINAL_BLUEPRINT.md)
- [ADR-0021](../decisions/ADR-0021-constitutional-platform-layering.md)
- [Second-Pass Compliance Report](../reviews/CONSTITUTION_SECOND_PASS_REPORT_2026-07-18.md)

## 结论

PHX-A03 退出门禁通过。后续实现必须先按本表确定 ownership；如需改变上述边界，必须新增 ADR，并在涉及第一原则时暂停取得人工批准。
