# ADR-0054 — Marketplace Commercial Policy (Foundation v1)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-M17  
**归属：** Marketplace Platform  
**人工批准：** 2026-07-18 批准启动商业产品化；2026-07-19「继续」固化 Foundation 默认政策并实现

## 背景

ADR-0031 将定价/账单/分成/争议恒 fail-closed。M17 须书面固定政策后开放受治理实现；支付网关与法务终局裁决仍不在本切片。

## Foundation 默认政策（v1）

| 政策项 | 裁决 |
|--------|------|
| 计价模型 | **固定单价（fixed）**；币种 ISO 4217，默认 `CNY`；金额非负十进制（最多 2 位小数） |
| 分成 | **平台 `platform_share_bps` 默认 2000（20%）**；发布方得剩余；允许范围 **0–5000**（平台不超过 50%） |
| 账单周期 | **immediate**：`create_invoice` 按当前定价即时开立 `issued` 发票；不接支付清算 |
| 争议裁决 | **发布方租户内裁决**：`open_dispute` 记审计事实；`resolve_dispute` 仅同租户可结案并强制审计。外部法务/仲裁延后 |
| Acquire | 技术获取 **≠** 购买合同；发票/争议不改变 Acquire 语义 |

## 决策

1. 商业 API 按上表实现；超出范围（订阅计量、支付扣款、跨法域终局）仍返回 `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`。  
2. 商业状态持久化于 Marketplace 仓储；Gateway 仅薄适配。  
3. Kernel 不宿主计费引擎或法务裁决器。

## Explicit Defer

- 支付网关 / 退款自动清算  
- 订阅与用量计量  
- 税务、优惠、试用  
- 平台面 Governor 强制改判、外部仲裁对接  
- JWKS 无关本 ADR

## 关联

- [ADR-0031-marketplace-technical-boundary.md](ADR-0031-marketplace-technical-boundary.md)
- [../project/PHX-M17_ARCHITECTURE_GATE.md](../project/PHX-M17_ARCHITECTURE_GATE.md)
- [../constitution/BOOK08.md](../constitution/BOOK08.md)
