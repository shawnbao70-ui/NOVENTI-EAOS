# PHX-G144 Foundation 0.2.1 Release Train Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Release Engineering / Phoenix Foundation  
**规范源：** ADR-0163  
**授权：** DAL-G003 Eng Explicit Defer `1`（DAL-U005）

## 1. 门禁目标

将已接受的 Foundation 切片（G18–G143）滚动进包基线 `0.2.1`；Alembic 仍 `0029`；**不**打开支付清算、Role→grant、WebAuthn 产品页、Brain execute、Twin authorize；**无**新 schema。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Train kind | Patch release train（SemVer `0.2.0` → `0.2.1`） |
| Compatibility | Additive-only；破坏性变更需主版本 |
| In baseline | G18–G143 accepted work + R17 train artifacts |
| Package / Manifest / Helm / SDK / `GET /v1/release` | `0.2.1` |
| Alembic | Head stays `0029_eaos_declared_roles_g90` |
| Out | 支付清算；Role→grant；WebAuthn 产品页（Eng `2`）；Brain execute；Twin authorize；新 Alembic（除非后续另批） |

## 3. Exit Criteria

1. ADR-0163 Accepted。  
2. Gate / Acceptance + Manifest / pyproject / SDK / Helm / release docs + status sync 齐。  
3. `test_release_g144.py` 与相关 R17/G76/G51 合约绿。  

见 [PHX-G144_ACCEPTANCE.md](PHX-G144_ACCEPTANCE.md)。
