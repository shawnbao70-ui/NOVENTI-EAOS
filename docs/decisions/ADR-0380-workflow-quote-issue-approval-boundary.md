# ADR-0380 — Workflow Quote.issue Approval Wiring Boundary

**状态：** Accepted（PHX-G348）  
**日期：** 2026-07-26  
**里程碑：** PHX-G348  
**授权源：** [Coding Authorization](../project/WF_QUOTE_ISSUE_APPROVAL_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 唯一挂钩命令：`Quote.issue`。  
2. 审批通过 ≠ 自动 issue；仅解除门禁。  
3. Human confirm 与 Workflow 审批分词。

## Workflow action binding

Use the existing `POST /v1/workflow/instances` surface to start a quote-issue
approval. Bind `approval_action` to `crm.quote.issue` and
`approval_resource_ref` to the quote UUID. After it is approved, the caller
supplies that instance id as `approval_ref` to `POST /v1/crm/quotes/{quote_id}/issue`;
the command still requires `human_confirm: true` and does not run automatically.
