# Implementation Log

**Program:** Project Phoenix  
**Repository:** `NOVENTI-EAOS`

---

## Title

Implementation Chronology

## Purpose

Record what was executed, when, and under which milestone — documentation and later code.

## Scope

Work performed inside `NOVENTI-EAOS` only.

## Current Status

Active.

## 日志

### 2026-07-20 — PHX-G81 OIDC Claim→Role JWT Mint Gate

- 固化 ADR-0100；claim→eaos_roles mint；契约 621

### 2026-07-20 — PHX-G80 OIDC amr/acr Auth Context Gate

- 固化 ADR-0099；amr/acr 认证上下文门禁；契约 614

### 2026-07-20 — PHX-G79 OIDC Required Claims Gate

- 固化 ADR-0098；OIDC 必填声明门禁；契约 608

### 2026-07-20 — PHX-G78 Tenant IdP Federation Issuer Priority

- 固化 ADR-0097；绑定 priority + Alembic 0028；契约 603

### 2026-07-20 — PHX-G77 Tenant IdP Federation Policy Matrix

- 固化 ADR-0096；联邦矩阵只读 + Terminal；契约 595

### 2026-07-20 — PHX-G76 Deploy Region Identity Foundation

- 固化 ADR-0095；部署区域身份标签；契约 587

### 2026-07-20 — PHX-G75 OIDC Refresh KMS Key Provider

- 固化 ADR-0094；kms http|aws|gcp|azure；契约 580

### 2026-07-20 — PHX-G74 OIDC Refresh Fernet Key Provider

- 固化 ADR-0093；env|file 密钥提供方；契约 576

### 2026-07-20 — PHX-G73 Service Mesh AuthorizationPolicy Foundation

- 固化 ADR-0092；opt-in Istio AuthorizationPolicy；契约 572

### 2026-07-20 — PHX-G72 Service Mesh Traffic CRD Foundation

- 固化 ADR-0091；opt-in Istio VS+DR；契约 568

### 2026-07-20 — PHX-G71 Service Mesh Policy CRD Foundation

- 固化 ADR-0090；opt-in Istio PeerAuthentication；契约 564

### 2026-07-20 — PHX-G70 OIDC Refresh Re-encrypt On Read

- 固化 ADR-0089；读时迁主密钥；契约 560

### 2026-07-20 — PHX-G69 Tenant IdP Federation Terminal Ops

- 固化 ADR-0088；Terminal Admin 联邦薄操作；契约 557

### 2026-07-20 — PHX-G68 JWT Tenant IdP Federation Enforcement

- 固化 ADR-0087；租户面 JWT 联邦强制；契约 553

### 2026-07-20 — PHX-G67 Tenant IdP Federation SQL Adapter

- 固化 ADR-0086；federation store memory|sql + Alembic 0027；契约 547

### 2026-07-20 — PHX-G66 Tenant IdP Federation Binding

- 固化 ADR-0085；租户↔issuer 薄 API + 可选 OIDC 强制；契约 544

### 2026-07-20 — PHX-G65 OIDC Refresh Fernet Key Rotation

- 固化 ADR-0084；MultiFernet 旧密钥解密窗口；契约 540

### 2026-07-20 — PHX-G64 OIDC Refresh Token Field Encryption

- 固化 ADR-0083；Fernet 字段加密可选；契约 536

### 2026-07-20 — PHX-G63 OIDC Refresh Binding SQL Adapter

- 固化 ADR-0082；refresh store memory|sql + Alembic 0026；契约 532
- 七步自审 Fully Accepted；支付清算另批；令牌加密延后

### 2026-07-20 — PHX-G62 Platform IdP Registry Terminal Ops

- 固化 ADR-0081；Admin IdP 注册表薄操作 + platform 头；契约 529
- 七步自审 Fully Accepted；支付清算另批；组织联邦 UI 延后

### 2026-07-20 — PHX-G61 OIDC Refresh + RP-Logout

- 固化 ADR-0080；refresh/logout API + runtime revoke + Terminal 按钮；契约 525
- 七步自审 Fully Accepted；支付清算另批；联邦 UI / SQL refresh 延后

### 2026-07-19 — PHX-G60 OIDC Discovery → Registry Writeback

- 固化 ADR-0079；Discovery→registry upsert + sync API；契约 520
- 七步自审 Fully Accepted；支付清算另批；联邦 UI / 写 env 延后

### 2026-07-19 — PHX-G59 Service Mesh Foundation

- 固化 ADR-0078；Helm mesh 注入接线 + MESH.md；契约 515
- 七步自审 Fully Accepted；支付清算另批；控制面/网格 CRD 延后

### 2026-07-19 — PHX-G58 KEDA Foundation

- 固化 ADR-0077；Helm ScaledObject + KEDA.md；与 HPA/VPA 互斥；契约 510
- 七步自审 Fully Accepted；支付清算另批；Mesh / operator 安装延后

### 2026-07-19 — PHX-G57 IdP Registry SQL Adapter

- 固化 ADR-0076；`EAOS_IDP_REGISTRY_STORE` + SQLAlchemy 仓储接线；复用 0025；契约 505
- 七步自审 Fully Accepted；支付清算另批；Mesh / Discovery 写回延后

### 2026-07-19 — PHX-G56 Multi-IdP Write Registry

- 固化 ADR-0075；平台 IdP 注册表 + 校验合并；Alembic 0025；契约 500
- 七步自审 Fully Accepted；支付清算另批；SQL 适配器 / Mesh 延后

### 2026-07-19 — PHX-G55 Multi-IdP Status UI

- 固化 ADR-0074；`/v1/auth/idp/status` + Admin 探针；契约 496
- 七步自审 Fully Accepted；支付清算另批；写注册表 / 联邦策略 UI 延后

### 2026-07-19 — PHX-G54 VPA Foundation

- 固化 ADR-0073；Helm VPA 模板 + VPA.md；与 HPA 互斥；契约 493
- 七步自审 Fully Accepted；支付清算另批；VPA 组件安装 / Mesh / 多 IdP UI 延后

### 2026-07-19 — PHX-G53 HPA Foundation

- 固化 ADR-0072；Helm HPA 模板 + HPA.md；契约 488
- 七步自审 Fully Accepted；支付清算另批；metrics-server 安装 / VPA / Mesh / 多 IdP UI 延后

### 2026-07-19 — PHX-G52 Ingress / TLS Foundation

- 固化 ADR-0071；Helm Ingress 模板 + INGRESS.md；契约 483
- 七步自审 Fully Accepted；支付清算另批；Controller 安装 / Mesh / 多 IdP UI 延后

### 2026-07-19 — PHX-G51 Kubernetes Helm Foundation

- 固化 ADR-0070；`deploy/helm/eaos` + HELM.md；契约 478
- 七步自审 Fully Accepted；支付清算另批；Ingress / 多区域 / 多 IdP UI 延后

### 2026-07-19 — PHX-G50 Docker Compose Foundation

- 固化 ADR-0069；`deploy/docker` + COMPOSE.md；契约 472
- 七步自审 Fully Accepted；支付清算另批；K8s/Helm / 多区域 / 多 IdP UI 延后

### 2026-07-19 — PHX-G49 Production Deploy Topology

- 固化 ADR-0068；`PRODUCTION_TOPOLOGY.md` + Runbook 扩展；契约 466
- 七步自审 Fully Accepted；支付清算另批；Compose/K8s / 多区域 / 多 IdP UI 延后

### 2026-07-19 — PHX-G48 OIDC Discovery → JWKS Wire

- 固化 ADR-0067；`maybe_wire_discovery_jwks` + Bearer 接线；契约 461
- 七步自审 Fully Accepted；支付清算另批；多 IdP UI / 写回 env 延后

### 2026-07-19 — PHX-G47 OIDC IdP Discovery

- 固化 ADR-0066；Discovery 填充 authorize/token；issuer 匹配；契约 453
- 七步自审 Fully Accepted；支付清算另批；多 IdP UI / Discovery→JWKS 延后

### 2026-07-19 — PHX-G46 JWT Denylist

- 固化 ADR-0065；denylist JSON/URL + verify 后检查；契约 446
- 七步自审 Fully Accepted；支付清算另批；实时吊销总线 / Discovery 延后

### 2026-07-19 — PHX-G45 JWT Multi-Issuer JWKS

- 固化 ADR-0064；JwtIssuerBinding + 校验路径；kid miss 刷新；契约 442
- 七步自审 Fully Accepted；支付清算另批（已确认）；吊销列表/IdP UI 延后

### 2026-07-19 — PHX-G44 Terminal Extension Signature Cryptography

- 固化 ADR-0063；extension signing + activate 接线；契约 438
- 七步自审 Fully Accepted；JWKS 发行方 / 支付清算延后

### 2026-07-19 — PHX-M18 Marketplace Package Signature Cryptography

- 固化 ADR-0062；marketplace.signing + Service 接线；契约 435
- 七步自审 Fully Accepted；Extension 强制验签 / 支付清算延后

### 2026-07-19 — PHX-G43 Terminal Extension Worker Runtime

- 固化 ADR-0061；demo-worker + UI 启停；bridge channel allowlist
- 契约 431；七步自审 Fully Accepted；CDN/SharedWorker/签名密码学延后

### 2026-07-19 — PHX-G42 Terminal Extension iframe + CSP

- 固化 ADR-0060；extension_runtime 桥接/CSP；demo-panel + UI 宿主 + Gateway 中间件
- 契约 428；七步自审 Fully Accepted；Worker / CDN / 签名密码学延后

### 2026-07-19 — PHX-G41 Terminal Extension SQL Persistence

- 固化 ADR-0059；Extension SQL 表/仓储/Transactional；Alembic 0024
- 契约 425；七步自审 Fully Accepted；iframe runtime / 热加载延后

### 2026-07-19 — PHX-G40 OIDC Authorization Code Login

- 固化 ADR-0058；PKCE login/callback + EAOS JWT 签发；Terminal Bearer 应用
- 契约 424；七步自审 Fully Accepted；refresh/logout / 多 IdP Discovery 延后

### 2026-07-19 — PHX-G39 Terminal Extension Host

- 固化 ADR-0057；沙箱注册/激活/invoke；Gateway + UI Extensions 表面
- 契约 421；七步自审 Fully Accepted；iframe runtime / SQL 延后

### 2026-07-19 — PHX-E22 Event Webhook HMAC

- 固化 ADR-0056；订阅 signing_secret + 投递签名头；Alembic 0023
- 契约 418；七步自审 Fully Accepted；密钥轮换/加密存储延后

### 2026-07-19 — PHX-G38 JWT JWKS / RS256

- 固化 ADR-0055；`verify_token` RS256/JWKS + HS256 分流
- 契约 415；七步自审 Fully Accepted；OIDC 登录页延后

### 2026-07-19 — PHX-M17 Marketplace Commercial Policy

- 固化 ADR-0054；实现定价/发票/分成/争议 + Alembic 0022 + Gateway
- 契约 412；支付/外部仲裁显式延后；七步自审 Fully Accepted

### 2026-07-19 — PHX-G37 JWT/OIDC Trusted Context

- 固化 ADR-0053；`auth_jwt` + context Bearer 优先派生
- 契约 410；七步自审 Fully Accepted（HS256）；OIDC 登录/JWKS 延后

### 2026-07-19 — PHX-G36 Complete Terminal UI

- 固化 ADR-0052；扩展 `smart_terminal/ui` 为四表面完整壳
- 契约 405；登记 M17/G37 已批准待启

### 2026-07-18 — PHX-E21 Event Webhook Transport

- 固化 ADR-0051；实现 url_safety / webhook poster；订阅表 delivery_url
- Gateway 透传；完整回归 402 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-E20 Permission DecisionRecorded Wiring

- 固化 ADR-0050；Permission.evaluate → outbox `permission.decision.recorded`
- 完整回归 398 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G35 Smart Terminal Operator Shell

- 固化 ADR-0049；实现 Operator Shell 与 `/terminal/` 挂载
- 完整回归 397 + PostgreSQL 19；技术壳七步自审 Fully Accepted

### 2026-07-18 — PHX-G34 Gateway Marketplace Technical HTTP Surface

- 固化 ADR-0048；实现 Marketplace 技术九路由与序列化；替换 pricing stub
- 完整回归 393 + PostgreSQL 19；技术面七步自审 Fully Accepted（商业仍开放）

### 2026-07-18 — PHX-G32 Gateway Organization Route Completions

- 固化 ADR-0047；实现 Organization 企业/单元/成员扩展 HTTP
- 完整回归 393 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G31 Gateway Domain Route Completions

- 固化 ADR-0046；实现 Workflow/Knowledge/Permission 扩展 HTTP
- 完整回归 387 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G30 Gateway Smart Terminal HTTP Surface

- 固化 ADR-0045；实现 Terminal 十路由与序列化；共享 Workflow 接线
- 完整回归 383 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G29 Gateway AI Runtime HTTP Surface

- 固化 ADR-0044；实现 AI 八路由与序列化；共享 Workflow/Knowledge 接线
- 完整回归 378 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G28 Gateway Twin & Brain HTTP Surface

- 固化 ADR-0043；实现 Twin/Brain 六路由与 fail-closed 执行路径
- 完整回归 374 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G27 Gateway Package Platform HTTP Surface

- 固化 ADR-0042；实现 Package 七路由与序列化
- 完整回归 369 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G26 Gateway Event Bus HTTP Surface

- 固化 ADR-0041；实现 Event 九路由与序列化；subscribe = HTTP no-op 登记
- 完整回归 365 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G25 Gateway Platform Tenant Lifecycle

- 固化 ADR-0040；实现平台上下文派生与三条租户生命周期路由
- 完整回归 358 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G24 Gateway Knowledge HTTP Surface

- 固化 ADR-0039；实现 Knowledge 六路由与序列化
- archive/share HTTP 延后；完整回归 352 + PostgreSQL 19
- 七步自审 Fully Accepted

### 2026-07-18 — PHX-G23 Gateway Workflow HTTP Surface

- 固化 ADR-0038；实现 Workflow 六路由与序列化
- signal/cancel/compensate/escalate HTTP 延后；完整回归 346 + PostgreSQL 19
- 七步自审 Fully Accepted

### 2026-07-18 — PHX-G22 Gateway Permission HTTP Surface

- 固化 ADR-0037；实现 Permission 七路由与序列化
- Evaluate 禁止 body 冒充 principal；deprecate/delegate HTTP 延后
- 完整回归 339 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G21 Gateway Organization HTTP Surface

- 固化 ADR-0036；实现租户面 Organization 六路由
- 平台租户生命周期 HTTP 显式延后；契约覆盖跨租户与 ineligible membership
- 完整回归 331 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G20 Gateway Identity HTTP Surface

- 固化 ADR-0035；实现 `api/gateway/routers/identity` 与错误/序列化适配
- 五路由契约 + G18 回归；默认内存 IdentityService
- 完整回归 322 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-E19 Domain Event Catalog Wiring

- 固化 ADR-0034；目录命名归一；实现 DomainEventEmitter
- 四域 Transactional 同 session 写 outbox；DecisionRecorded 延后
- 契约测试覆盖命名、enqueue 与 dispatch；调整 P11/PG 计数断言适配目录事实
- 完整回归 314 + PostgreSQL 19；七步自审 Fully Accepted

### 2026-07-18 — PHX-G18 API Gateway Foundation

- 固化 ADR-0033 与 Architecture Gate；实现 `api/gateway`
- 受信头派生 `ExecutionContext`；拒绝 body 提升；商业定价 HTTP 失败关闭
- 契约测试 5 项；完整回归 305 + PostgreSQL 19（无新 Alembic）
- 七步自审 Fully Accepted；全量 OpenAPI 路由与 OIDC 仍延后

### 2026-07-18 — PHX-R17 EAOS Release Train

- 固化 ADR-0032 与 Release Manifest；版本升至 `0.2.0`
- 交付 SDK / API adapter registry / Compat / Ops Runbook
- 发布契约测试覆盖 Manifest、OpenAPI 清单、商业 fail-closed
- 完整回归 300 + PostgreSQL 19；七步自审 Fully Accepted（Phoenix Foundation）

### 2026-07-18 — PHX-M16 Marketplace Technical Foundation

- 固化 ADR-0031；实现落点 `eaos_platform.marketplace`
- 交付签名上架治理与租户技术获取；商业 API 失败关闭
- 实现 TransactionalMarketplaceService + Alembic `0020_marketplace_m16`
- Alembic `0020` + PostgreSQL 19 项；完整回归 294 passed
- 技术七步自审 Accepted；焦点转入 PHX-R17；商业政策仍待另批

### 2026-07-18 — PHX-E15 Enterprise Brain & Twin

- 固化 ADR-0030 与 Architecture Gate；实现 `eaos_platform.twin` / `brain`
- 交付 Twin Snapshot 与 advisory Insight；执行路径失败关闭
- 实现 TransactionalTwin/Brain + Alembic `0019_enterprise_brain_twin_e15`
- 补齐 OpenAPI / 状态机与契约测试
- Alembic `0019` + PostgreSQL 18 项；完整回归 285 passed
- 七步自审 Fully Accepted；下一 M16 需商业/法律人工批准

### 2026-07-18 — PHX-B14 Business Package Platform

- 固化 ADR-0029 与 Architecture Gate；实现落点 `eaos_platform.package`
- 交付 Manifest / Install / Surface·Action Resolve 与 sample_ops 制品
- 实现 TransactionalPackageService + Alembic `0018_package_platform_b14`
- 补齐 OpenAPI / 状态机与契约测试
- Alembic `0018` + PostgreSQL 17 项；完整回归 274 passed
- 七步自审 Fully Accepted，焦点转入 PHX-E15

### 2026-07-18 — PHX-T13 Smart Terminal Foundation

- 固化 ADR-0028 与 Architecture Gate；实现落点 `smart_terminal/`
- 交付 Session / Intent / Preview / Approval UX / Commit 回执
- 实现 TransactionalSmartTerminalService + Alembic `0017_smart_terminal_t13`
- 补齐 OpenAPI / 状态机与契约测试
- Alembic `0017` + PostgreSQL 16 项；完整回归 263 passed
- 七步自审 Fully Accepted，焦点转入 PHX-B14

### 2026-07-18 — PHX-A12 AI Runtime & Agent

- 固化 ADR-0027 与 Architecture Gate；实现落点 `runtime/ai`
- 交付 Agent Run、工具治理、Memory、Workflow approval bridge
- 实现 TransactionalAIRuntimeService + Alembic `0016_ai_runtime_a12`
- 补齐 OpenAPI / 状态机与契约测试
- Alembic `0016` + PostgreSQL 15 项；完整回归 251 passed
- 七步自审 Fully Accepted，焦点转入 PHX-T13

### 2026-07-18 — PHX-P11 Event Delivery / Outbox

- 固化 ADR-0026 与 Architecture Gate
- 实现 Outbox enqueue、worker lease、退避重试与 DLQ 重放
- 扩展 TransactionalEventBus 与 Alembic `0015_event_outbox_dlq`
- 补齐 OpenAPI / 状态机 / 观测 stats 与契约测试
- Alembic `0015` + PostgreSQL 14 项；完整回归 240 passed
- 七步自审 Fully Accepted，焦点转入 PHX-A12

### 2026-07-18 — PHX-K10 Knowledge Shared Capability

- 固化 ADR-0025 与 Architecture Gate；实现落点 `eaos_platform.knowledge`
- 交付 Entity / Link / Provenance / Retention / Share / 关键词 Search
- 实现 TransactionalKnowledgeService + Alembic `0014_knowledge_k10`
- 补齐 OpenAPI / 状态机 / 事件目录与契约测试
- Alembic `0014` + PostgreSQL 13 项；完整回归 229 passed
- 七步自审 Fully Accepted，焦点转入 PHX-P11

### 2026-07-18 — PHX-K09 Workflow Kernel

- 固化 ADR-0024 与 Architecture Gate
- 修复内存仓储共享引用导致的乐观锁误报
- 实现绑定扩展、SLA、升级硬化、补偿最小语义
- Alembic `0013` + PostgreSQL 12 项；完整回归 215 passed
- 七步自审 Fully Accepted，焦点转入 PHX-K10

### 2026-07-18 — PHX-K08 Permission Kernel

- 关闭 Slice A：条件未解析 deny、Principal fail-closed、可见性与乐观锁
- 实现 Policy 生命周期、Scope 层级与 deny-overrides Evaluate
- 实现 Delegation 与父链有效性；Explain 证据持久化
- Alembic `0012` + PostgreSQL 11 项集成通过；完整回归 201 passed
- 七步自审 Fully Accepted，焦点转入 PHX-K09

### 2026-07-18 — PHX-K07 Organization Kernel

- 三路审查 Organization 宪政要求、实现与测试/持久化差距
- 修复 suspended Tenant 成员写入、Unit self/cycle、ended Membership 修改等 P0
- 建立独立 Enterprise domain/ORM/repository 与 primary Enterprise 原子创建
- 为 Tenant、Enterprise、Unit、Membership 接入数据库原子乐观锁
- 实现 Enterprise / Unit / Membership 状态机和 active dependency 门禁
- 通过 Enterprise FOR UPDATE 锁解决生命周期与并发成员/层级写竞态
- 补齐 0010→0011 populated migration、三元 Enterprise FK、跨 Enterprise active Membership 约束
- 三轮最终复核逐项关闭阻断，最终 Fully Accepted
- 完整回归 184/184；专用 PostgreSQL 10/10

### 2026-07-18 — PHX-G02 / PHX-A03 Compliance Closure

- 根据两轮独立只读审查逐项关闭所有 Critical 与 Medium 宪法/架构一致性发现
- 将 BOOK00–BOOK23 元数据、规范效力、风险 taxonomy、AI taxonomy 与跨书关系统一到 Charter v2.1
- 补齐 Enterprise Brain 最低宪政锚点、Marketplace extension 规则与 Smart Terminal/BOOK12 层级
- 裁决 Knowledge 为 Shared Platform Capability、Core Kernel 仅治理端口
- 明确 Event Bus Shared ownership 与 `kernel/event_bus/` 兼容路径
- 同步 Roadmap v3 编号、工程顺序、入口 README、架构与项目状态
- 新增自动化文档契约并通过 8/8，完整回归 163/163；最终复核结论 Fully Compliant
- 完成 PHX-A03 唯一 ownership 验收，下一门禁为 PHX-K07

### 2026-07-18 — Project Phoenix Constitutional Convergence

- 并行精读 BOOK00–BOOK22，建立术语、依赖、冲突与 Smart Terminal gap 清单
- 生成 Constitution Conformance Report 与独立 Canvas 分析视图
- 人工裁决 Kernel 双层解释、AI taxonomy 与 Smart Terminal ownership
- 重构 Roadmap v3，插入 PHX-G01/G02/A03 治理门禁
- 生成 BOOK23、ADR-0021、Smart Terminal Blueprint 并对齐 EAOS Architecture
- 启动第二轮只读合规与引用复核

### 2026-07-18 — PHX-006 Identity Kernel 人工验收

- 人工批准 PHX-006
- 固化 `160 passed`、PostgreSQL integration 与零 lint 验收基线
- 当时记录的下一阶段为旧编号 PHX-007 Organization Kernel；Roadmap v3 已将其替换为 PHX-G02 → PHX-A03 → PHX-K07

### 2026-07-18 — PHX-006 Identity IDL and State Machines

- 新增 `docs/api/identity.openapi.yaml` OpenAPI 3.1 规范
- API `/v1` 版本化并使用 Bearer 认证边界描述
- 禁止客户端声明 ExecutionContext 安全字段，仅开放 correlation ID
- 新增 `IDENTITY_STATE_MACHINES.md` 与 YAML/ref/security 契约测试
- 完整回归 160 passed

### 2026-07-18 — PHX-006 Identity ↔ Organization L2

- 增加 MembershipEligibility Protocol 与 fail-closed 默认实现
- SQL eligibility 校验 Subject active、tenant 归属与 AI active assignment
- TransactionalOrganizationService 接入真实 Identity 资格检查
- 新增跨域共享 UoW Coordinator，原子结束 membership 并改派 AI
- 完整回归 155 passed

### 2026-07-18 — PHX-006 AI Profile Persistence

- 建立 AIEmployeeProfile 领域模型与 Repository 端口
- 将注册时未持久化的 capabilities_profile / owner_policy 落入独立表
- 实现 GetAIProfile / UpdateAIProfile 与数据库原子乐观锁
- 新增 ORM、Alembic `0010`、内存/SQLite/PostgreSQL 契约
- 完整回归 152 passed

### 2026-07-18 — PHX-006 AI Assignment Semantics

- 将 AssignAIToTenant 收紧为 AI 全局 active 独占
- ReassignAI 对历史多活状态失败关闭，非 archive 要求现有派驻与目标租户
- INHERIT 新 assignment 持久化 predecessor self-reference
- ARCHIVE 支持省略 to_tenant_id
- 新增 ADR-0017、Alembic `0009` 与内存/SQLite/PostgreSQL 契约
- 完整回归 150 passed

### 2026-07-18 — PHX-006 Platform Identity Governor Persistence

- 建立 PlatformIdentityGovernorGrant 领域模型与 Repository 端口
- 实现 bootstrap 首授权、持久 Governor 授权/撤销与权限切换
- 新增 ORM partial unique index 与 `0008_platform_identity_governors`
- TransactionalIdentityService 重组后仍从数据库恢复治理权限
- PostgreSQL 验证 Governor 记录与 AI 注册/改派授权
- 完整回归 148 passed

### 2026-07-18 — PHX-006 Identity Credential Lifecycle

- 将 Session 创建契约改为必填 credential_id
- 实现 Credential active / revoked / expiry / tenant / subject 验证
- 实现幂等 RevokeCredential 与无 secret ValidationView
- 在 ORM 与 `0007_session_credential_binding` 中记录会话凭证来源
- PostgreSQL 验证 Bind → Validate → Session → Revoke → Deny
- 完整回归 146 passed

### 2026-07-18 — PHX-006 Identity Session Boundary Closure

- 定义 Identity 诊断错误与 Runtime 非泄露映射边界
- 新增 SessionValidationView 与 ValidateSession
- 对跨租户/主体不匹配统一隐藏为 SESSION_NOT_FOUND
- RuntimeExecutor 在 operation 前强制会话验证且缺验证器失败关闭
- PostgreSQL 验证 Create → Validate → Revoke → Deny
- 完整回归 143 passed

### 2026-07-18 — PHX-005 Runtime Foundation

- 人工批准复用唯一 ExecutionContext 与显式 Runtime.execute 网关
- 创建 runtime context / executor / observability 包并纳入 setuptools
- 对安全字段传播、snapshot 版本、非法入站与 operation 零执行做 fail-closed
- 增加 R-01～R-10 共 15 项自动化契约
- 完整回归 138 passed，包含 PostgreSQL migration 与 Kernel 往返
- 技术验收通过并获人工批准，PHX-005 Foundation 正式完成

### 2026-07-18 — PHX-004 真实 PostgreSQL 技术验收

- EDB 系统安装器无响应后，改用官方二进制 ZIP 建立用户级隔离实例
- 在端口 55432 创建专用 `eaos_test` 并安全保存用户级连接配置
- 执行 Alembic 完整 upgrade / downgrade 与所有 Kernel 往返契约
- 修复无 ORM relationship 时 Workflow / Event 子记录抢先 flush 的真实外键错误
- PostgreSQL 套件 4 passed；完整套件 123 passed
- 技术退出标准全部满足并获人工确认，PHX-004 正式完成

### 2026-07-18 — PHX-004 Foundation 条件验收

- 从 Contract Test Plan、Persistence Ports 与 ADR-0012 汇总退出标准
- 验证 ADR-0008 在 SQLAlchemy Transactional Workflow 路径生效
- 验证持久化 Membership 角色不会绕过 Permission 默认拒绝
- 预写五域 + Event 的真实 PostgreSQL 往返集成契约
- 本地验证为 119 passed / 1 PostgreSQL skipped
- 保留最终里程碑状态给真实 PostgreSQL 结果与人工确认

### 2026-07-18 — PHX-004 Transactional Event Bus

- 分离持久化 Subscription Metadata 与进程内 Handler Registry
- 实现 Event / Subscription / Delivery ORM 与 `0006_event_bus`
- 实现 SQLAlchemyEventRepository 与 TransactionalEventBus
- 在同一 UoW 中组合 Event、Permission Decision 与 Audit
- 记录失败尝试、错误类别与重放后的成功状态
- 当前验证为 116 passed / 1 PostgreSQL skipped

### 2026-07-18 — PHX-004 Transactional Workflow

- 实现 Workflow Definition / Instance / Task / History / Signal Receipt ORM
- 创建 `0005_workflow` 并通过完整离线 PostgreSQL DDL 编译
- 实现 SQLAlchemyWorkflowRepository 与 TransactionalWorkflowService
- 让 Workflow 与 Permission Repository 共享 Session / AuditLog / UoW
- 验证启动、审批、默认拒绝审计与幂等 Signal
- 当前验证为 112 passed / 1 PostgreSQL skipped

### 2026-07-18 — PHX-004 Transactional Permission

- 实现 Permission 两表 ORM 与 `0004_permission`
- 补齐 Grant 显式 save 端口和租户绑定 SQL Repository
- 实现 TransactionalPermissionService 与 Grant Administrator 注入
- 验证默认拒绝、授权/撤销、跨租户拒绝与无授权无残留
- 当前验证为 108 passed / 1 PostgreSQL skipped

### 2026-07-18 — PHX-004 Transactional Organization

- 实现 Organization 三表 ORM 与 `0003_organization`
- 增加父组织单元、Membership 到 OrgUnit 的租户复合外键
- 补齐 Tenant / Membership 显式 save 端口
- 实现 SQLAlchemyOrganizationRepository 与 TransactionalOrganizationService
- 当前验证为 103 passed / 1 PostgreSQL skipped

### 2026-07-18 — PHX-004 Platform Identity Governor

- 为 IdentityService 增加显式 platform_governors
- 注册 AI 与跨租户改派同时校验 platform scope 和 Governor 主体
- 将 Governor 配置传入 TransactionalIdentityService 内部组合
- 增加未授权内存/SQL 事务负向测试
- 当前验证为 98 passed / 1 PostgreSQL skipped

### 2026-07-18 — PHX-004 PostgreSQL Integration Harness

- 检测本机 Docker、psql、pg_isready 与测试 URL，确认均不可用
- 新增只允许 `eaos_test*` 数据库的破坏性安全门
- 编写真实迁移链、Repository、Audit 与 partial index 集成契约
- 无连接时模块显式 skip，不用 SQLite 冒充 PostgreSQL 通过
- 当前验证为 96 passed / 1 skipped

### 2026-07-18 — PHX-004 Transactional Identity

- 实现事务型 Identity composition facade
- 每条命令动态注入租户绑定 Repository 与 AuditLog
- 成功结果显式 commit，失败结果依赖 UoW 自动 rollback
- 映射 IntegrityError 与 SQLAlchemyError 为稳定 KernelResult
- 增加 Domain/Audit 原子提交和提交失败原子回滚测试
- 契约测试扩展至 96 项并全部通过

### 2026-07-18 — PHX-004 Shared Audit / Identity SQL Repositories

- 实现 Domain ↔ ORM 显式转换与租户作用域查询
- 实现 Audit append/list 与 Identity read/add/save 适配器
- 修复 Credential tenant_id、跨租户错误码与 UTC 恢复边界
- 通过临时 SQL Engine 验证提交、读取、更新与租户隔离
- 契约测试扩展至 89 项并全部通过

### 2026-07-18 — PHX-004 SQLAlchemy Unit of Work

- 实现 PostgreSQL Engine 与 Session Factory
- 实现显式 commit / rollback / close 生命周期
- 增加未提交、异常、嵌套进入与提交后访问负向契约
- 保持 Service 暂不假装拥有数据库原子性，待 Repository 接线
- 契约测试扩展至 83 项并全部通过

### 2026-07-18 — PHX-004 Shared Audit / Identity ORM

- 实现 AuditEvent、Subject、ExternalRef、Credential、Session、AIAssignment ORM
- Credential Domain Model 增加显式 tenant_id
- 创建 `0002_shared_audit_identity` 迁移与数据库级约束
- 用 Alembic offline 模式验证完整 PostgreSQL DDL
- 契约测试扩展至 77 项并全部通过

### 2026-07-18 — PHX-004 SQL Foundation

- 安装并声明 SQLAlchemy 2 / Alembic / psycopg 持久化依赖组
- 建立 infrastructure persistence 包与统一 metadata
- 创建 Alembic 配置、模板与空基线修订
- 增加 PostgreSQL 驱动白名单及配置 fail-closed 测试
- 契约测试扩展至 69 项并全部通过

### 2026-07-18 — PHX-004 Persistence Ports

- 为五个 Kernel 域建立运行时可校验的 Repository Protocol
- Service 构造函数改为依赖端口并保留内存默认适配器
- 新增 AuditLog 与 Unit of Work Protocol
- 增加提交、无提交回滚、异常回滚和适配器结构契约
- 契约测试扩展至 63 项并全部通过

### 2026-07-18 — PHX-004 持久化技术决策

- 经人工战略确认选择 PostgreSQL + SQLAlchemy 2 + Alembic
- 新增 ADR-0012，定义分层、事务、迁移与租户约束
- 下一实施边界为 Repository / Unit of Work Protocol

### 2026-07-18 — PHX-004 Workflow 幂等与 Event 可靠性决策

- 实现定义名称/版本唯一性冲突保护
- 实现持久化边界兼容的 Signal Receipt 内存模型
- 实现 Signal 请求指纹、幂等重试与冲突复用拒绝
- 新增 ADR-0011，确定生产 Event 的持久化、at-least-once 与 DLQ 语义
- 契约测试扩展至 54 项并全部通过

### 2026-07-18 — PHX-004 Event Bus 垂直切片

- 实现 ADR-0006 不可变事件信封与内存事件总线
- 实现 Permission 控制、租户隔离、幂等投递与重放审计
- 收紧 payload 为 JSON 安全且深度不可变
- 契约测试扩展至 51 项并全部通过

### 2026-07-18 — PHX-004 Workflow 与跨域契约

- 实现 Workflow 内存状态机并接入 Permission 求值
- 落地 AI 审批闸门，审批绑定主体/动作/资源
- 增加 Organization ↔ Permission 边界测试
- 契约测试扩展至 42 项并全部通过

### 2026-07-18 — PHX-004 Organization / Permission 垂直切片

- 实现 Organization 内存仓储与服务层
- 实现 Permission 默认拒绝、授权、撤销、解释与审计
- 增加平台治理与 Grant 管理主体的显式授权边界
- 契约测试扩展至 31 项并全部通过
- 清理构建生成物；未引入数据库或 Web 框架

### 2026-07-18 — PHX-004 Identity 垂直切片（代码）

- 实现 shared + identity（内存）
- 契约测试通过
- 遵循失败关闭、租户隔离、凭证不回传、审计留痕

### 2026-07-18 — PHX-004 契约层（上下文/错误码/持久化 ADR）

- 接受 ADR-0009
- 发布执行上下文契约与错误码总表
- 未开始 Python 实现

### 2026-07-18 — PHX-004 Foundation 文档与骨架

- 完成 Kernel 数据模型草案、Org/Workflow 接口、契约测试计划
- 建立 kernel 模块目录与 tests/contracts 占位
- 未编写实现代码；未修改遗留仓库

### 2026-07-18 — PHX-001 收官 + ADR + 接口细化

- 完成 BOOK00–BOOK22 工作宪章基线
- 接受 ADR-0006/0007/0008
- 发布 Identity/Permission 接口细化文档
- 未实现业务代码；未修改遗留仓库

### 2026-07-18 — PHX-001 宪法充实与接口大纲

- 只读参考遗留宪章迁移文本，写入 `NOVENTI-EAOS` 工作宪章
- 完成核心书目与关键治理书目正文
- 发布 Kernel 接口大纲，明确 PHX-004 进入门槛
- 未创建 Python / FastAPI / SQL / 业务模块

### 2026-07-18 — PHX-002 / PHX-003 文档基线

- 仅在 `NOVENTI-EAOS` 内扩展架构蓝图与开发标准
- 未修改遗留仓库
- 未创建实现代码
- 产出：可执行的架构与标准基线，供后续接口定义使用

### 2026-07-18 — PHX-000 工作区迁移

- Stopped all writable work targeting Legacy CRM repository
- Confirmed agent workspace root: `H:\Workspace\NOVENTI-EAOS`
- Initialized empty EAOS repository structure (documentation and directory placeholders only)
- Created governance, blueprint, standards, and architecture starter documents
- Did **not** create Python, FastAPI, SQL, APIs, business modules, or database tables
- Did **not** copy Legacy code
- Did **not** modify, move, rename, or delete any Legacy files

## Future Expansion

Append entries for every milestone checkpoint.

## Related Documents

- [CHANGELOG.md](CHANGELOG.md)
- [MIGRATION_STATUS.md](MIGRATION_STATUS.md)
- [PROJECT_STATUS.md](PROJECT_STATUS.md)
