# Project Phoenix Roadmap v3

**状态：** 生效  
**日期：** 2026-07-18  
**依据：** BOOK00–BOOK23 Constitution Conformance Review 与 BOOK XXIII 二次合规审查  
**替代：** 原 PHX-007–PHX-015 顺序

## 路线原则

1. 已完成的 PHX-000–PHX-006 保留历史编号与验收结论。
2. 在继续 Kernel 深化前插入宪法与架构收敛门禁。
3. Smart Terminal 先立宪、再蓝图、再标准、最后实现。
4. Enterprise Brain 必须在 Knowledge、AI Runtime、Digital Twin 与 Event 基础成熟后进入。
5. Marketplace 必须晚于 Package、Smart Terminal extension 与平台经济治理。

## 新路线

| 里程碑 | 名称 | 核心交付 | 退出门禁 |
|---|---|---|---|
| PHX-G01 | Constitutional Convergence | 合规报告、Kernel 双层解释、AI taxonomy、BOOK22 矩阵 | 无未裁决 Critical |
| PHX-G02 | Smart Terminal Constitution | BOOK XXIII、二次合规审查 | 无第一原则冲突 |
| PHX-A03 | Architecture Realignment | EAOS 分层、Terminal Blueprint、ownership map | 每项能力唯一归属 |
| PHX-K07 | Organization Kernel | 企业层级、成员生命周期、跨组织治理 | L0–L2 + PostgreSQL |
| PHX-K08 | Permission Kernel | Policy、Scope、Delegation、Explain | 默认拒绝与决策审计 |
| PHX-K09 | Workflow Kernel | 定义版本、审批 SLA、补偿与升级 | 审批唯一真相源 |
| PHX-K10 | Knowledge Kernel | Provenance、Derived、Retention、授权检索 | 知识主权与来源完整 |
| PHX-P11 | Platform Runtime & Event | 异步投递、worker、lease、DLQ、区域韧性 | 可恢复、可观测、可重放 |
| PHX-A12 | AI Runtime & Agent | Agent 生命周期、工具治理、Memory、approval bridge | AI 不越权且可解释 |
| PHX-T13 | Smart Terminal Foundation | Shell、session、intent、preview、approval UX | 不持有业务真相 |
| PHX-B14 | Business Package Platform | Package manifest、surface/action contract、行业包 | 不分叉 Kernel |
| PHX-E15 | Enterprise Brain & Twin | 洞察、推理、孪生同步、置信度与偏差治理 | 建议与执行权分离 |
| PHX-M16 | Marketplace & Economy | 签名分发、审核、计量、账单与争议治理 | 商业/法律人工批准 |
| PHX-R17 | EAOS Release Train | SDK、API adapters、兼容策略、运营手册 | 全系统合规与发布评审 |
| PHX-G18 | API Gateway Foundation（Post-Foundation） | 最小 FastAPI、受信上下文派生 | 客户端不可提升安全上下文 |
| PHX-E19 | Domain Event Catalog Wiring（Post-Foundation） | K07–K10 同事务 outbox 接线 | 目录名合规且命令与 enqueue 原子 |
| PHX-G20 | Gateway Identity HTTP Surface（Post-Foundation） | Identity 五路由薄适配 | 网关不宿主业务规则 |
| PHX-G21 | Gateway Organization HTTP Surface（Post-Foundation） | Organization 租户面六路由 | 不开放平台上下文提升 |
| PHX-G22 | Gateway Permission HTTP Surface（Post-Foundation） | Permission 七路由薄适配 | Evaluate 不可冒充 principal |
| PHX-G23 | Gateway Workflow HTTP Surface（Post-Foundation） | Workflow 六路由薄适配 | 审批权限仍归 Kernel |
| PHX-G24 | Gateway Knowledge HTTP Surface（Post-Foundation） | Knowledge 六路由薄适配 | 出处与授权仍归 Capability |
| PHX-G25 | Gateway Platform Tenant Lifecycle（Post-Foundation） | 平台上下文 + 租户生命周期 | 租户面不可提升 platform_scope |
| PHX-G26 | Gateway Event Bus HTTP Surface（Post-Foundation） | Event 九路由薄适配 | HTTP subscribe 仅 no-op 登记 |
| PHX-G27 | Gateway Package Platform HTTP Surface（Post-Foundation） | Package 七路由薄适配 | 不开放 Marketplace 商业路径 |
| PHX-G28 | Gateway Twin & Brain HTTP Surface（Post-Foundation） | Twin/Brain 六路由薄适配 | authorize/execute 恒 fail-closed |
| PHX-G29 | Gateway AI Runtime HTTP Surface（Post-Foundation） | AI 八路由薄适配 | AI subject + 审批桥接仍归 Kernel |
| PHX-G30 | Gateway Smart Terminal HTTP Surface（Post-Foundation） | Terminal 十路由薄适配 | 审批真相归 Workflow；claimed_* 不可提升 |
| PHX-G31 | Gateway Domain Route Completions（Post-Foundation） | Workflow/Knowledge/Permission 扩展路由 | 薄适配；Org 扩展另切片 |
| PHX-G32 | Gateway Organization Route Completions（Post-Foundation） | Enterprise/Unit/Membership 扩展路由 | 薄适配；平台面不变 |
| PHX-G34 | Gateway Marketplace Technical HTTP（Post-Foundation） | Listing 生命周期 + pricing fail-closed | 商业政策仍另批；无 G33 |
| PHX-G35 | Smart Terminal Operator Shell（Post-Foundation） | `/terminal/` 静态壳 + 生命周期 UI | 无业务真相；品牌 UX / Extension 另批 |
| PHX-E20 | Permission DecisionRecorded Wiring（Post-Foundation） | Evaluate → outbox 摘要事实 | 高基数；无 Broker / 采样产品化 |
| PHX-E21 | Event Webhook Transport（Post-Foundation） | 可选 delivery_url + SSRF 基础 | Event Bus 拥有投递；签名另批 |
| PHX-G36 | Complete Terminal UI（Post-Foundation） | 四表面完整壳 | 无业务真相；OIDC/Extension 另批 |
| PHX-G37 | JWT/OIDC Trusted Context（Post-Foundation） | Bearer → ExecutionContext | **完成；HS256 Fully Accepted** |
| PHX-M17 | Marketplace Commercial Policy（Post-Foundation） | 定价/账单/分成/争议 | **完成；Foundation v1 Fully Accepted** |
| PHX-G38 | JWT JWKS / RS256（Post-Foundation） | RS256 + JWKS 密钥选择 | **完成；Fully Accepted** |
| PHX-E22 | Event Webhook HMAC（Post-Foundation） | 可选 signing_secret + v1 HMAC | **完成；Fully Accepted** |
| PHX-G39 | Terminal Extension Host（Post-Foundation） | 清单沙箱登记/激活/invoke | **完成；Foundation Fully Accepted** |

## 当前关键路径

```text
PHX-G01
  → PHX-G02
  → PHX-A03
  → PHX-K07/K08/K09/K10
  → PHX-P11
  → PHX-A12
  → PHX-T13
  → PHX-B14
  → PHX-E15
  → PHX-M16
  → PHX-R17
  → PHX-G18（Post-Foundation；已验收）
  → PHX-E19（Post-Foundation；已验收）
  → PHX-G20（Post-Foundation；已验收）
  → PHX-G21（Post-Foundation；已验收）
  → PHX-G22（Post-Foundation；已验收）
  → PHX-G23（Post-Foundation；已验收）
  → PHX-G24（Post-Foundation；已验收）
  → PHX-G25（Post-Foundation；已验收）
  → PHX-G26（Post-Foundation；已验收）
  → PHX-G27（Post-Foundation；已验收）
  → PHX-G28（Post-Foundation；已验收）
  → PHX-G29（Post-Foundation；已验收）
  → PHX-G30（Post-Foundation；已验收）
  → PHX-G31（Post-Foundation；已验收）
  → PHX-G32（Post-Foundation；已验收）
  → PHX-G34（Post-Foundation；技术已验收；商业仍开放）
  → PHX-G35（Post-Foundation；Operator Shell 技术壳已验收）
  → PHX-E20（Post-Foundation；DecisionRecorded 已验收）
  → PHX-E21（Post-Foundation；Webhook 传输已验收）
  → PHX-G36（Post-Foundation；Complete Terminal UI 已验收）
  → PHX-G37（Post-Foundation；JWT HS256 已验收）
  → PHX-M17（Post-Foundation；Foundation 商业政策已验收；支付/仲裁延后）
  → PHX-G38（Post-Foundation；JWKS/RS256 已验收；OIDC 登录页延后）
  → PHX-E22（Post-Foundation；Webhook HMAC 已验收）
  → PHX-G39（Post-Foundation；Extension Host Foundation 已验收）
```

## 并行边界

- K07–K10 可在共享 ExecutionContext / UoW / Event contract 稳定后有限并行。
- Terminal 设计可在 A12 期间推进，但实现不得早于 Runtime/Agent contract。
- Business Package manifest 可与 T13 后半程并行，业务包实现不得早于 Kernel 门禁。
- Enterprise Brain 与 Marketplace 不得抢跑。

## 里程碑统一自审

每个里程碑必须执行：

1. Architecture Review
2. Constitution Review
3. Cross-reference Review
4. Documentation Review
5. Consistency Review
6. Gap Analysis
7. Second-pass Review

## 人工批准门禁

- 第一原则或宪法位阶变化
- 产品战略与 Smart Terminal 核心定位
- 商业模式、定价、分成、计量
- 法律/合规政策
- 不可逆数据或部署架构
