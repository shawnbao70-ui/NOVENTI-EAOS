# PHX-M16 Marketplace Technical Foundation Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted；技术骨架已验收（见 PHX-M16_ACCEPTANCE；商业门禁仍开放）  
**归属：** Shared Platform Capability / Marketplace  
**规范源：** BOOK08、BOOK11、BOOK19、BOOK22、BOOK23、ADR-0029、ADR-0031  
**退出门禁（本切片）：** 签名可验证引用、可审核、可撤销；商业政策 API 失败关闭  
**商业/法律门禁：** 仍开放（定价/分成/账单/争议不得宣称已交付）

## 1. 门禁目标

交付 Marketplace 技术最小垂直切片：Listing、签名引用、审核、发布、撤销、租户获取；并证明商业政策 API 不可用。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `eaos_platform.marketplace` |
| Listing | package_key + version + capability declaration |
| Signature | 发布前强制 `signature_ref`（引用，非自研密码学） |
| Review | submitted → approved/rejected |
| Acquire | 技术获取记录；≠ 购买合同 |
| Commercial APIs | 恒 `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED` |

## 3. Action / Resource Contract

- `marketplace_listing:create|submit|review|publish|revoke|read`
- `marketplace_acquisition:acquire|read`

## 4. 实现切片

### Slice A — Listing + Signature + Review

### Slice B — Publish / Revoke / Acquire + commercial deny

### Slice C — Persistence + Alembic `0020`

### Slice D — OpenAPI / 状态机 / PostgreSQL / 七步自审

## 5. Exit Criteria

1. 无签名不可发布。  
2. 未批准不可发布。  
3. 撤销后不可新获取。  
4. 能力声明必填。  
5. 商业政策 API 失败关闭。  
6. OpenAPI / Migration / Code 一致；回归通过。  
7. **不宣称** 定价/账单/争议已交付。

## 6. Explicit Defer

定价、分成、计量单价、账单、税务、支付、争议裁决、Extension 沙箱执行引擎
