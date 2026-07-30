# ADR-0031 — Marketplace 技术边界（商业政策延后）

**状态：** Accepted（技术边界）  
**日期：** 2026-07-18  
**里程碑：** PHX-M16  
**归属：** Shared Platform Capability / Marketplace  
**人工批准范围：** 用户指示「继续」批准启动技术骨架；**定价、分成、账单细则与争议裁决政策仍未批准，禁止写入实现。**

## 背景

BOOK08 要求市场包签名、声明能力、可审计安装/回滚/撤销，并明确商业条款变更需人类批准。PHX-B14 已提供 Package Manifest；PHX-M16 需固定分发治理而不抢跑商业模式。

## 决策

### 1. Ownership 与落点

- Marketplace Platform：`eaos_platform.marketplace`
- 消费 `eaos_platform.package` 契约；不分叉 Kernel
- 不实现计费引擎、分成账本或法务争议裁决器

### 2. 技术生命周期

```text
draft → submitted → approved|rejected → published → revoked
```

- 发布前必须具备 `signature_ref` 与能力声明（permissions / events / data_scope）
- 租户 `AcquireListing` 产生技术获取记录（非购买合同）
- `RevokeListing` 阻断新获取；已获取需可审计

### 3. 商业政策失败关闭

以下调用恒返回 `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`：

- `set_pricing` / `create_invoice` / `open_dispute` / `set_revenue_share`

### 4. 与 Package Platform

- Listing 绑定 `package_key` + `version`
- 获取后仍须经 Package Platform 安装治理；Marketplace 不绕过 Permission

## Explicit Defer（待另一次人工批准）

- 定价模型、货币、试用、优惠
- 分成比例、计量单价、账单与税务
- 争议解决流程与法律责任归属
- 支付网关、Sandbox 执行引擎产品化

## 关联

- [ADR-0029-business-package-platform.md](ADR-0029-business-package-platform.md)
- [../constitution/BOOK08.md](../constitution/BOOK08.md)
- [../project/PHX-M16_ARCHITECTURE_GATE.md](../project/PHX-M16_ARCHITECTURE_GATE.md)
