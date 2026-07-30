# PHX-G144 Foundation 0.2.1 Release Train Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Release Engineering / Phoenix Foundation  
**退出门禁：** 包 `0.2.1`；Alembic `0029`；fail-closed 持有；无新 schema  
**授权：** DAL-G003 Eng `1`；Usage **DAL-U005**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0163 + Architecture Gate |
| B | 版本 bump：pyproject / SDK / Manifest / Helm Chart+values / release docs / `GET /v1/release` |
| C | PROJECT_STATUS / CHANGELOG / ROADMAP / TASKS / DAL-U005 |
| D | `test_release_g144.py` + R17/G76/G51 合约对齐 `0.2.1` |

## 2. 核心不变量

- 不修改 Constitution BOOK / Blueprint / Kernel 执行语义 / Runtime 执行权  
- 不打开 Twin authorize / Brain execute / 支付清算 / Role→grant / WebAuthn 产品页  
- 无新 Alembic；head 仍 `0029_eaos_declared_roles_g90`  
- 兼容：additive-only patch

## 3. 自动化证据

- 契约：`tests/contracts/test_release_g144.py`  
- 回归：`test_release_r17.py` · `test_api_gateway_g76_deploy_region.py` · `test_ops_g51.py` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0163 |
| Constitution Review | 通过；无 BOOK 编辑；fail-closed 持有 |
| Cross-reference Review | 通过；Manifest / DAL / status 同步 |
| Documentation Review | 通过；release docs Version → `0.2.1`；历史 `0.2.0` 保留 |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Eng 下一可选 WebAuthn（`2`）；支付清算（`4`）暂缓 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Full WebAuthn / MFA registration product page（Eng `2`）  
- Role→grant 自动写入（Eng `3`）  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 新 Alembic（除非后续编号切片）  

## 6. 证据索引

- [PHX-G144 Architecture Gate](PHX-G144_ARCHITECTURE_GATE.md)  
- [ADR-0163](../decisions/ADR-0163-foundation-0-2-1-release-train.md)  
- [RELEASE_MANIFEST.yaml](../release/RELEASE_MANIFEST.yaml)  
- [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md)（DAL-U005）  
- [test_release_g144.py](../../tests/contracts/test_release_g144.py)  
