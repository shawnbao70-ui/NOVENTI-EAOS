# History / 审计轨迹观察 — Legacy Knowledge

**Evidence strength:** Strong（表形、读取与部分对象日志）/ Weak（写入覆盖与关联）/ Missing（不可篡改、完整保留和统一对象审计）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件只描述 Customer360/Sample360 邻接的 history、timeline、sample log 与通用 Audit Center 表象。它不把 Legacy 的多类日志合并成同一语义，也不形成 EAOS Audit 设计定论。

Legacy 中至少存在四类不同事物：

1. 读取当前对象及关联集合的 `history` facade。
2. 页面临时拼装的 Timeline。
3. `sample_logs` 这类对象附属动作记录。
4. `audit_logs`、`security_audit_logs`、`operation_logs` 等平台/安全记录。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 证据强度 |
|---|---|---|
| HISTORY-AUDIT-RULE-001 | `customer_360()` history facade 返回客户及跟进、报价、订单、收款、样品集合 | Strong |
| HISTORY-AUDIT-RULE-002 | 该 facade 是当前数据装配，不是客户字段版本历史 | Strong negative |
| HISTORY-AUDIT-RULE-003 | `sample_history()` 只返回当前样品；supplier history 也为同类 scaffold | Strong negative |
| HISTORY-AUDIT-RULE-004 | 报价 history 明确装配 quote versions；这是少数有版本集合的对象证据，不能外推至客户/样品 | Strong |
| HISTORY-AUDIT-RULE-005 | Customer360 Timeline 由跟进、报价、销售订单展示拼接，无统一事件表和全局时间排序 | Strong |
| HISTORY-AUDIT-RULE-006 | Sample 表定义 `sample_logs(sample_id, action, remark, operator, created_at)`，可表达对象动作记录 | Strong |
| HISTORY-AUDIT-RULE-007 | `create_sample_log` helper 支持 tenant-aware 写入及旧 schema 回退，但未找到业务调用点 | Strong negative |
| HISTORY-AUDIT-RULE-008 | 当前 Sample360 service 未查询 `sample_logs`，template Timeline 因而不能证明日志已展示 | Strong negative |
| HISTORY-AUDIT-RULE-009 | 通用 `audit_logs` 可记录 module、operation、object、username、IP、result、remark、time | Strong（模型） |
| HISTORY-AUDIT-RULE-010 | Audit Center 页面/API 可读取日志、统计和 health；另有 security 与 operation log 表面 | Strong |
| HISTORY-AUDIT-RULE-011 | 通用 `add_audit_log` helper 未找到业务调用点；不能证明客户/样品 CRUD 被完整捕获 | Strong negative |
| HISTORY-AUDIT-RULE-012 | V15.1 Audit Center registry/event/log/report 记录多为 `implemented=0` / metadata，且遇到 V14 audit_logs 会避免写入 catalog row | Strong |
| HISTORY-AUDIT-RULE-013 | 审计日志存在 cleanup(默认 365 日)和以 remark 标记 Archived 的函数 | Strong（函数） |
| HISTORY-AUDIT-RULE-014 | scheduler 是否实际周期调用、归档是否外移、删除前是否留存为 `UNKNOWN` | Missing |
| HISTORY-AUDIT-RULE-015 | 防篡改、签名/哈希、WORM、访问审计、字段脱敏、法定留存及跨租户导出为 `UNKNOWN` | Missing |
| HISTORY-AUDIT-RULE-016 | Customer 新增在注入 `write_log` 时写 operation log；Update、Delete 和新增 follow-up 未见对称写入 | Strong / Strong negative |
| HISTORY-AUDIT-RULE-017 | `customers` 主表未见 created/updated/by 字段；当前 customer status 不构成状态变更历史 | Strong |
| HISTORY-AUDIT-RULE-018 | Enterprise Timeline engine 与 Customer360 timeline bridge 仍 defer to Legacy；统一 timeline 属架构/scaffold | Strong |
| HISTORY-AUDIT-RULE-019 | V15.1 Audit Center 默认未启用，registry/event/log 多标 `implemented=false`，不替换 Legacy operation log | Strong |

## 3. 流程

### 3.1 对象详情 history/timeline

1. history facade 按对象 id 读取当前对象。
2. Customer history 额外读取多个关联集合；Sample history 不读取动作日志。
3. Customer360 页面把部分集合依序渲染成 Timeline。
4. 这些读取不生成不可变事件，也不保留字段 before/after。

### 3.2 Sample log

设计上：业务动作调用 helper → 写入 sample id、action、remark、operator、tenant（若列存在）→ commit → Sample360 查询并展示。  
运行证据：helper 和表存在，但未找到调用点，且当前 Sample360 context 未读取 logs；闭环为 `UNKNOWN`。

### 3.3 客户操作日志

客户新增可通过注入的 `write_log` 记录 Customer/Add；客户更新、删除和新增跟进未找到同等写入。该记录是模块操作日志，不是字段 before/after 或 Customer360 timeline 事件。

### 3.4 通用审计

设计上：业务动作调用 `add_audit_log` → Audit Center 按 id 倒序读取 → dashboard/statistics 汇总 → cleanup/archive 维护。  
运行证据：表、helper、页面与维护函数存在；客户/样品关键写入是否调用及 scheduler 是否启用为 `UNKNOWN`。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| HISTORY-AUDIT-VAL-001 | Sample log 关联有效样品 | 缺失 | 未见外键或 helper 存在性检查 |
| HISTORY-AUDIT-VAL-002 | Sample log tenant 写入 | 弱 | 有 tenant-aware 尝试，但旧 schema 会回退 |
| HISTORY-AUDIT-VAL-003 | Audit log 必填对象、用户与结果 | 弱 | helper 参数存在，数据库约束未证 |
| HISTORY-AUDIT-VAL-004 | 审计查看权限 | 不一致 | security audit 页面有 permission check；普通 audit 页面未见同等门禁 |
| HISTORY-AUDIT-VAL-005 | 写入失败不得影响业务事务 | `UNKNOWN` | 未证统一事务策略 |
| HISTORY-AUDIT-VAL-006 | 日志顺序 | 弱 | 多数按自增 id 倒序，不等于业务事件时间 |
| HISTORY-AUDIT-VAL-007 | old/new value 完整捕获 | 缺失 | security schema 有字段，通用 audit 模型未统一使用 |
| HISTORY-AUDIT-VAL-008 | 防修改、防删除、链式完整性 | 缺失 | 存在直接 UPDATE/DELETE 维护函数 |
| HISTORY-AUDIT-VAL-009 | Customer 写操作审计对称性 | 缺失 | 仅新增找到 write_log，Update/Delete/follow-up 未见 |
| HISTORY-AUDIT-VAL-010 | Object360 时间字段与 Legacy 数据对齐 | 缺失 | architecture optional 字段不证明源表有值 |

## 5. 数据含义

| 数据 | 业务含义/限制 |
|---|---|
| `history` facade | 对象当前快照或关联集合装配；名称不保证版本历史 |
| Customer360 Timeline | 页面投影，供查看客户活动和商业单据 |
| `sample_logs.action` | 样品动作标签；正式词汇未集中定义 |
| `sample_logs.remark` | 动作补充说明 |
| `sample_logs.operator` | 写入方提供的操作者文本，默认可为 System |
| `audit_logs` | 通用模块/操作/对象级日志模型 |
| `security_audit_logs` | 含 old/new value、IP、设备/结果等安全操作表象 |
| `operation_logs` | 较轻量的 username/module/action 记录 |
| `audit_history` | Audit Center 自身 metadata/history 记录，不等于所有业务对象审计 |
| Archived | 写入 remark 的标签；未证明外部归档介质 |
| `customers.customer_status` | 客户当前 pipeline 标签；没有已证 status-history 表 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Success | 通用 add-audit helper 的默认 result |
| Active | V14 audit rule 状态 |
| metadata_only | V15.1 audit catalog/rule 表象 |
| completed | Audit Center history 默认状态 |
| Archived | audit log remark 标记，不是不可变归档保证 |
| created / updated / deleted | 可作为事件词汇，但客户/样品覆盖为 `UNKNOWN` |
| Customer/Sample 统一审计状态 | `UNKNOWN`；未见对象级审计状态机 |
| 开发中 / 跟进中 / 已成交 / 长期客户 | 客户当前 pipeline 词汇，不是 history 事件状态 |
| draft / active / archived | Enterprise Object360 架构词汇，不是 Legacy CRM 审计状态 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\runtime.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\runtime.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\utils.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\audit_center\audit_api.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\audit_center\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\audit_center\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_audit_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\audit\types.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\timeline\timeline_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\customer\timeline_bridge.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_integration.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\customer_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\audit_logs.html`
