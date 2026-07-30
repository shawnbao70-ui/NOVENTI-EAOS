# PHX-G169 Signed Extension Host Productization Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal Extensions  
**规范源：** ADR-0188  
**授权：** DAL-G003 + DAL-G004（DAL-U042）

## 1. 门禁目标

将 signed extension host 产品化为 Hydrate → Mount → Invoke 垂直切片，承接 G168 demo seed，且不打开 Marketplace 任意脚本。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Entry | Hydrate from list + bootstrap id/key |
| Auto | Boot after bootstrap；Extensions tab switch |
| Sandbox | First-party iframe/Worker + CSP only |
| Marketplace arbitrary script | Closed |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

1. ADR-0188 Accepted。  
2. UI hydrate + status + tests + DAL-U042 + tip/status 齐。  
3. `test_api_gateway_g169_*` 绿。  
