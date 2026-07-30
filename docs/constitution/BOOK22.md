# BOOK22 — 宪章附录

**仓库：** `NOVENTI-EAOS`  
**版本：** EAOS Charter v2.1  
**状态：** 生效

---

## 标题

宪章附录

## 目的

承载术语、冲突裁决、修订程序与版本记录规则。

## 范围

程序与附录。

## 当前状态

**规范正文生效**

## 未来扩展

术语、引用矩阵与修订程序随宪章版本持续维护。

---

## 一、规范术语

| 术语 | 含义 |
|------|------|
| EAOS | 企业 AI 操作系统 |
| Constitutional Kernel | 不可绕过的平台公共能力与基本法集合，不等同于单体部署层 |
| Core Kernel | Constitutional Kernel 中的可部署核心技术层 |
| Tenant | 数据、权限、配置与运营的强隔离边界 |
| Enterprise | 租户边界内的法人或组织主体，可具有集团层级 |
| Digital Employee / AI Employee | 永久、受治理、可派驻的 AI 劳动力身份 |
| Agent | AI Runtime 内执行规划、工具调用和受控动作的技术单元 |
| Digital Human | AI Employee 或 Agent 的可选人格化/多模态表现 |
| AI Assistant | 面向特定人或团队的协作角色 |
| Smart Terminal | 人类与 AI 协作的独立受治理交互层；不是业务真相源或 AI 主体 |
| Platform Runtime | 执行上下文、会话守卫、传播、调度与运行控制层 |
| Shared Platform Capability | 可被多个层复用且不属于业务包的公共平台能力 |
| Package | 扩展包（行业/业务/AI/集成） |
| Legacy | 只读遗留业务资产仓库 |
| High-impact Action | 可能显著影响法律、财务、安全、数据、客户、人员或不可逆状态的动作 |
| High-risk Operation | 由于威胁、权限、秘密或破坏半径需要强化安全控制的操作 |
| Commercially Sensitive Action | 影响合同、价格、结算、承诺或交易责任的动作 |
| Provenance | 数据、知识、建议或决策依据的可追溯来源链 |
| Derived Knowledge | 由模型、规则或推理生成且必须显式标注的知识 |
| AI Memory | Agent 执行上下文与保留状态，不等同于企业知识真相源 |
| Digital Twin State | 对企业事实的受治理、可追溯数字映像 |
| Enterprise Brain | 跨域形成有依据洞察和建议的智能层，不拥有未经批准的执行权 |
| Workflow | 审批、路由、任务、升级与补偿的唯一流程真相源 |
| Event | 已发生事实的不可变记录 |
| Fail Closed | 缺少身份、权限、上下文或有效证据时默认拒绝副作用 |

## 二、冲突裁决

1. 宪法书系内部：总纲（BOOK00）与平台（BOOK01）优先解释；专项书细化不得削弱总纲。  
2. 宪法 > 蓝图 > 标准 > ADR > 项目文档 > 遗留资产。  
3. 安全/合规要求与便利冲突时，安全/合规优先。  
4. 同一动作同时命中 High-impact、High-risk 或 Commercially Sensitive 分类时，适用最严格控制。  
5. “Constitutional Kernel”表达宪政能力归属；“Core Kernel”表达技术部署边界，两者不得混用以规避控制。  

## 三、统一工程顺序

Constitution → Ownership Classification → Blueprint → Standards → ADR → Interfaces → Data Models → Implementation → Testing → Documentation → Review → Release / Optimization。

## 四、修订程序

1. 提出修订案（说明冲突、影响面、迁移影响）。  
2. 架构与宪法一致性评审。  
3. 涉及产品战略/法律/商业/重大 UX 时暂停等待人类批准。  
4. 通过后更新书目版本与 CHANGELOG。  

## 五、版本规则

- 宪章版本：`EAOS Charter vMAJOR.MINOR`  
- 条文变更必须可追溯  
- 废弃条款标注废止日期与替代条款  
- 改变第一原则、权利义务或治理权力为 MAJOR 修订。  
- 增加定义、引用、解释性条款且不改变第一原则为 MINOR 修订。  

## 六、修订提案最小内容

1. 问题与冲突证据  
2. 受影响书目与条款  
3. 第一原则影响  
4. 架构、数据、迁移与兼容影响  
5. 安全、合规、商业与 UX 影响  
6. 人工批准记录（适用时）  
7. 二次合规审查结果  

## 七、跨书依赖矩阵

| 书目 | 规范主题 | 主要上位/协作书 |
|---|---|---|
| BOOK00 | 立宪总纲 | BOOK01、BOOK22 |
| BOOK01 | 平台原则 | BOOK00、BOOK22 |
| BOOK02 | 企业主权 | BOOK00、BOOK04、BOOK14、BOOK19 |
| BOOK03 | AI 劳动力 | BOOK00、BOOK10、BOOK15、BOOK17、BOOK19、BOOK23 |
| BOOK04 | 数据 | BOOK00、BOOK02、BOOK05、BOOK06、BOOK14 |
| BOOK05 | 安全 | BOOK00、BOOK01、BOOK04、BOOK06、BOOK19、BOOK23 |
| BOOK06 | 法律合规 | BOOK01、BOOK04、BOOK05、BOOK16、BOOK23 |
| BOOK07 | 商业 | BOOK01、BOOK02、BOOK08、BOOK20 |
| BOOK08 | Marketplace | BOOK05、BOOK07、BOOK10、BOOK11、BOOK20、BOOK23 |
| BOOK09 | 开发者 | BOOK01、BOOK05、BOOK08、BOOK21、BOOK22 |
| BOOK10 | AI 治理 | BOOK01、BOOK03、BOOK05、BOOK17、BOOK19、BOOK23 |
| BOOK11 | 行业 | BOOK06、BOOK07、BOOK08、BOOK14 |
| BOOK12 | UI/UX | BOOK01、BOOK05、BOOK10、BOOK13、BOOK15、BOOK16、BOOK23 |
| BOOK13 | Workflow | BOOK05、BOOK10、BOOK12、BOOK19、BOOK23 |
| BOOK14 | Knowledge | BOOK00、BOOK02、BOOK04、BOOK17、BOOK18、BOOK19、BOOK23 |
| BOOK15 | Digital Human | BOOK03、BOOK10、BOOK12、BOOK17、BOOK23 |
| BOOK16 | 全球治理 | BOOK01、BOOK04、BOOK05、BOOK06、BOOK12、BOOK23 |
| BOOK17 | Agent | BOOK03、BOOK10、BOOK13、BOOK14、BOOK15、BOOK19、BOOK23 |
| BOOK18 | Digital Twin | BOOK04、BOOK10、BOOK14、BOOK19、BOOK23 |
| BOOK19 | Constitutional Kernel | BOOK00、BOOK01、BOOK03–18、BOOK22、BOOK23 |
| BOOK20 | 平台经济 | BOOK04、BOOK05、BOOK07、BOOK08、BOOK23 |
| BOOK21 | 创新 | BOOK01、BOOK05、BOOK09、BOOK19、BOOK23 |
| BOOK22 | 术语、冲突与修订 | BOOK00、BOOK01、全专项书 |
| BOOK23 | Smart Terminal | BOOK00、BOOK01、BOOK03/05/06/08/10/12–22 |

## 关联文档

- [BOOK00.md](BOOK00.md)
- [BOOK01.md](BOOK01.md)
- [BOOK03.md](BOOK03.md)
- [BOOK19.md](BOOK19.md)
- [BOOK23.md](BOOK23.md)
- [../project/CHANGELOG.md](../project/CHANGELOG.md)
- [../project/ARCHITECTURE_DECISIONS.md](../project/ARCHITECTURE_DECISIONS.md)
