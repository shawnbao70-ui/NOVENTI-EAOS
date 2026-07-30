# BOOK XXIII — Smart Terminal 宪法 / Smart Terminal Constitution

**仓库：** `NOVENTI-EAOS`  
**版本：** EAOS Charter v2.1  
**规范层级：** 专项宪法（受 BOOK00 / BOOK01 约束）  
**状态：** 生效

---

## 第一编 — 定义与使命

### 第 1.1 条

Smart Terminal 是 NOVENTI EAOS 中人类与 AI 协作的独立受治理交互层。

### 第 1.2 条

Smart Terminal 的使命是将意图、上下文、建议、权限、审批、执行结果与证据以安全、透明、可审计的方式呈现给操作者。

### 第 1.3 条

Smart Terminal 不是 AI 主体、业务真相源、权限引擎、审批引擎、企业知识库、Enterprise Brain 或 Marketplace。

### 第 1.4 条

Smart Terminal 不得直接读写数据库、绕过 API/Runtime/Kernel，或在终端代码中复制业务包与内核规则。

---

## 第二编 — 架构归属

### 第 2.1 条

Smart Terminal 独立于 Constitutional Kernel、Core Kernel、Platform Runtime、Shared Platform Capability、Business Package、Marketplace 与 Enterprise Brain。

### 第 2.2 条

Smart Terminal 通过版本化 API、Runtime gateway、Event contract 与声明式 Package surfaces 消费平台能力。

### 第 2.3 条

Terminal Shell 归 Smart Terminal；身份、权限、流程、审计与业务状态分别归其宪政真相源。

### 第 2.4 条

每项 Terminal capability 必须在实现前完成 architectural ownership classification。

---

## 第三编 — Human–AI Interaction

### 第 3.1 条

操作者必须能够区分人类输入、AI 建议、Agent 计划、Digital Human 表现、系统事实与最终执行结果。

### 第 3.2 条

AI 建议不得伪装为已执行事实；预测、推导与不确定内容必须明确标识。

### 第 3.3 条

Smart Terminal 必须展示当前 AI Employee、Agent、协作角色、权限范围与责任主体。

### 第 3.4 条

Human Responsibility 不因自然语言、语音、多模态或自动补全而转移。

---

## 第四编 — Identity, Session and Device Trust

### 第 4.1 条

所有 Terminal session 必须绑定可验证的 Subject、Tenant、Session、Device trust 状态与 Correlation ID。

### 第 4.2 条

Subject、Tenant、Session 与 platform scope 必须由受信认证边界派生，客户端不得自行声明或提升。

### 第 4.3 条

租户切换必须显式、可见、可审计，并重新验证目标租户资格；禁止静默跨租户继承上下文。

### 第 4.4 条

高风险操作必须依据风险等级执行强化验证；设备不可信时默认拒绝高风险副作用。

### 第 4.5 条

Session 到期、撤销、主体不匹配或上下文不完整时必须失败关闭，且不得执行目标操作。

---

## 第五编 — Context and Tenant Isolation

### 第 5.1 条

Security-sensitive context 在传播中不可被 Terminal extension、Package surface、Agent 或用户输入覆盖。

### 第 5.2 条

Terminal 的标签页、面板、历史、缓存、剪贴板辅助与 AI memory 必须保持租户隔离。

### 第 5.3 条

跨租户比较、聚合或治理视图必须使用显式平台授权，并标注数据来源与作用域。

### 第 5.4 条

终端历史不得成为跨租户知识泄漏通道。

---

## 第六编 — Intent, Command and Tool Execution

### 第 6.1 条

受控执行遵循：

```text
Intent
  → Resolve Context
  → Produce Plan / Preview
  → Permission Evaluation
  → Human Approval（如适用）
  → Commit
  → Result Verification
  → Audit / Event
```

### 第 6.2 条

Terminal 必须区分建议、预览、草稿与 Commit；任何建议不得仅因展示或确认焦点变化而自动提交。

### 第 6.3 条

Agent 工具调用必须经 AI Runtime 与 Permission 求值；Terminal 不得直接调用未声明工具。

### 第 6.4 条

破坏性、不可逆、高影响、高风险或商业敏感命令必须在 Commit 前展示作用域、预期影响、资源与批准状态。

### 第 6.5 条

批量操作必须显示目标数量、租户边界、失败策略与幂等标识。

### 第 6.6 条

执行结果必须由权威 API/Kernel 状态验证，不得仅以客户端乐观状态宣称成功。

---

## 第七编 — Permission and Human Approval

### 第 7.1 条

Smart Terminal 不计算最终权限；Permission Kernel 是授权决策真相源。

### 第 7.2 条

Smart Terminal 不维护平行审批状态；Workflow Kernel 是审批与路由真相源。

### 第 7.3 条

批准必须绑定主体、动作、资源、作用域、计划版本与有效期；修改计划后原批准不得复用。

### 第 7.4 条

同一动作命中多个风险分类时适用 BOOK22 的最严格控制原则。

### 第 7.5 条

拒绝、过期、撤销或不匹配的批准必须阻断 Commit。

---

## 第八编 — Knowledge, Memory and Provenance

### 第 8.1 条

用于建议或决策的事实、知识、策略与工具输出必须具备可展示的 provenance。

### 第 8.2 条

Derived knowledge、预测、置信度与缺失证据必须显式标注，不得伪装为原始事实。

### 第 8.3 条

AI Memory 是执行上下文，不等同于 Enterprise Knowledge；持久化与提升为知识必须经过 Knowledge governance。

### 第 8.4 条

Smart Terminal 不得把秘密、凭证、令牌或受限数据写入普通历史、日志或 AI memory。

### 第 8.5 条

用户必须能够查看建议依据，并在依据不足时选择不执行。

---

## 第九编 — Digital Human and Representation

### 第 9.1 条

Digital Human 是 AI Employee 或 Agent 的可选表现，不拥有独立权限或责任。

### 第 9.2 条

Digital Human 必须明确标识其 AI 性质、代表对象与授权边界，不得冒充未经授权的人类。

### 第 9.3 条

语音、形象、情绪与人格化不得掩盖风险、审批状态、置信度或责任主体。

### 第 9.4 条

表现层变化不得改变底层 Subject、Agent、Permission 或 Workflow 状态。

---

## 第十编 — Package and Marketplace Surfaces

### 第 10.1 条

Business Package 仅可通过声明式 surface/action contract 扩展 Smart Terminal。

### 第 10.2 条

Terminal extension 必须声明权限、数据范围、工具、事件、网络、存储与合规影响。

### 第 10.3 条

Marketplace 分发的 extension 必须签名、版本化、可撤销、可回滚，并运行在沙箱与 capability boundary 内。

### 第 10.4 条

Extension 不得修改 Terminal Shell 的安全控制、隐藏审批、覆盖租户标识或绕过审计。

### 第 10.5 条

行业定制不得分叉 Smart Terminal 的宪政安全基线。

---

## 第十一编 — Enterprise Brain and Digital Twin

### 第 11.1 条

Enterprise Brain 可向 Smart Terminal 提供有依据的洞察、建议、模拟与计划，但不因此取得执行权。

### 第 11.2 条

Enterprise Brain 输出必须标注来源、推理类型、置信度、作用域与适用时间。

### 第 11.3 条

Digital Twin State 是受治理映像，不是默认写入业务系统的授权。

### 第 11.4 条

基于孪生的模拟与实际 Commit 必须明确分离；从模拟转为执行须重新求值权限和审批。

---

## 第十二编 — Security, Privacy and Compliance

### 第 12.1 条

安全与合规优先于交互便利、响应速度与个性化。

### 第 12.2 条

秘密必须脱敏；复制、导出、下载、屏幕共享与外部跳转须服从策略控制。

### 第 12.3 条

适用法律、数据驻留、跨境与租户配置必须在相关操作前求值。

### 第 12.4 条

AI 法律、财务、医疗或其他受监管建议必须展示适当限制，不得冒充未经授权专业意见。

### 第 12.5 条

安全事件必须可检测、可阻断、可响应、可追溯；Terminal 不得允许关闭安全证据。

---

## 第十三编 — Accessibility, Internationalization and Resilience

### 第 13.1 条

无障碍、多语言、时区、区域格式与键盘可操作性是 Smart Terminal 基线。

### 第 13.2 条

风险、审批与错误不得仅依赖颜色、声音或单一感官通道表达。

### 第 13.3 条

离线或弱网模式必须明确标识陈旧状态；缺少在线授权验证时不得执行高影响副作用。

### 第 13.4 条

区域故障时优先保持租户隔离、证据完整与安全降级，不得静默切换到不合规区域。

---

## 第十四编 — Audit, Observability and Incident Response

### 第 14.1 条

Intent、Plan、Permission Decision、Approval、Commit、Result 与 Failure 必须通过 Correlation ID 关联。

### 第 14.2 条

审计记录必须区分人类输入、AI 生成、系统推导与最终执行主体。

### 第 14.3 条

可观测数据必须最小化并脱敏；遥测不得成为秘密、业务数据或跨租户泄漏通道。

### 第 14.4 条

终端安全事件应支持会话撤销、extension 隔离、凭证轮换与可控恢复。

---

## 第十五编 — Evolution, Compatibility and Prohibited Designs

### 第 15.1 条

Smart Terminal 公共 surface、action、command 与 event contract 必须版本化。

### 第 15.2 条

破坏性变更必须具备 ADR、迁移路径、回滚策略、兼容窗口与人工批准（适用时）。

### 第 15.3 条

禁止以下设计：

1. 在 Terminal 中保存业务真相或实现业务规则引擎。
2. 直接数据库访问或绕过 API/Runtime/Kernel。
3. 客户端声明或提升安全上下文。
4. 未经 Permission 求值或 Workflow approval 执行副作用。
5. 未签名 extension 执行特权代码。
6. 跨租户共享历史、缓存、memory 或剪贴板数据。
7. 隐藏 AI 身份、风险、审批、来源或执行状态。
8. 把 Enterprise Brain 建议或 Digital Twin 模拟当作已授权执行。

---

## 第十六编 — 合宪验收

Smart Terminal capability 只有同时满足以下条件才可进入实现：

1. 已完成 architectural ownership classification。
2. 已有 Blueprint、Standards、ADR、Interface 与 Data Model（适用时）。
3. 已验证身份、租户、权限、审批、审计与 Runtime 边界。
4. 已覆盖失败关闭、跨租户、过期会话、拒绝批准、秘密泄漏与 extension 沙箱负面契约。
5. 已完成无障碍、国际化、安全、合规和文档评审。
6. 已通过 Constitution Review 与 Second-pass Review。

## 关联书目

- [BOOK00.md](BOOK00.md)
- [BOOK01.md](BOOK01.md)
- [BOOK03.md](BOOK03.md)
- [BOOK05.md](BOOK05.md)
- [BOOK06.md](BOOK06.md)
- [BOOK08.md](BOOK08.md)
- [BOOK10.md](BOOK10.md)
- [BOOK12.md](BOOK12.md)
- [BOOK13.md](BOOK13.md)
- [BOOK14.md](BOOK14.md)
- [BOOK15.md](BOOK15.md)
- [BOOK16.md](BOOK16.md)
- [BOOK17.md](BOOK17.md)
- [BOOK18.md](BOOK18.md)
- [BOOK19.md](BOOK19.md)
- [BOOK20.md](BOOK20.md)
- [BOOK21.md](BOOK21.md)
- [BOOK22.md](BOOK22.md)
