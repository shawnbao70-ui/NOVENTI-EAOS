# Finance Commission Ledger Architecture Gate

**日期：** 2026-07-26  
**状态：** Gate Accepted（design boundary only；coding authorization = None）  
**规范源：** ADR-0322  
**里程碑：** 未分配；`PHX-G314` 未打开  
**授权源：** [Approved Authorization Summary](FIN_COMMISSION_LEDGER_AUTHORIZATION_SUMMARY.md)  
**生成物：** [System-generated Acceptance](FIN_COMMISSION_LEDGER_ACCEPTANCE.md)

## Accepted design boundary

| Concern | Accepted ruling |
|---|---|
| Ownership | `noventi.finance` / `pkg.finance.commission`；非 CRM、非 Kernel |
| Entry | `CommissionEntry`，状态仅 `accrued` |
| Source | 同租户、状态为 `issued` 的 AR Invoice only |
| Amount/currency | explicit amount > 0；request currency 必须匹配 invoice |
| Beneficiary | 同租户 known/eligible subject；具体 eligibility contract 后置 |
| Uniqueness | tenant+idempotency key 与 tenant+invoice+beneficiary 双约束 |
| Permission | create/read default-deny；trusted execution context |
| Audit | 应计动作与拒绝可审计；敏感 payload 最小化 |
| Interface intent | future POST collection + GET by id；当前无 API artifact |
| Migration posture | 当前 tip 保持 `0048`；未来获批时推荐 `0049_finance_commission_ledger_g314` |

## In（design only）

- accrual-only CommissionEntry 语义
- issued-invoice source、explicit amount、currency match、beneficiary eligibility 边界
- tenant isolation、Permission、audit、idempotency 与 duplicate-accrual guard
- future interface intent 与 future migration recommendation

## Out

- payout/payroll/PSP/bank transfer、GL/journal、tax withholding
- clawback、multi-tier hierarchy、partner portal
- payable/paid/cancelled 状态与 Z2b/Z3
- Customer360 write-back、Brain execute、Twin authorize
- SQL、Alembic、OpenAPI、API route、service、repository、UI、runtime manifest
- `PHX-G314` 创建/分配、`0049` migration 创建、tip bump
- DAL/status/changelog/release promotion 或任何 Coding Authorization 暗示

## Generated OD dispositions

| ID | Product Owner disposition |
|---|---|
| OD-01 | Accept：Package = `noventi.finance` |
| OD-02 | Accept：source = issued AR Invoice only |
| OD-03 | Accept：currency 显式请求并必须匹配 invoice |
| OD-04 | Accept design recommendation：未来获批迁移使用 `0049`，不跳到 `0050` |
| OD-05 | Accept：双唯一性边界同时成立 |

## Generated RC attestations

| ID | Reject if true | System attestation |
|---|---|---|
| RC-01 | Gate 包含 payout/payroll/PSP/GL | False |
| RC-02 | source 允许非 issued invoice 或 confirmed SO | False |
| RC-03 | payable/paid/cancelled/clawback 被隐式打开 | False |
| RC-04 | Tenant/Permission default-deny 缺失 | False |
| RC-05 | 只使用单一唯一性而允许重复应计 | False |
| RC-06 | 创建 `0049`/`0050` migration 或 bump tip | False |
| RC-07 | 打开或分配 `PHX-G314` | False |
| RC-08 | 生成 SQL/API/service/UI/runtime manifest | False |
| RC-09 | Design approval 被解释为 Coding Authorization | False |

## Coding separation

Product Owner 的 Approve 只接受 Authorization Summary 中的设计边界。任何数据库表、`0049` migration、接口、服务、runtime manifest、里程碑或业务写路径仍需独立明确 Coding Authorization。

## Generated artifact index

- [Authorization Summary](FIN_COMMISSION_LEDGER_AUTHORIZATION_SUMMARY.md)
- [ADR-0322](../decisions/ADR-0322-finance-commission-ledger-design-boundary.md)
- [Acceptance](FIN_COMMISSION_LEDGER_ACCEPTANCE.md)
