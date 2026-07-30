# PHX-G75 OIDC Refresh KMS Key Provider Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0094  
**人工确认：** 支付清算另批  

## 1. 门禁目标

启用 `provider=kms`；`http|aws|gcp|azure` 薄后端；云 SDK 可选；默认不引入重依赖。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Provider | `kms`（G74 的 Foundation 硬拒绝解除） |
| Backend | `EAOS_OIDC_REFRESH_KMS_BACKEND` |
| 可测路径 | http + 注入 fetcher |
| Status | `refresh_encrypt_kms_backend` |

## 3. Exit Criteria

1. ADR-0094 Accepted。  
2. http 可测；aws/gcp/azure 无 SDK fail-closed；注入路径绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G75_ACCEPTANCE.md](PHX-G75_ACCEPTANCE.md)。
