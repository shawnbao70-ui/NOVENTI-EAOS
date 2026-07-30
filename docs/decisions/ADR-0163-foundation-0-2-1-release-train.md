# ADR-0163 — Foundation 0.2.1 Release Train

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G144  
**归属：** Release Engineering / Phoenix Foundation  
**授权：** DAL-G003 Eng Explicit Defer item `1`（DAL-U005）

## 背景

Phoenix Foundation 包基线停在 `0.2.0`（PHX-R17）。此后 PHX-G18…G143 已 Fully Accepted（含 Dual-Track ADR-0162），但发布清单与包版本未滚动。工程需一次 **patch** 发布列车将已接受切片纳入基线标识，且不打开支付清算、Role→grant、WebAuthn 产品页、Brain execute、Twin authorize，亦无新 Alembic。

## 决策

### 1. 发布列车边界（patch）

- 产品基线名称不变：`EAOS Phoenix Foundation`
- 包版本：`noventi-eaos==0.2.1`（与 `eaos_sdk.__version__`、Release Manifest、Helm chart/appVersion/image.tag、`GET /v1/release` 对齐）
- Alembic head **保持** `0029_eaos_declared_roles_g90`（本列车无 schema 变更）
- 兼容策略仍为 **additive-only**（见 `docs/release/COMPATIBILITY.md`）
- 先前 Foundation 基线 `0.2.0`（PHX-R17）保留为历史引用；本切片为 patch 滚动

### 2. 纳入基线的已接受切片

- **In：** PHX-G18…PHX-G143（含 R17 列车产物与后续 Gateway / Terminal / OpenAPI / Dual-Track 治理）一并视为 `0.2.1` Fully Accepted Foundation 基线内容
- Manifest milestones 增补 `PHX-G143`、`PHX-G144` 为 `fully_accepted`；既有 `PHX-R17` 仍 `fully_accepted`

### 3. Explicit Out（本列车不开口）

- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page（Eng Explicit Defer `2`）  
- Brain execute  
- Twin authorize  
- 新 Alembic revision（除非后续编号切片另批）  
- 多区域生产 SaaS / failover（非目标）

### 4. 运营与契约

- 更新 `RELEASE_MANIFEST.yaml`、`COMPATIBILITY.md`、Runbook / Checklist / Compose / Helm / Topology 等当前 Version 与 `/v1/release` 示例为 `0.2.1`
- 契约：`tests/contracts/test_release_g144.py`；既有 R17 / G76 / G51 合约跟进当前包版本

## 后果

- 生产真相包版本为 `0.2.1`；fail-closed 持有不变  
- Eng 下一可选项：WebAuthn 产品页（`2`）、Role→grant（`3`）；支付清算（`4`）仍暂缓  
- 不修改 Constitution BOOK、Blueprint、Kernel 语义、Runtime 执行权

## 关联

- [../project/PHX-G144_ARCHITECTURE_GATE.md](../project/PHX-G144_ARCHITECTURE_GATE.md)  
- [../project/PHX-G144_ACCEPTANCE.md](../project/PHX-G144_ACCEPTANCE.md)  
- [ADR-0032-release-train-boundary.md](ADR-0032-release-train-boundary.md)  
- [../release/RELEASE_MANIFEST.yaml](../release/RELEASE_MANIFEST.yaml)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
