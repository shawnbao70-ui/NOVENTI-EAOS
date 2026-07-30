# ADR-0367 — Brain Execute + Twin Authorize Open Boundary

**状态：** Accepted  
**日期：** 2026-07-26  
**里程碑：** **PHX-G335**  
**归属：** Platform Brain / Twin（非 Kernel 业务实体）  
**授权源：** [Decision Summary](../project/BRAIN_TWIN_EXECUTION_AUTHORIZATION_SUMMARY.md) · [Coding Authorization](../project/BRAIN_TWIN_EXECUTION_CODING_AUTHORIZATION_SUMMARY.md)

> System-generated governance artifact (ADR-0321). Coding authorization granted
> for PHX-G335; Alembic none. Tip remains `0064_purchase_three_way_match_g334`.

## 背景

至今 Brain `request_execution` 与 Twin `authorize_from_twin` 无条件 fail-closed
（403 + `BRAIN_EXECUTION_FORBIDDEN` / `TWIN_EXECUTION_FORBIDDEN`）。Z3 仅挂只读
advisory。PO 打开执行面须独立 Gate + Coding Auth + 里程碑，不得由 Z3 暗示。

## 决策

1. Permission allow + 资格校验通过 → 可成功（本切片无商业副作用）；否则仍 403 与稳定错误码。  
2. 审计不可关闭；advisory envelope 仍 `execution_authority: "none"`。  
3. 不自动授权 Cap→grant，不静默驱动 SO/DO/AR/AP/RET/GL 写路径。  
4. Alembic：**none**（无执行账本表）。  
5. Status honesty：`execute_execution` / `authorize_execution` = `permission_gated`。

## 非目标

- 无限制自动业务写；去掉 deny 测试；与 PSP/Tax live 混批

## Product Owner approval record

```text
Design Gate: Approve
Coding Auth: Approve Milestone PHX-G335
Alembic: none
Signer: Product Owner — Shawn — 2026-07-26
```

## 关联

- [ADR-0135](ADR-0135-brain-execute-fail-closed-probe.md)  
- [ADR-0359](ADR-0359-brain-twin-crm-advisory-boundary.md)（Z3）  
- [POST_CRM_VERTICAL_ROADMAP](../project/POST_CRM_VERTICAL_ROADMAP.md)
