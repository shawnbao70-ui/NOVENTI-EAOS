# 任务列表

**仓库：** `NOVENTI-EAOS`  
**最后更新：** 2026-07-18

---

## 本轮完成（开始实现）

| ID | 任务 | 状态 |
|----|------|------|
| T-0035 | ADR-0010 内存仓储 Foundation 切片 | 完成 |
| T-0036 | `kernel/shared` 上下文/错误码/结果/审计 | 完成 |
| T-0037 | Identity 最小垂直切片 | 完成 |
| T-0038 | 契约测试并通过 pytest | 完成 |
| T-0039 | pyproject.toml 工程脚手架 | 完成 |
| T-0040 | Organization 最小垂直切片 | 完成 |
| T-0041 | Permission.Evaluate 最小垂直切片 | 完成 |
| T-0042 | Organization / Permission 契约测试（31 passed） | 完成 |
| T-0043 | 清理构建产物并添加 `.gitignore` | 完成 |
| T-0044 | Workflow 最小垂直切片 | 完成 |
| T-0045 | Organization ↔ Permission 集成契约 | 完成 |
| T-0046 | AI 人工审批闸门（主体/动作/资源绑定） | 完成 |
| T-0047 | 完整契约测试（42 passed） | 完成 |
| T-0048 | Event Bus 最小信封切片 | 完成 |
| T-0049 | Event 发布/订阅/重放/租户隔离契约 | 完成 |
| T-0050 | Event payload 深度冻结与 JSON 安全约束 | 完成 |
| T-0051 | 完整契约测试（51 passed） | 完成 |
| T-0052 | Workflow 幂等信号/定义版本设计 | 完成 |
| T-0053 | Event 持久化/投递保证/死信 ADR | 完成 |
| T-0054 | 完整契约测试（54 passed） | 完成 |
| T-0055 | DB/ORM 选型 ADR（PostgreSQL/SQLAlchemy/Alembic） | 完成 |
| T-0056 | Kernel Repository / Unit of Work Protocol | 完成 |
| T-0057 | 持久化端口契约测试（63 passed） | 完成 |
| T-0058 | SQLAlchemy metadata 与 Alembic baseline | 完成 |
| T-0059 | SQL Foundation 契约测试（69 passed） | 完成 |
| T-0060 | Shared Audit / Identity SQLAlchemy 映射与迁移 | 完成 |
| T-0061 | ORM / 离线迁移契约测试（77 passed） | 完成 |
| T-0062 | SQLAlchemy Unit of Work | 完成 |
| T-0063 | SQLAlchemy UoW 契约测试（83 passed） | 完成 |
| T-0064 | Shared Audit / Identity SQLAlchemy Repository | 完成 |
| T-0065 | SQL Repository 隔离契约测试（89 passed） | 完成 |
| T-0066 | UoW Repository 注入与 Identity command 事务接线 | 完成 |
| T-0067 | Transactional Identity 契约测试（96 passed） | 完成 |
| T-0068 | 受保护 PostgreSQL 集成测试套件 | 完成 |
| T-0070 | Platform Identity Governor 显式授权 | 完成 |
| T-0071 | Identity Governor 契约测试（98 passed） | 完成 |
| T-0072 | Organization SQLAlchemy 持久化切片 | 完成 |
| T-0073 | Transactional Organization 契约测试（103 passed） | 完成 |
| T-0074 | Permission SQLAlchemy 持久化切片 | 完成 |
| T-0075 | Transactional Permission 契约测试（108 passed） | 完成 |
| T-0076 | Workflow SQLAlchemy 持久化切片 | 完成 |
| T-0077 | Transactional Workflow 契约测试（112 passed） | 完成 |
| T-0078 | Event SQLAlchemy 持久化切片 | 完成 |
| T-0079 | Transactional Event Bus 契约测试（116 passed） | 完成 |
| T-0081 | Transactional Workflow W-04/W-05 AI 审批验收 | 完成 |
| T-0082 | Transactional Organization ↔ Permission L2 契约 | 完成 |
| T-0083 | 扩展五域 + Event PostgreSQL 集成套件 | 完成 |
| T-0069 | 真实 PostgreSQL 迁移与 Repository 契约执行 | 完成（123 passed） |
| T-0084 | 修复 Workflow / Event PostgreSQL 父子写入顺序 | 完成 |
| T-0080 | PHX-004 持久化验收收敛 | 完成（人工批准） |
| T-0085 | ADR-0013 Runtime Foundation 边界 | 完成 |
| T-0086 | Runtime 接口与契约测试计划 | 完成 |
| T-0087 | Runtime 上下文构造/传播/快照 | 完成 |
| T-0088 | Runtime Executor 与 Observability Binding | 完成 |
| T-0089 | Runtime Foundation 契约与完整回归（138 passed） | 完成 |
| T-0090 | PHX-005 Foundation 里程碑确认 | 完成（人工批准） |
| T-0091 | ADR-0014 Identity Session Validation | 完成 |
| T-0092 | Identity.ValidateSession 内存/事务实现 | 完成 |
| T-0093 | Runtime 强制 SessionValidator | 完成 |
| T-0094 | Session 内存/SQLite/PostgreSQL 契约（143 passed） | 完成 |
| T-0095 | Credential revoke / validate 与 CreateSession 绑定 | 完成 |
| T-0097 | Alembic `0007` Session Credential Binding | 完成 |
| T-0098 | Credential 生命周期完整回归（146 passed） | 完成 |
| T-0096 | Platform Identity Governor 持久化 ADR | 完成 |
| T-0099 | Governor ORM / Repository / Alembic `0008` | 完成 |
| T-0100 | Bootstrap / 撤销 / PostgreSQL Governor 契约（148 passed） | 完成 |
| T-0101 | AI 多租户派驻与 INHERIT 语义 ADR | 完成 |
| T-0102 | 全局 active 唯一、INHERIT 谱系与 ARCHIVE 契约 | 完成 |
| T-0103 | Alembic `0009` AI Assignment Semantics | 完成 |
| T-0104 | AI profile / owner policy 持久化 | 完成 |
| T-0105 | Governor-only Profile 乐观锁契约 | 完成 |
| T-0106 | Alembic `0010` AI Employee Profiles | 完成 |
| T-0107 | Identity ↔ Organization L2 契约 | 完成 |
| T-0108 | Membership Eligibility Port 与失败关闭 | 完成 |
| T-0109 | AI 改派 membership 共享事务协调器 | 完成 |
| T-0110 | Identity OpenAPI 3.1 IDL | 完成 |
| T-0111 | Identity 状态机规范 | 完成 |
| T-0112 | IDL 安全边界契约测试 | 完成 |
| T-0113 | PHX-006 最终人工确认 | 完成（人工批准） |
| T-0114 | BOOK00–22 全量 Constitution Conformance Review | 完成 |
| T-0115 | Kernel 双层解释与 AI 四层 taxonomy | 完成（人工批准） |
| T-0116 | Project Phoenix Roadmap v3 | 完成 |
| T-0117 | BOOK XXIII Smart Terminal Constitution | 完成 |
| T-0118 | Smart Terminal Blueprint 与 Architecture ownership | 完成 |

## 下一任务

| ID | 任务 | 状态 |
|----|------|------|
| T-0119 | BOOK XXIII 二次宪法合规审查 | 完成（Fully Compliant） |
| T-0120 | PHX-A03 Architecture Realignment 验收 | 完成 |
| T-0121 | PHX-K07 Organization Kernel 架构与接口门禁 | 完成 |
| T-0122 | ADR-0022 Organization 生命周期、层级与并发 | 完成 |
| T-0123 | Tenant / Enterprise 分离与 Alembic 0011 | 完成 |
| T-0124 | Organization 乐观锁、状态机与并发门禁 | 完成 |
| T-0125 | Organization OpenAPI 与 PostgreSQL 验收 | 完成（184 + 10） |
| T-0126 | PHX-K07 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0127 | PHX-K08 Permission Kernel 架构与接口门禁 | 完成 |
| T-0128 | ADR-0023 Policy / Scope / Delegation | 完成 |
| T-0129 | Slice A Foundation Security Closure | 完成 |
| T-0130 | Slice B Policy / Scope / deny-overrides | 完成 |
| T-0131 | Slice C Delegation 父链与缩小约束 | 完成 |
| T-0132 | Slice D OpenAPI / Alembic 0012 / PostgreSQL | 完成 |
| T-0133 | PHX-K08 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0134 | PHX-K09 Workflow Kernel 架构与接口门禁 | 完成 |
| T-0135 | ADR-0024 Workflow 审批真相源 | 完成 |
| T-0136 | Slice A 并发与 reject/escalate 闭合 | 完成 |
| T-0137 | Slice B 定义废弃与批准绑定扩展 | 完成 |
| T-0138 | Slice C SLA due_at | 完成 |
| T-0139 | Slice D 补偿 / OpenAPI / Alembic 0013 / PostgreSQL | 完成 |
| T-0140 | PHX-K09 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0141 | PHX-K10 Knowledge 架构与接口门禁 | 完成 |
| T-0142 | ADR-0025 Knowledge Shared Capability | 完成 |
| T-0143 | Slice A/B Knowledge 内存服务（Provenance/Derived/Retention/Search） | 完成 |
| T-0144 | Slice C SQLAlchemy / TransactionalKnowledge / Alembic 0014 | 完成 |
| T-0145 | Slice D OpenAPI / 状态机 / 事件 / PostgreSQL | 完成 |
| T-0146 | PHX-K10 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0147 | PHX-P11 Event Delivery / Outbox 架构门禁 | 完成 |
| T-0148 | ADR-0026 Event Outbox / Worker / DLQ | 完成 |
| T-0149 | Slice A/B Outbox enqueue + dispatch/retry/DLQ | 完成 |
| T-0150 | Slice C/D Alembic 0015 / OpenAPI / PostgreSQL | 完成 |
| T-0151 | PHX-P11 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0152 | PHX-A12 AI Runtime 架构与接口门禁 | 完成 |
| T-0153 | ADR-0027 AI Runtime 边界与审批桥 | 完成 |
| T-0154 | Slice A/B Agent/Tool/Memory/Approval Bridge | 完成 |
| T-0155 | Slice C/D Alembic 0016 / OpenAPI / PostgreSQL | 完成 |
| T-0156 | PHX-A12 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0157 | PHX-T13 Smart Terminal 架构门禁 | 完成 |
| T-0158 | ADR-0028 Smart Terminal 边界 | 完成 |
| T-0159 | Slice A/B Session/Intent/Preview/Approval/Commit | 完成 |
| T-0160 | Slice C/D Alembic 0017 / OpenAPI / PostgreSQL | 完成 |
| T-0161 | PHX-T13 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0162 | PHX-B14 Business Package Platform 架构门禁 | 完成 |
| T-0163 | ADR-0029 Package Platform 边界 | 完成 |
| T-0164 | Slice A/B Manifest/Install/Resolve | 完成 |
| T-0165 | Slice C/D Alembic 0018 / OpenAPI / sample_ops / PostgreSQL | 完成 |
| T-0166 | PHX-B14 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0167 | PHX-E15 Enterprise Brain & Twin 架构门禁 | 完成 |
| T-0168 | ADR-0030 Brain/Twin 边界 | 完成 |
| T-0169 | Slice A/B Twin Snapshot + Brain Insight | 完成 |
| T-0170 | Slice C/D Alembic 0019 / OpenAPI / PostgreSQL | 完成 |
| T-0171 | PHX-E15 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0172 | PHX-M16 Marketplace 技术架构门禁 | 完成 |
| T-0173 | ADR-0031 Marketplace 技术边界 | 完成 |
| T-0174 | Slice A/B Listing/Signature/Review/Acquire | 完成 |
| T-0175 | Slice C/D Alembic 0020 / OpenAPI / PostgreSQL | 完成 |
| T-0176 | PHX-M16 技术七步自审与验收 | 完成（Technically Fully Accepted） |
| T-0177 | Marketplace 商业/法律政策（定价/分成/账单/争议） | 待批准 |
| T-0178 | PHX-R17 EAOS Release Train 架构门禁 | 完成 |
| T-0179 | ADR-0032 Release Train 边界 | 完成 |
| T-0180 | Release Manifest / Compat / Ops Runbook | 完成 |
| T-0181 | eaos_sdk + api.adapters + 发布契约测试 | 完成 |
| T-0182 | PHX-R17 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0183 | PHX-G18 API Gateway 架构门禁 | 完成 |
| T-0184 | ADR-0033 API Gateway 边界 | 完成 |
| T-0185 | 最小 FastAPI 网关与受信上下文派生 | 完成 |
| T-0186 | 网关契约测试与文档 | 完成 |
| T-0187 | PHX-G18 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0188 | 全量 OpenAPI HTTP 路由实现 | 部分完成（G148 inventory；G164 mount；G166 semantic remainder deepened；full parity 仍 defer） |
| T-0189 | JWT/OIDC 认证提供商产品化 | 完成（G40/G61/G132 + G147 product surface） |
| T-0190 | PHX-E19 领域事件目录接线门禁 | 完成 |
| T-0191 | ADR-0034 命名归一与受信 enqueue | 完成 |
| T-0192 | K07–K10 同事务 outbox 接线 | 完成 |
| T-0193 | PHX-E19 契约测试与最终验收 | 完成（Fully Accepted） |
| T-0194 | permission.decision.recorded 接线 | 完成（PHX-E20） |
| T-0195 | PHX-G20 Identity HTTP 架构门禁 | 完成 |
| T-0196 | ADR-0035 Gateway Identity 边界 | 完成 |
| T-0197 | Identity 五路由薄适配与契约测试 | 完成 |
| T-0198 | PHX-G20 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0199 | 其他域 / Identity AI·Governor HTTP | 完成（G138 thin probe；相关 G120/G121/G137） |
| T-0200 | PHX-G21 Organization HTTP 架构门禁 | 完成 |
| T-0201 | ADR-0036 Gateway Organization 边界 | 完成 |
| T-0202 | Organization 租户面六路由与契约 | 完成 |
| T-0203 | PHX-G21 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0204 | 平台租户 HTTP / derive_platform_context | 完成（G25 Gateway；G127 Terminal thin probe） |
| T-0205 | PHX-G22 Permission HTTP 架构门禁 | 完成 |
| T-0206 | ADR-0037 Gateway Permission 边界 | 完成 |
| T-0207 | Permission 七路由与契约测试 | 完成 |
| T-0208 | PHX-G22 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0209 | Permission deprecate/delegate HTTP | 完成（PHX-G31） |
| T-0210 | PHX-G23 Workflow HTTP 架构门禁 | 完成 |
| T-0211 | ADR-0038 Gateway Workflow 边界 | 完成 |
| T-0212 | Workflow 六路由与契约测试 | 完成 |
| T-0213 | PHX-G23 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0214 | Workflow signal/cancel/compensate/escalate HTTP | 完成（PHX-G31） |
| T-0215 | PHX-G24 Knowledge HTTP 架构门禁 | 完成 |
| T-0216 | ADR-0039 Gateway Knowledge 边界 | 完成 |
| T-0217 | Knowledge 六路由与契约测试 | 完成 |
| T-0218 | PHX-G24 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0219 | Knowledge archive/share HTTP | 完成（PHX-G31） |
| T-0220 | PHX-G25 平台租户 HTTP 架构门禁 | 完成 |
| T-0221 | ADR-0040 平台上下文边界 | 完成 |
| T-0222 | platform tenants 三路由与契约 | 完成 |
| T-0223 | PHX-G25 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0224 | PHX-G26 Event HTTP 架构门禁 | 完成 |
| T-0225 | ADR-0041 Gateway Event 边界 | 完成 |
| T-0226 | Event 九路由与契约测试 | 完成 |
| T-0227 | PHX-G26 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0228 | Event webhook / 外部订阅传输 | 完成（E21 传输 + E22 HMAC） |
| T-0229 | PHX-G27 Package HTTP 架构门禁 | 完成 |
| T-0230 | ADR-0042 Gateway Package 边界 | 完成 |
| T-0231 | Package 七路由与契约测试 | 完成 |
| T-0232 | PHX-G27 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0233 | PHX-G28 Twin/Brain HTTP 架构门禁 | 完成 |
| T-0234 | ADR-0043 建议与执行权分离边界 | 完成 |
| T-0235 | Twin/Brain 六路由与契约测试 | 完成 |
| T-0236 | PHX-G28 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0237 | PHX-G29 AI Runtime HTTP 架构门禁 | 完成 |
| T-0238 | ADR-0044 Gateway AI 边界 | 完成 |
| T-0239 | AI 八路由与契约测试 | 完成 |
| T-0240 | PHX-G29 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0241 | PHX-G30 Terminal HTTP 架构门禁 | 完成 |
| T-0242 | ADR-0045 Gateway Terminal 边界 | 完成 |
| T-0243 | Terminal 十路由与契约测试 | 完成 |
| T-0244 | PHX-G30 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0245 | PHX-G31 域扩展路由架构门禁 | 完成 |
| T-0246 | ADR-0046 Domain Route Completions | 完成 |
| T-0247 | Workflow/Knowledge/Permission 扩展路由与契约 | 完成 |
| T-0248 | PHX-G31 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0249 | Organization 扩展 HTTP（enterprise/membership 生命周期） | 完成（Fully Accepted） |
| T-0250 | PHX-G32 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0251 | ADR-0048 Gateway Marketplace 技术 HTTP 边界 | 完成 |
| T-0252 | Marketplace 技术九路由与契约测试 | 完成 |
| T-0253 | PHX-G34 七步自审与最终验收 | 完成（Fully Accepted；商业仍开放） |
| T-0254 | PHX-G35 Operator Shell 架构门禁 | 完成 |
| T-0255 | ADR-0049 Terminal Operator Shell 边界 | 完成 |
| T-0256 | Operator Shell 静态资源与 `/terminal/` 挂载 | 完成 |
| T-0257 | PHX-G35 七步自审与最终验收 | 完成（Fully Accepted；技术壳） |
| T-0258 | PHX-E20 DecisionRecorded 架构门禁 | 完成 |
| T-0259 | ADR-0050 DecisionRecorded 接线 | 完成 |
| T-0260 | Evaluate → outbox 实现与契约 | 完成 |
| T-0261 | PHX-E20 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0262 | PHX-E21 Webhook 架构门禁 | 完成 |
| T-0263 | ADR-0051 Event Webhook 传输边界 | 完成 |
| T-0264 | delivery_url / SSRF / Alembic 0021 与契约 | 完成 |
| T-0265 | PHX-E21 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0266 | PHX-G36 Complete Terminal UI 架构门禁 | 完成 |
| T-0267 | ADR-0052 Complete Terminal UI 边界 | 完成 |
| T-0268 | 四表面壳与契约测试 | 完成 |
| T-0269 | PHX-G36 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0270 | PHX-G37 JWT/OIDC（已批准） | 完成（Fully Accepted — HS256） |
| T-0271 | PHX-M17 Marketplace 商业（已批准；待政策输入） | 完成（Fully Accepted — Foundation v1） |
| T-0272 | ADR-0053 JWT/OIDC Trusted Context | 完成 |
| T-0273 | Bearer 校验与 Context 派生契约 | 完成 |
| T-0274 | PHX-G37 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0275 | ADR-0054 Marketplace Commercial Policy | 完成 |
| T-0276 | 商业领域/SQL/Gateway 与契约 | 完成 |
| T-0277 | PHX-M17 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0278 | PHX-G38 JWKS/RS256 架构门禁 | 完成 |
| T-0279 | ADR-0055 JWT JWKS/RS256 | 完成 |
| T-0280 | RS256/JWKS 校验与契约 | 完成 |
| T-0281 | PHX-G38 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0282 | PHX-E22 Webhook HMAC 架构门禁 | 完成 |
| T-0283 | ADR-0056 Event Webhook HMAC | 完成 |
| T-0284 | signing_secret / 签名头与契约 | 完成 |
| T-0285 | PHX-E22 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0286 | PHX-G39 Extension Host 架构门禁 | 完成 |
| T-0287 | ADR-0057 Terminal Extension Host | 完成 |
| T-0288 | 扩展沙箱 API / UI / 契约 | 完成 |
| T-0289 | PHX-G39 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0290 | PHX-G40 OIDC 登录架构门禁 | 完成 |
| T-0291 | ADR-0058 OIDC Authorization Code Login | 完成 |
| T-0292 | OIDC login/callback / Terminal Bearer / 契约 | 完成 |
| T-0293 | PHX-G40 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0294 | PHX-G41 Extension SQL 架构门禁 | 完成 |
| T-0295 | ADR-0059 Terminal Extension SQL | 完成 |
| T-0296 | terminal_extensions / 仓储 / Transactional | 完成 |
| T-0297 | PHX-G41 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0298 | PHX-G42 Extension iframe/CSP 架构门禁 | 完成 |
| T-0299 | ADR-0060 Terminal Extension iframe + CSP | 完成 |
| T-0300 | demo-panel / 桥接 / CSP 中间件 / 契约 | 完成 |
| T-0301 | PHX-G42 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0302 | PHX-G43 Extension Worker 架构门禁 | 完成 |
| T-0303 | ADR-0061 Terminal Extension Worker | 完成 |
| T-0304 | demo-worker / 桥接 channel / 契约 | 完成 |
| T-0305 | PHX-G43 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0306 | PHX-M18 Marketplace 签名架构门禁 | 完成 |
| T-0307 | ADR-0062 Marketplace Package Signature | 完成 |
| T-0308 | signing HMAC/Ed25519 / Service 接线 / 契约 | 完成 |
| T-0309 | PHX-M18 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0310 | PHX-G44 Extension 验签架构门禁 | 完成 |
| T-0311 | ADR-0063 Terminal Extension Signature | 完成 |
| T-0312 | signing / activate 接线 / 契约 | 完成 |
| T-0313 | PHX-G44 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0314 | PHX-G45 多发行方 JWKS 架构门禁 | 完成 |
| T-0315 | ADR-0064 JWT Multi-Issuer JWKS | 完成 |
| T-0316 | issuers JSON / kid 刷新 / 契约 | 完成 |
| T-0317 | PHX-G45 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0318 | PHX-G46 JWT denylist 架构门禁 | 完成 |
| T-0319 | ADR-0065 JWT Denylist | 完成 |
| T-0320 | denylist JSON/URL / 契约 | 完成 |
| T-0321 | PHX-G46 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0322 | PHX-G47 OIDC Discovery 架构门禁 | 完成 |
| T-0323 | ADR-0066 OIDC IdP Discovery | 完成 |
| T-0324 | Discovery 客户端 / 缓存 / 契约 | 完成 |
| T-0325 | PHX-G47 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0326 | PHX-G48 Discovery→JWKS Wire 架构门禁 | 完成 |
| T-0327 | ADR-0067 OIDC Discovery JWKS Wire | 完成 |
| T-0328 | maybe_wire_discovery_jwks / Bearer 接线 / 契约 | 完成 |
| T-0329 | PHX-G48 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0330 | PHX-G49 生产拓扑架构门禁 | 完成 |
| T-0331 | ADR-0068 Production Deploy Topology | 完成 |
| T-0332 | PRODUCTION_TOPOLOGY / Runbook / 契约 | 完成 |
| T-0333 | PHX-G49 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0334 | PHX-G50 Compose 架构门禁 | 完成 |
| T-0335 | ADR-0069 Docker Compose Foundation | 完成 |
| T-0336 | deploy/docker + COMPOSE + 契约 | 完成 |
| T-0337 | PHX-G50 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0338 | PHX-G51 Helm 架构门禁 | 完成 |
| T-0339 | ADR-0070 Kubernetes Helm Foundation | 完成 |
| T-0340 | deploy/helm/eaos + HELM + 契约 | 完成 |
| T-0341 | PHX-G51 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0342 | PHX-G52 Ingress 架构门禁 | 完成 |
| T-0343 | ADR-0071 Ingress / TLS Foundation | 完成 |
| T-0344 | ingress 模板 + INGRESS + 契约 | 完成 |
| T-0345 | PHX-G52 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0346 | PHX-G53 HPA 架构门禁 | 完成 |
| T-0347 | ADR-0072 HPA Foundation | 完成 |
| T-0348 | hpa 模板 + HPA.md + 契约 | 完成 |
| T-0349 | PHX-G53 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0350 | PHX-G54 VPA 架构门禁 | 完成 |
| T-0351 | ADR-0073 VPA Foundation | 完成 |
| T-0352 | vpa 模板 + VPA.md + 契约 | 完成 |
| T-0353 | PHX-G54 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0354 | PHX-G55 多 IdP UI 架构门禁 | 完成 |
| T-0355 | ADR-0074 Multi-IdP Status UI | 完成 |
| T-0356 | idp/status + Admin 探针 + 契约 | 完成 |
| T-0357 | PHX-G55 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0358 | PHX-G56 IdP 注册表架构门禁 | 完成 |
| T-0359 | ADR-0075 Multi-IdP Write Registry | 完成 |
| T-0360 | 注册表 API / 合并 / Alembic 0025 / 契约 | 完成 |
| T-0361 | PHX-G56 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0362 | PHX-G57 IdP SQL 适配器架构门禁 | 完成 |
| T-0363 | ADR-0076 IdP Registry SQL Adapter | 完成 |
| T-0364 | SQL 仓储 / store 接线 / 契约 | 完成 |
| T-0365 | PHX-G57 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0366 | PHX-G58 KEDA 架构门禁 | 完成 |
| T-0367 | ADR-0077 KEDA Foundation | 完成 |
| T-0368 | ScaledObject 模板 + KEDA.md + 契约 | 完成 |
| T-0369 | PHX-G58 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0370 | PHX-G59 Mesh 架构门禁 | 完成 |
| T-0371 | ADR-0078 Service Mesh Foundation | 完成 |
| T-0372 | mesh values/模板 + MESH.md + 契约 | 完成 |
| T-0373 | PHX-G59 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0374 | PHX-G60 Discovery 写回架构门禁 | 完成 |
| T-0375 | ADR-0079 Discovery → Registry Writeback | 完成 |
| T-0376 | upsert / sync API / status / 契约 | 完成 |
| T-0377 | PHX-G60 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0378 | PHX-G61 Refresh/Logout 架构门禁 | 完成 |
| T-0379 | ADR-0080 OIDC Refresh + RP-Logout | 完成 |
| T-0380 | refresh/logout API + Terminal + 契约 | 完成 |
| T-0381 | PHX-G61 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0382 | PHX-G62 IdP Terminal Ops 架构门禁 | 完成 |
| T-0383 | ADR-0081 Platform IdP Registry Terminal Ops | 完成 |
| T-0384 | Admin UI + platform 头 + 契约 | 完成 |
| T-0385 | PHX-G62 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0386 | PHX-G63 Refresh SQL 架构门禁 | 完成 |
| T-0387 | ADR-0082 OIDC Refresh Binding SQL | 完成 |
| T-0388 | 仓储 / Alembic 0026 / 契约 | 完成 |
| T-0389 | PHX-G63 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0390 | PHX-G64 Refresh 加密架构门禁 | 完成 |
| T-0391 | ADR-0083 OIDC Refresh Token Encryption | 完成 |
| T-0392 | Fernet seal/open + store/status 契约 | 完成 |
| T-0393 | PHX-G64 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0394 | PHX-G65 Fernet 轮换架构门禁 | 完成 |
| T-0395 | ADR-0084 OIDC Refresh Key Rotation | 完成 |
| T-0396 | MultiFernet + status key_count 契约 | 完成 |
| T-0397 | PHX-G65 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0398 | PHX-G66 组织联邦薄 API 架构门禁 | 完成 |
| T-0399 | ADR-0085 Tenant IdP Federation Binding | 完成 |
| T-0400 | 绑定存储/平台 API/OIDC 强制契约 | 完成 |
| T-0401 | PHX-G66 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0402 | PHX-G67 联邦 SQL 架构门禁 | 完成 |
| T-0403 | ADR-0086 Tenant IdP Federation SQL | 完成 |
| T-0404 | 仓储 / Alembic 0027 / 契约 | 完成 |
| T-0405 | PHX-G67 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0406 | PHX-G68 JWT 联邦强制架构门禁 | 完成 |
| T-0407 | ADR-0087 JWT Tenant IdP Federation | 完成 |
| T-0408 | 租户面 JWT 强制 + 契约 | 完成 |
| T-0409 | PHX-G68 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0410 | PHX-G69 联邦 Terminal UI 架构门禁 | 完成 |
| T-0411 | ADR-0088 Tenant IdP Federation Terminal Ops | 完成 |
| T-0412 | Admin UI + 契约 | 完成 |
| T-0413 | PHX-G69 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0414 | PHX-G70 读时重加密架构门禁 | 完成 |
| T-0415 | ADR-0089 OIDC Refresh Re-encrypt On Read | 完成 |
| T-0416 | get 路径 re-seal + 契约 | 完成 |
| T-0417 | PHX-G70 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0418 | PHX-G71 Mesh Policy CRD 架构门禁 | 完成 |
| T-0419 | ADR-0090 Mesh Policy CRD Foundation | 完成 |
| T-0420 | PeerAuthentication 模板 + MESH/契约 | 完成 |
| T-0421 | PHX-G71 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0422 | PHX-G72 Mesh VS/DR 架构门禁 | 完成 |
| T-0423 | ADR-0091 Mesh Traffic CRD Foundation | 完成 |
| T-0424 | VS/DR 模板 + MESH/契约 | 完成 |
| T-0425 | PHX-G72 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0426 | PHX-G73 Mesh Authz 架构门禁 | 完成 |
| T-0427 | ADR-0092 Mesh AuthorizationPolicy Foundation | 完成 |
| T-0428 | AuthorizationPolicy 模板 + MESH/契约 | 完成 |
| T-0429 | PHX-G73 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0430 | PHX-G74 Key Provider 架构门禁 | 完成 |
| T-0431 | ADR-0093 OIDC Refresh Key Provider | 完成 |
| T-0432 | env|file 加载 + 契约 | 完成 |
| T-0433 | PHX-G74 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0434 | PHX-G75 KMS 架构门禁 | 完成 |
| T-0435 | ADR-0094 OIDC Refresh KMS Provider | 完成 |
| T-0436 | http/aws/gcp/azure 薄后端 + 契约 | 完成 |
| T-0437 | PHX-G75 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0438 | PHX-G76 Deploy Region 架构门禁 | 完成 |
| T-0439 | ADR-0095 Deploy Region Identity | 完成 |
| T-0440 | release/Helm/Compose + 契约 | 完成 |
| T-0441 | PHX-G76 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0442 | PHX-G77 Federation Matrix 架构门禁 | 完成 |
| T-0443 | ADR-0096 Tenant IdP Federation Matrix | 完成 |
| T-0444 | matrix API + Terminal + 契约 | 完成 |
| T-0445 | PHX-G77 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0446 | PHX-G78 Issuer Priority 架构门禁 | 完成 |
| T-0447 | ADR-0097 Federation Issuer Priority | 完成 |
| T-0448 | priority 字段 + Alembic 0028 + 契约 | 完成 |
| T-0449 | PHX-G78 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0450 | PHX-G79 Required Claims 架构门禁 | 完成 |
| T-0451 | ADR-0098 OIDC Required Claims Gate | 完成 |
| T-0452 | mint 门禁 + status + 契约 | 完成 |
| T-0453 | PHX-G79 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0454 | PHX-G80 amr/acr 架构门禁 | 完成 |
| T-0455 | ADR-0099 OIDC amr/acr Gate | 完成 |
| T-0456 | mint 门禁 + status + 契约 | 完成 |
| T-0457 | PHX-G80 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0458 | PHX-G81 Claim→Role 架构门禁 | 完成 |
| T-0459 | ADR-0100 OIDC Claim→Role Mint | 完成 |
| T-0460 | eaos_roles mint + status + 契约 | 完成 |
| T-0461 | PHX-G81 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0462 | PHX-G82 ExecutionContext roles 架构门禁 | 完成 |
| T-0463 | ADR-0101 JWT eaos_roles → Context | 完成 |
| T-0464 | roles 解析 + serialize + 契约 | 完成 |
| T-0465 | PHX-G82 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0466 | PHX-G83 role grant map 架构门禁 | 完成 |
| T-0467 | ADR-0102 Permission Role Grant Map | 完成 |
| T-0468 | evaluate/explain + 契约 | 完成 |
| T-0469 | PHX-G83 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0470 | PHX-G84 multi-provider login 架构门禁 | 完成 |
| T-0471 | ADR-0103 OIDC Multi-Provider Login | 完成 |
| T-0472 | providers 目录 + login/callback + Terminal | 完成 |
| T-0473 | PHX-G84 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0474 | PHX-G85 per-provider refresh 架构门禁 | 完成 |
| T-0475 | ADR-0104 OIDC Provider Refresh | 完成 |
| T-0476 | provider claim + refresh/logout overlay | 完成 |
| T-0477 | PHX-G85 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0478 | PHX-G86 provider end_session 架构门禁 | 完成 |
| T-0479 | ADR-0105 OIDC Provider End-Session | 完成 |
| T-0480 | end_session 第 7 段 + catalog + 契约 | 完成 |
| T-0481 | PHX-G86 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0482 | PHX-G87 authorize step-up 架构门禁 | 完成 |
| T-0483 | ADR-0106 OIDC Authorize Step-Up | 完成 |
| T-0484 | acr_values/prompt + status + 契约 | 完成 |
| T-0485 | PHX-G87 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0486 | PHX-G88 roles catalog 架构门禁 | 完成 |
| T-0487 | ADR-0107 EAOS Roles Catalog | 完成 |
| T-0488 | GET /permission/roles + 契约 | 完成 |
| T-0489 | PHX-G88 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0490 | PHX-G89 MFA enrollment URL 架构门禁 | 完成 |
| T-0491 | ADR-0108 OIDC MFA Enrollment URL | 完成 |
| T-0492 | redirect + deny 附 URL + Terminal | 完成 |
| T-0493 | PHX-G89 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0494 | PHX-G90 roles catalog SQL 架构门禁 | 完成 |
| T-0495 | ADR-0109 Declared Roles SQL Store | 完成 |
| T-0496 | Alembic 0029 + platform CRUD + 契约 | 完成 |
| T-0497 | PHX-G90 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0498 | PHX-G91 Terminal roles admin 架构门禁 | 完成 |
| T-0499 | ADR-0110 Terminal Roles Admin | 完成 |
| T-0500 | Terminal Admin List/Upsert/Disable + 契约 | 完成 |
| T-0501 | PHX-G91 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0502 | PHX-G92 tenant roles catalog read 架构门禁 | 完成 |
| T-0503 | ADR-0111 Terminal Tenant Roles Catalog Read | 完成 |
| T-0504 | Terminal Admin 租户目录只读 + 契约 | 完成 |
| T-0505 | PHX-G92 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0506 | PHX-G93 roles status 架构门禁 | 完成 |
| T-0507 | ADR-0112 Permission Roles Status | 完成 |
| T-0508 | GET /permission/roles/status + Terminal + 契约 | 完成 |
| T-0509 | PHX-G93 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0510 | PHX-G94 permission evaluate probe 架构门禁 | 完成 |
| T-0511 | ADR-0113 Terminal Permission Evaluate | 完成 |
| T-0512 | Terminal Evaluate/Explain + 契约 | 完成 |
| T-0513 | PHX-G94 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0514 | PHX-G95 effective-permissions probe 架构门禁 | 完成 |
| T-0515 | ADR-0114 Terminal Effective Permissions | 完成 |
| T-0516 | Terminal List effective permissions + 契约 | 完成 |
| T-0517 | PHX-G95 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0518 | PHX-G96 JWT denylist status 架构门禁 | 完成 |
| T-0519 | ADR-0115 JWT Denylist Status | 完成 |
| T-0520 | GET /auth/jwt/status + Terminal + 契约 | 完成 |
| T-0521 | PHX-G96 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0522 | PHX-G97 event bus stats probe 架构门禁 | 完成 |
| T-0523 | ADR-0116 Terminal Event Bus Stats | 完成 |
| T-0524 | Terminal Event stats/DLQ/replay + 契约 | 完成 |
| T-0525 | PHX-G97 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0526 | PHX-G98 event dispatch probe 架构门禁 | 完成 |
| T-0527 | ADR-0117 Terminal Event Dispatch | 完成 |
| T-0528 | Terminal Dispatch/Get event + 契约 | 完成 |
| T-0529 | PHX-G98 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0530 | PHX-G99 event enqueue/publish probe 架构门禁 | 完成 |
| T-0531 | ADR-0118 Terminal Event Enqueue/Publish | 完成 |
| T-0532 | Terminal Enqueue/Publish + 契约 | 完成 |
| T-0533 | PHX-G99 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0534 | PHX-G100 event subscribe/replay probe 架构门禁 | 完成 |
| T-0535 | ADR-0119 Terminal Event Subscribe/Replay | 完成 |
| T-0536 | Terminal Subscribe/Replay + 契约 | 完成 |
| T-0537 | PHX-G100 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0538 | PHX-G101 marketplace status/listing 架构门禁 | 完成 |
| T-0539 | ADR-0120 Marketplace Status + Listing Probe | 完成 |
| T-0540 | GET /marketplace/status + Terminal listing + 契约 | 完成 |
| T-0541 | PHX-G101 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0542 | PHX-G102 marketplace listing lifecycle 架构门禁 | 完成 |
| T-0543 | ADR-0121 Marketplace Listing Lifecycle Probe | 完成 |
| T-0544 | Terminal signature/submit/review/publish/revoke + 契约 | 完成 |
| T-0545 | PHX-G102 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0546 | PHX-G103 marketplace acquire probe 架构门禁 | 完成 |
| T-0547 | ADR-0122 Marketplace Acquire Technical Probe | 完成 |
| T-0548 | Terminal Acquire listing + 契约 | 完成 |
| T-0549 | PHX-G103 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0550 | PHX-G104 workflow status/definition/instance 架构门禁 | 完成 |
| T-0551 | ADR-0123 Workflow Status / Definition / Instance Probe | 完成 |
| T-0552 | GET /workflow/status + Terminal 五控件 + 契约 | 完成 |
| T-0553 | PHX-G104 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0554 | PHX-G105 workflow approve/reject 架构门禁 | 完成 |
| T-0555 | ADR-0124 Workflow Task Approve / Reject Probe | 完成 |
| T-0556 | Terminal Approve/Reject workflow task + 契约 | 完成 |
| T-0557 | PHX-G105 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0558 | PHX-G106 workflow signal/cancel 架构门禁 | 完成 |
| T-0559 | ADR-0125 Workflow Signal / Cancel Probe | 完成 |
| T-0560 | Terminal Signal/Cancel workflow instance + 契约 | 完成 |
| T-0561 | PHX-G106 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0562 | PHX-G107 workflow compensate/escalate 架构门禁 | 完成 |
| T-0563 | ADR-0126 Workflow Compensate / Escalate Probe | 完成 |
| T-0564 | Terminal Compensate/Escalate + 契约 | 完成 |
| T-0565 | PHX-G107 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0566 | PHX-G108 package status/manifest/surfaces 架构门禁 | 完成 |
| T-0567 | ADR-0127 Package Status / Manifest / Surfaces Probe | 完成 |
| T-0568 | GET /packages/status + Terminal 四控件 + 契约 | 完成 |
| T-0569 | PHX-G108 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0570 | PHX-G109 package publish/install/resolve 架构门禁 | 完成 |
| T-0571 | ADR-0128 Package Publish / Install / Disable / Resolve Probe | 完成 |
| T-0572 | Terminal Publish/Install/Disable/Resolve + 契约 | 完成 |
| T-0573 | PHX-G109 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0574 | PHX-G110 knowledge status/entity 架构门禁 | 完成 |
| T-0575 | ADR-0129 Knowledge Status / Entity Probe | 完成 |
| T-0576 | GET /knowledge/status + Terminal 四控件 + 契约 | 完成 |
| T-0577 | PHX-G110 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0578 | PHX-G111 knowledge archive/share/search 架构门禁 | 完成 |
| T-0579 | ADR-0130 Knowledge Archive / Share / Search Probe | 完成 |
| T-0580 | Terminal Archive/Share/Search + 契约 | 完成 |
| T-0581 | PHX-G111 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0582 | PHX-G112 knowledge link/provenance 架构门禁 | 完成 |
| T-0583 | ADR-0131 Knowledge Link / Provenance Probe | 完成 |
| T-0584 | Terminal Create link / Get provenance + 契约 | 完成 |
| T-0585 | PHX-G112 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0586 | PHX-G113 twin status/snapshot 架构门禁 | 完成 |
| T-0587 | ADR-0132 Twin Status / Snapshot Probe | 完成 |
| T-0588 | GET /twin/status + Terminal Upsert/Get + 契约 | 完成 |
| T-0589 | PHX-G113 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0590 | PHX-G114 twin authorize fail-closed 架构门禁 | 完成 |
| T-0591 | ADR-0133 Twin Authorize Fail-Closed Probe | 完成 |
| T-0592 | Terminal Authorize from twin + 契约 | 完成 |
| T-0593 | PHX-G114 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0594 | PHX-G115 brain status/insight 架构门禁 | 完成 |
| T-0595 | ADR-0134 Brain Status / Insight Probe | 完成 |
| T-0596 | GET /brain/status + Terminal Publish/Get + 契约 | 完成 |
| T-0597 | PHX-G115 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0598 | PHX-G116 brain execute fail-closed 架构门禁 | 完成 |
| T-0599 | ADR-0135 Brain Execute Fail-Closed Probe | 完成 |
| T-0600 | Terminal Execute brain insight + 契约 | 完成 |
| T-0601 | PHX-G116 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0602 | PHX-G117 AI Runtime status/run 架构门禁 | 完成 |
| T-0603 | ADR-0136 AI Runtime Status / Run Probe | 完成 |
| T-0604 | GET /ai/status + Terminal Create/Get run + 契约 | 完成 |
| T-0605 | PHX-G117 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0606 | PHX-G118 AI tools/memory 架构门禁 | 完成 |
| T-0607 | ADR-0137 AI Tools / Memory Probe | 完成 |
| T-0608 | Terminal Register/Invoke/Memory + 契约 | 完成 |
| T-0609 | PHX-G118 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0610 | PHX-G119 AI approval/commit 架构门禁 | 完成 |
| T-0611 | ADR-0138 AI Approval / Commit Probe | 完成 |
| T-0612 | Terminal Request approval / Commit + 契约 | 完成 |
| T-0613 | PHX-G119 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0614 | PHX-G120 identity status/subject 架构门禁 | 完成 |
| T-0615 | ADR-0139 Identity Status / Subject Probe | 完成 |
| T-0616 | GET /identity/status + Terminal Register/Resolve + 契约 | 完成 |
| T-0617 | PHX-G120 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0618 | PHX-G121 identity credential/session 架构门禁 | 完成 |
| T-0619 | ADR-0140 Identity Credential / Session Probe | 完成 |
| T-0620 | Terminal Bind/Create/Validate + 契约 | 完成 |
| T-0621 | PHX-G121 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0622 | PHX-G122 organization status/tenant/enterprise 架构门禁 | 完成 |
| T-0623 | ADR-0141 Organization Status / Tenant / Enterprise Probe | 完成 |
| T-0624 | GET /organization/status + Terminal Get/Create/List + 契约 | 完成 |
| T-0625 | PHX-G122 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0626 | PHX-G123 organization unit/membership 架构门禁 | 完成 |
| T-0627 | ADR-0142 Organization Unit / Membership Probe | 完成 |
| T-0628 | Terminal Upsert unit / Tree / Membership + 契约 | 完成 |
| T-0629 | PHX-G123 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0630 | PHX-G124 organization lifecycle 架构门禁 | 完成 |
| T-0631 | ADR-0143 Organization Lifecycle Probe | 完成 |
| T-0632 | Terminal Set unit status / Suspend·Reactivate + 契约 | 完成 |
| T-0633 | PHX-G124 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0634 | PHX-G125 membership transfer/end 架构门禁 | 完成 |
| T-0635 | ADR-0144 Organization Membership Transfer / End Probe | 完成 |
| T-0636 | Terminal Transfer·End membership + 契约 | 完成 |
| T-0637 | PHX-G125 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0638 | PHX-G126 enterprise lifecycle 架构门禁 | 完成 |
| T-0639 | ADR-0145 Organization Enterprise Lifecycle Probe | 完成 |
| T-0640 | Terminal Suspend·Reactivate·Close enterprise + 契约 | 完成 |
| T-0641 | PHX-G126 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0642 | PHX-G127 platform tenant lifecycle 架构门禁 | 完成 |
| T-0643 | ADR-0146 Platform Tenant Lifecycle Probe | 完成 |
| T-0644 | Terminal Create·Suspend·Reactivate platform tenant + 契约 | 完成 |
| T-0645 | PHX-G127 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0646 | PHX-G128 permission write 架构门禁 | 完成 |
| T-0647 | ADR-0147 Permission Policy / Grant Manual Write Probe | 完成 |
| T-0648 | Terminal Create·Activate policy / Create·Revoke grant + 契约 | 完成 |
| T-0649 | PHX-G128 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0650 | PHX-G129 permission deprecate/delegate 架构门禁 | 完成 |
| T-0651 | ADR-0148 Permission Deprecate / Delegate Probe | 完成 |
| T-0652 | Terminal Deprecate·Delegate + 契约 | 完成 |
| T-0653 | PHX-G129 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0654 | PHX-G130 OpenAPI status catalog 架构门禁 | 完成 |
| T-0655 | ADR-0149 OpenAPI Foundation Status Catalog | 完成 |
| T-0656 | 9 份 OpenAPI status GET + 契约 | 完成 |
| T-0657 | PHX-G130 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0658 | PHX-G131 auth OpenAPI 架构门禁 | 完成 |
| T-0659 | ADR-0150 Auth OpenAPI Status Catalog | 完成 |
| T-0660 | auth.openapi.yaml + Manifest 12 + 契约 | 完成 |
| T-0661 | PHX-G131 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0662 | PHX-G132 OIDC login OpenAPI 架构门禁 | 完成 |
| T-0663 | ADR-0151 OIDC Login / Callback OpenAPI | 完成 |
| T-0664 | auth.openapi login/callback/providers + 契约 | 完成 |
| T-0665 | PHX-G132 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0666 | PHX-G133 OIDC refresh/logout OpenAPI 架构门禁 | 完成 |
| T-0667 | ADR-0152 OIDC Refresh / Logout OpenAPI | 完成 |
| T-0668 | auth.openapi refresh/logout + 契约 | 完成 |
| T-0669 | PHX-G133 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0670 | PHX-G134 MFA enrollment OpenAPI 架构门禁 | 完成 |
| T-0671 | ADR-0153 OIDC MFA Enrollment OpenAPI | 完成 |
| T-0672 | auth.openapi mfa-enrollment + 契约 | 完成 |
| T-0673 | PHX-G134 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0674 | PHX-G135 Platform OpenAPI 架构门禁 | 完成 |
| T-0675 | ADR-0154 Platform OpenAPI Catalog | 完成 |
| T-0676 | platform.openapi + Manifest 13 + 契约 | 完成 |
| T-0677 | PHX-G135 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0678 | PHX-G136 permission/roles OpenAPI 架构门禁 | 完成 |
| T-0679 | ADR-0155 Permission Roles List OpenAPI | 完成 |
| T-0680 | permission.openapi GET /roles + 契约 | 完成 |
| T-0681 | PHX-G136 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0682 | PHX-G137 Identity revoke 架构门禁 | 完成 |
| T-0683 | ADR-0156 Identity credential/session revoke | 完成 |
| T-0684 | Gateway + Terminal revoke 薄接线 + 契约 | 完成 |
| T-0685 | PHX-G137 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0686 | PHX-G138 AI/governor 架构门禁 | 完成 |
| T-0687 | ADR-0157 Identity AI/governor 薄探针 | 完成 |
| T-0688 | Gateway + Terminal AI/governor + 契约 | 完成 |
| T-0689 | PHX-G138 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0690 | PHX-G139 Ops OpenAPI 架构门禁 | 完成 |
| T-0691 | ADR-0158 Gateway Ops OpenAPI Catalog | 完成 |
| T-0692 | ops.openapi + Manifest 14 + 契约 | 完成 |
| T-0693 | PHX-G139 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0694 | PHX-G140 Terminal echo/deprecate 架构门禁 | 完成 |
| T-0695 | ADR-0159 Terminal ops echo + workflow deprecate | 完成 |
| T-0696 | Terminal 控件 + 契约 | 完成 |
| T-0697 | PHX-G140 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0698 | PHX-G141 Marketplace commercial Terminal 架构门禁 | 完成 |
| T-0699 | ADR-0160 Marketplace commercial Terminal probe | 完成 |
| T-0700 | Terminal 商业控件 + 契约 | 完成 |
| T-0701 | PHX-G141 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0702 | PHX-G142 Get enterprise 架构门禁 | 完成 |
| T-0703 | ADR-0161 Organization get enterprise probe | 完成 |
| T-0704 | Terminal Get enterprise + README + 契约 | 完成 |
| T-0705 | PHX-G142 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0706 | PHX-G144 Foundation 0.2.1 架构门禁 | 完成 |
| T-0707 | ADR-0163 Foundation 0.2.1 Release Train | 完成 |
| T-0708 | 版本 bump + release docs + DAL-U005 | 完成 |
| T-0709 | PHX-G144 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0710 | PHX-G145 WebAuthn/MFA posture 架构门禁 | 完成 |
| T-0711 | ADR-0164 WebAuthn/MFA product posture | 完成 |
| T-0712 | helper + oidc status + OpenAPI + Terminal + DAL-U006 | 完成 |
| T-0713 | PHX-G145 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0714 | PHX-G146 Role→grant posture 架构门禁 | 完成 |
| T-0715 | ADR-0165 Role→grant product posture | 完成 |
| T-0716 | helper + roles/status + OpenAPI + Terminal + DAL-U007 | 完成 |
| T-0717 | PHX-G146 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0718 | PHX-G147 OIDC login product 架构门禁 | 完成 |
| T-0719 | ADR-0166 OIDC login product surface | 完成 |
| T-0720 | helper + oidc status + OpenAPI + Terminal + DAL-U008 + T-0189 | 完成 |
| T-0721 | PHX-G147 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0722 | PHX-G148 OpenAPI inventory posture 架构门禁 | 完成 |
| T-0723 | ADR-0167 OpenAPI inventory product posture | 完成 |
| T-0724 | helper + adapters meta + ops OpenAPI + Terminal + DAL-U009 + T-0188 | 完成 |
| T-0725 | PHX-G148 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0726 | PHX-G149 Eng soft-queue tip 架构门禁 | 完成 |
| T-0727 | ADR-0168 Eng soft-queue tip board | 完成 |
| T-0728 | ENG_SOFT_QUEUE_TIP + TASKS T-0199/T-0204 + DAL-U010 | 完成 |
| T-0729 | PHX-G149 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0730 | PHX-G150 AED 架构门禁 | 完成 |
| T-0731 | ADR-0169 Autonomous Execution Directive | 完成 |
| T-0732 | AED v1.1 + DAL-G004/U012 + Dual-Track sync | 完成 |
| T-0733 | RP-001 AR Candidate NRI-ARC-RP-001 + DAL-U013 | 完成 |
| T-0734 | PHX-G150 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0735 | PHX-G151 WebAuthn ceremony stub 架构门禁 | 完成 |
| T-0736 | ADR-0170 WebAuthn ceremony stub deepen | 完成 |
| T-0737 | ceremony helper + router + posture + OpenAPI + Terminal + DAL-U023 | 完成 |
| T-0738 | PHX-G151 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0739 | PHX-G152 AR Board Queue 架构门禁 | 完成 |
| T-0740 | ADR-0171 AR Board Queue + Manifest hygiene | 完成 |
| T-0741 | NRI-AR-BOARD-QUEUE + Manifest G145–G152 + DAL-U024 | 完成 |
| T-0742 | PHX-G152 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0743 | PHX-G153 ops/compat/checklist 架构门禁 | 完成 |
| T-0744 | ADR-0172 Foundation ops hygiene | 完成 |
| T-0745 | Runbook + Compatibility + Checklist + Manifest G153 + DAL-U025 | 完成 |
| T-0746 | PHX-G153 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0747 | PHX-G154 ceremony observability 架构门禁 | 完成 |
| T-0748 | ADR-0173 WebAuthn ceremony stub observability | 完成 |
| T-0749 | step detail + posture G154 + OpenAPI 1.3.4 + inventory fence + DAL-U026 | 完成 |
| T-0750 | PHX-G154 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0751 | PHX-G155 T2/T3 Evidence Readiness 架构门禁 | 完成 |
| T-0752 | ADR-0174 T2/T3 Evidence Readiness Board | 完成 |
| T-0753 | NRI-T2-T3-EVID + Index/Library/G2 tip + DAL-U027 | 完成 |
| T-0754 | PHX-G155 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0755 | PHX-G156 Role→grant auto-write stub 架构门禁 | 完成 |
| T-0756 | ADR-0175 Role→grant auto-write stub deepen | 完成 |
| T-0757 | helper + router + posture G156 + OpenAPI 1.1.2 + DAL-U028 | 完成 |
| T-0758 | PHX-G156 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0759 | PHX-G157 ops/checklist 架构门禁 | 完成 |
| T-0760 | ADR-0176 Foundation ops hygiene after G156 | 完成 |
| T-0761 | Runbook + Checklist + Manifest G157 + DAL-U029 | 完成 |
| T-0762 | PHX-G157 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0763 | PHX-G158 Natural Pause 架构门禁 | 完成 |
| T-0764 | ADR-0177 Autonomous Soft-Queue Natural Pause | 完成 |
| T-0765 | ENG tip Pause + status + DAL-U030 | 完成 |
| T-0766 | PHX-G158 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0767 | PHX-G159 AR Board Hold 架构门禁 | 完成 |
| T-0768 | ADR-0178 Generation-1 AR Board Hold | 完成 |
| T-0769 | NRI-ARC-RP-001…010 Hold + queue/Index/Library + DAL-G005/U031 | 完成 |
| T-0770 | PHX-G159 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0771 | PHX-G161 Role→grant live mint 架构门禁 | 完成 |
| T-0772 | ADR-0179 Role→grant env-gated live mint | 完成 |
| T-0773 | helper mint + router + posture G161 + OpenAPI 1.1.3 + DAL-G006/U032 | 完成 |
| T-0774 | PHX-G161 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0775 | PHX-G163 T2/T3 Evidence Intake 架构门禁 | 完成 |
| T-0776 | ADR-0180 T2/T3 Evidence Intake & Live Capture | 完成 |
| T-0777 | NRI-T2-T3-INTAKE + template + readiness deepen + DAL-U034 | 完成 |
| T-0778 | PHX-G163 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0779 | PHX-G162 payment clearing 架构门禁 | 完成 |
| T-0780 | ADR-0181 Marketplace payment clearing | 完成 |
| T-0781 | helper + router + service + OpenAPI 1.2.0 + Terminal + DAL-G007/U035 | 完成 |
| T-0782 | PHX-G162 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0783 | PHX-G164 OpenAPI semantic deepen 架构门禁 | 完成 |
| T-0784 | ADR-0182 OpenAPI semantic deepen | 完成 |
| T-0785 | inventory mount/semantic + domain OpenAPI + Terminal + DAL-U036 | 完成 |
| T-0786 | PHX-G164 七步自审与最终验收 | 完成（Fully Accepted） |
| T-0787 | PHX-G160 WebAuthn live mint 架构门禁 | 完成 |
| T-0788 | ADR-0183 WebAuthn env-gated live mint | 完成 |
| T-0789 | ceremony mint + OpenAPI 1.3.6 + Terminal + DAL-G008/U037 | 完成 |
| T-0790 | PHX-G160 七步自审与最终验收 | 完成（Fully Accepted） |

## 运行

```bash
pip install -e ".[dev,persistence,api]"
python -m pytest -p no:cacheprovider
```
