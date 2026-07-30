# PHX-M17 Marketplace Commercial Policy Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation 政策 v1）  
**归属：** Marketplace Platform  
**人工批准：** 2026-07-18 启动商业产品化；2026-07-19「继续」固化默认政策并实现  
**规范源：** ADR-0054  

## 1. 门禁目标

在 M16 技术骨架上开放定价 / 账单 / 分成 / 争议的受治理实现路径。

## 2. 已固化政策输入（Foundation v1）

| 项 | 裁决 |
|----|------|
| 计价 | 固定单价；币种默认 CNY |
| 分成 | 平台 0–5000 bps（默认 2000） |
| 账单 | immediate 开立 issued 发票 |
| 争议 | 发布方租户裁决 + 强制审计 |

## 3. Exit Criteria

1. ADR-0054 Accepted。  
2. 商业 API 按政策实现；延后项仍 fail-closed。  
3. Acquire ≠ 购买合同。  
4. 契约绿；Alembic `0022_marketplace_m17_commercial`。

## 4. Explicit Defer

支付网关、订阅计量、税务优惠、外部仲裁、平台面强制改判
