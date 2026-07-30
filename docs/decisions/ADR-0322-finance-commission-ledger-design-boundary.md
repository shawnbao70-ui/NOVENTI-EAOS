# ADR-0322 — Finance Commission Ledger Design Boundary

**状态：** Accepted（design boundary only；coding authorization = None）  
**日期：** 2026-07-26  
**里程碑：** 未分配；`PHX-G314` 仅为候选标签，不由本 ADR 打开  
**归属：** `noventi.finance` Business Package（非 Kernel）  
**授权源：** [Approved Authorization Summary](../project/FIN_COMMISSION_LEDGER_AUTHORIZATION_SUMMARY.md)

## 背景

Finance 需要一个可审计、只记录应计事实的 Commission Ledger 设计边界。Product Owner 已通过单次 Authorization Summary 接受该边界；本 ADR 由系统生成，不是实现授权。

## 决策

1. Commission Ledger 归属 `noventi.finance`，资源类型为 `pkg.finance.commission`；CRM 仅提供已开立 AR Invoice 的来源引用，不拥有佣金台账。
2. `CommissionEntry` 设计边界包含 tenant、source invoice、beneficiary subject、currency、explicit amount、`accrued` 状态、idempotency key、created time 与 version。
3. 唯一允许的来源是同租户、状态为 `issued` 的 AR Invoice；confirmed SO 或其他商业文档不能作为来源。
4. amount 必须显式提供且大于零；currency 必须显式提供并与 source invoice currency 匹配。
5. 状态仅为 `accrued`；本 Gate 不定义 payable、paid、cancelled、clawback 或 payout 状态机。
6. 未来写契约必须同时保证 tenant+idempotency key 与 tenant+invoice+beneficiary 两个唯一性边界。
7. 未来 create/read 均经 Permission default-deny；tenant、caller、subject 与 execution context 不能由不可信请求字段覆盖。
8. 未来应计动作必须可审计；审计元数据不复制不必要的 amount 或敏感 beneficiary 数据。
9. `POST /v1/finance/commissions` 与 `GET /v1/finance/commissions/{id}` 只作为已接受的接口意图；当前不生成 OpenAPI、route、service 或业务写路径。

## Alembic posture

- 当前已知 tip 为 `0048_finance_ar_credit_note_g312`。
- 本设计批准不创建 migration，也不 bump tip。
- 若未来独立 Coding Authorization 明确批准数据库表，推荐下一 revision 为 `0049_finance_commission_ledger_g314`。
- 不使用 `0050` 跳过空闲 `0049`，除非 Product Owner 另行明确接受 skip rationale。
- `PHX-G314`、`0049` 与表设计都不是本 ADR 产生的实现授权。

## 后果

- Finance 获得最小、accrual-only 的佣金事实边界。
- payout/payroll/PSP/GL 与状态推进保持关闭。
- 未来实现仍需独立 Coding Authorization、明确里程碑、数据模型/API/迁移契约与验证计划。

## 非目标

- payout、payroll、bank/PSP transfer、partner portal、multi-tier hierarchy
- clawback、GL/journal、tax withholding、payable/paid/cancelled 状态
- Customer360 write-back、Brain execute、Twin authorize、Z2b、Z3
- SQL、Alembic、API、service、UI、repository、runtime manifest 或任何业务实现
- 自行打开 `PHX-G314`、创建 `0049`、更新 DAL/status/changelog/release 或暗示 Coding Authorization

## 关联

- [Authorization Summary](../project/FIN_COMMISSION_LEDGER_AUTHORIZATION_SUMMARY.md)
- [Architecture Gate](../project/FIN_COMMISSION_LEDGER_ARCHITECTURE_GATE.md)
- [System-generated Acceptance](../project/FIN_COMMISSION_LEDGER_ACCEPTANCE.md)
- [Permission Interface](../architecture/PERMISSION_INTERFACE.md)
- [Event Interface](../architecture/EVENT_INTERFACE.md)
- [Package Blueprint](../blueprint/PACKAGE_BLUEPRINT.md)
