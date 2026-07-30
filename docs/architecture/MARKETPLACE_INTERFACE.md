# Marketplace 接口规格（技术骨架）

**文档 ID：** IF-MKT-001  
**版本：** 1.0  
**阶段：** PHX-M16  
**状态：** Technical Foundation Accepted；商业政策门禁仍开放  
**仓库：** `NOVENTI-EAOS`

## 目的

细化 Listing / Signature / Review / Publish / Revoke / Acquire，确保签名与审核治理，且商业 API 失败关闭。

## 不变式

1. 落点 `eaos_platform.marketplace`  
2. 能力声明必填；`kernel.*` 包键拒绝  
3. 无签名不可提交/发布  
4. 未批准不可发布；撤销后不可新获取  
5. Acquire ≠ 购买合同  
6. 定价/账单/争议/分成 → Foundation 政策（ADR-0054）；支付清算等仍 `MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`

## 关联

- [MARKETPLACE_STATE_MACHINES.md](MARKETPLACE_STATE_MACHINES.md)
- [../api/marketplace.openapi.yaml](../api/marketplace.openapi.yaml)
- [../decisions/ADR-0031-marketplace-technical-boundary.md](../decisions/ADR-0031-marketplace-technical-boundary.md)
