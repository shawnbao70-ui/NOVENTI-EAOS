# 信用特权绕过、告警与权限缺口

## Scope与证据强度

本页区分正式 credit override、全局 RBAC 特权、局部 Human Approved、UI-only warning 和无守卫变更入口。结论是未发现正式信用例外实体；现有审批结构均未接入信用 gate。

## 业务规则（稳定ID）

1. **OB-R01** 未找到 credit_override、credit_exception 或 credit_bypass 表/API。
2. **OB-R02** 未找到客户 Credit Hold/freeze/blacklist 执行实体。
3. **OB-R03** quote_approval 保存报价审批记录，但不阻断 Convert。
4. **OB-R04** approval_records/Approval Center 未连接 Quote/SO/DO 信用门禁。
5. **OB-R05** V18 Quote/SO Human Approved 只校验单据状态、行项和确认。
6. **OB-R06** Admin/Super Admin 在 has_permission 中全局返回 True。
7. **OB-R07** Admin 特权是 RBAC bypass，不是有理由、有额度、有审计的 credit override。
8. **OB-R08** Manager 不是 privileged role。
9. **OB-R09** Manager/Admin 可扩大 Customer/SO 列表可见性，但不获得专门信用例外。
10. **OB-R10** Customer balance 风险带只显示 warning。
11. **OB-R11** 10k/30k/100k 阈值不一致，且均不阻断交易。
12. **OB-R12** AI credit_score/credit_risk 是硬编码或未实现元数据。
13. **OB-R13** Convert SO 为 GET mutation，路由无服务端 has_permission。
14. **OB-R14** Quote status 可通过 GET 路由变更且无权限检查。
15. **OB-R15** Create DO 为 GET mutation，路由无服务端 has_permission。
16. **OB-R16** SO status 非 Open 更新虽有 Sales edit，但仍无信用检查。
17. **OB-R17** Approval approve/reject GET 路由未读取 can_approve。
18. **OB-R18** approve_expense GET 路由以 BOSS 硬编码审批人。
19. **OB-R19** Customer detail、followup、部分风险 AI 入口缺对象级权限。
20. **OB-R20** IP blacklist 属于安全域，不得解释为客户信用黑名单。
21. **OB-R21** 删除客户的级联硬删绕开了归档/冻结语义。
22. **OB-R22** duplicate legacy handlers 扩大了未守卫路径的不确定性。
23. **OB-R23** 知道 URL 的已登录用户可能绕开只在模板执行的按钮隐藏。
24. **OB-R24** Legacy 没有 override reason、requested_by、approved_by、expiry 或 audit 链。

## 流程

1. Customer360/AR 页面以余额阈值显示 warning。
2. 用户仍可进入 Quote/Convert/Create DO 链路。
3. UI 按钮可能按 RBAC 隐藏，但部分变更路由不二次校验。
4. Admin/Super Admin 对受守卫路由拥有全局权限 bypass。
5. Quote/SO Human Approved 只确认局部状态动作。
6. quote_approval/Approval Center 不参与信用判定。
7. 所以 Legacy 只有「提示后继续」与权限缺口，不存在正式信用 override 流程。

## 校验（强/弱/缺失）

1. **OB-V01（强）** 受守卫路由调用 has_permission。
2. **OB-V02（强/特权）** Admin/Super Admin 绕过全部 RBAC。
3. **OB-V03（缺失）** Manager credit override 权限不存在。
4. **OB-V04（缺失）** 无 balance>credit_limit 服务端比较。
5. **OB-V05（缺失）** 无 overdue 阻断和例外审批。
6. **OB-V06（强/局部）** Quote Approve 要求 human_confirm。
7. **OB-V07（强/局部）** SO Approve 要求 human_confirm。
8. **OB-V08（缺失）** Convert SO 路由无 RBAC。
9. **OB-V09（缺失）** Quote status GET 无 RBAC/审批联动。
10. **OB-V10（缺失）** Create DO 路由无 RBAC。
11. **OB-V11（缺失）** Approval GET mutation 无 can_approve。
12. **OB-V12（缺失）** override 无理由、金额、到期和撤销校验。
13. **OB-V13（缺失）** warning 阈值不统一。
14. **OB-V14（缺失）** customer_status 不阻断交易。
15. **OB-V15（弱/UI）** 模板可隐藏 Convert/Create DO 按钮。
16. **OB-V16（缺失）** quote_id 防重复为先查后写，无数据库唯一性证明。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| privileged role | Admin/Super Admin 全局 RBAC bypass |
| Manager | 普通 RBAC 角色，部分列表看全量 |
| `role_permissions.can_approve` | 审批动作位，部分 GET 路由未读取 |
| `quote_approval` | 报价审批记录，不是信用例外 |
| `approval_records` | 通用审批记录，不是信用例外 |
| `human_confirm` | 不可逆动作人工确认 |
| Customer balance | UI 风险启发式输入 |
| Credit Watch | warning，不是 hold |
| A/B/C/D band | 按销售额展示 |
| `credit_score=100` | AI/演示占位 |
| `credit_risk implemented=False` | 未实现元数据 |
| `customer_status` | 生命周期标签 |
| `ip_blacklist` | IP 安全封禁 |
| `quote_id` | Convert 来源和顺序幂等 |
| GET mutation | 读取式 HTTP 外观下的状态变更 |
| UI permission | 按钮可见性，不等于服务端授权 |
| override reason/expiry | 未建模 |
| audit trail | 信用例外域未建模 |

## 状态词汇

| 词汇 | 执行含义 |
|---|---|
| Pending/Approved/Rejected | 通用/报价审批态 |
| Draft/Sent | Quote Human Approved 态 |
| Pending/Open | SO Human Approved 态 |
| Credit Watch | 告警-only |
| Credit Hold/Override | 未实现 |
| Admin/Super Admin | 权限特权角色 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| OB-E01 | privileged roles 无条件通过权限 | 强 | `core/permission/checker.py`、`module_catalog.py` |
| OB-E02 | Manager 仅扩展数据可见性 | 强 | `apps/customer/services.py`、`apps/sales/services.py` |
| OB-E03 | Credit tab 为 UI 阈值 warning | 强 | `templates/customer_detail.html` |
| OB-E04 | Convert SO 无 has_permission/信用检 | 强 | `apps/sales/router.py`、`services.py` |
| OB-E05 | Quote status GET 无守卫 | 强 | `apps/quotation/router.py` |
| OB-E06 | Create DO GET 无守卫 | 强 | `apps/sales/router.py` |
| OB-E07 | Approval GET approve/reject 无 can_approve | 强 | `apps/approval/router.py` |
| OB-E08 | approve_expense 硬编码 BOSS | 强 | `apps/finance/router.py` |
| OB-E09 | quote_approval DDL存在但无信用联动 | 强 | `runtime/v14/legacy_support.py`、`apps/quotation/utils.py` |
| OB-E10 | AI credit_risk 未实现 | 强 | `core/ai_decision/risk.py` |
| OB-E11 | A-015 将 credit 定义为启发式 | 强 | `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` |
| OB-E12 | business_modules 无 credit override 规范 | 强（缺失证据） | `business_modules/crm.md`、`sales.md`、`approval.md` |

## UNKNOWN + 已查路径

1. **外部分支是否有 credit override 实体 UNKNOWN。** 已查路径：当前全库 py/sql/md、schema、business_modules。
2. **生产 role_permissions 中 Manager 默认 can_approve 值 UNKNOWN。** 已查路径：种子、permission schema；未读 live DB。
3. **quote_approval 是否由隐藏 UI 触发 UNKNOWN。** 已查路径：Quotation apps/templates、函数引用。
4. **Approval Center 是否有部署时插件联动 Convert UNKNOWN。** 已查路径：Approval router/service、bootstrap、hooks。
5. **全局 middleware 是否保护所有 GET mutation UNKNOWN。** 已查路径：security middleware、route registration。
6. **重复 convert/create_do handler 的真实优先级 UNKNOWN。** 已查路径：residual、router、bootstrap。
7. **PostgreSQL 部署是否另有信用约束 UNKNOWN。** 已查路径：migration/schema/docs。
8. **移动/PWA 是否另有 Convert 入口 UNKNOWN。** 已查路径：ui_center、mobile、templates。
9. **客户风险 AI 的完整数据源与权限 UNKNOWN。** 已查路径：Customer router/runtime。
10. **离线口头批准是否是实际信用 override UNKNOWN。** 已查路径：reports、business_modules、Approval records。
11. **管理员绕过是否有统一审计日志 UNKNOWN。** 已查路径：permission checker、audit、activity logs。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\approval\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
