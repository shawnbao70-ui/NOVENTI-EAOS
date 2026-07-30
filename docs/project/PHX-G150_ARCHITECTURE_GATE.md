# PHX-G150 Autonomous Execution Directive Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation；docs-only）  
**归属：** Phoenix Governance / Dual-Track Operating Directive  
**规范源：** ADR-0169  
**授权：** DAL-G003 + DAL-G004（DAL-U012）

## 1. 门禁目标

将修订后的 Autonomous Execution Directive（AED v1.1）形式化为 Dual-Track **operating directive**：HARD HOLDS、Explicit Defer 规则、价值平局、Research 默认产出、加深优先序、强制 milestone report + DAL Usage Log。**不**打开任何产品面。包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Docs-only governance formalization |
| Normative text | `AUTONOMOUS_EXECUTION_DIRECTIVE.md` v1.1 |
| Binding ADR | ADR-0169 Accepted |
| Grant | DAL-G004 Active（works with G003）；Usage DAL-U012 |
| 「继续」语义 | Highest-value selection under HARD HOLDS — not sequence invent |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | 支付清算；Brain execute；Twin authorize；AR Board 自证；Const/BP rewrite；新代码路径；新 Alembic |

## 3. Exit Criteria

1. ADR-0169 Accepted；AED v1.1 published.  
2. Gate / Acceptance + DAL-G004 / DAL-U012 + Dual-Track / tip boards / PROJECT_STATUS / CHANGELOG / ROADMAP 同步.  
3. `test_docs_g150_autonomous_execution_directive.py` 与 DAL 合约绿.  

见 [PHX-G150_ACCEPTANCE.md](PHX-G150_ACCEPTANCE.md)。
