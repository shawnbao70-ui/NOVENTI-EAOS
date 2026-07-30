# 海关与贸易中心（Customs Center）— Legacy Knowledge

**Evidence strength:** Medium for metadata catalogs; weak for operational declaration/clearance workflow  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

V15.1 Customs & Trade Center 提供海关模块、申报、清关、运输方式、Incoterms、HS Code、国家规则、贸易单证和历史的统一**元数据基础**。

必须保持以下边界：

- Customs Center 默认关闭；
- 框架页明确 Legacy customs/trade functions 仍为权威；
- 注册项普遍标为 `implemented=false` 或 `metadata_only`；
- 未实现申报引擎，也未替代进口/出口业务逻辑；
- Incoterms、国家和运输“登记”是目录种子及注册信息，不是可执行关税、责任划分、路线或承运流程。

本模块记录 customs_center 自身及与订单、交付、运输和贸易单证的概念交界，不把 GFIP/GTFIP 的独立智能或模拟路径并入 Customs Center 的已实现能力。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / UNKNOWN | EAOS 重写备注 |
|----|----------|----------|----------------|----------------|
| CU-R1 | Customs Center 注册进口、出口、申报、清关、运输、合规、贸易单证、HS Code、国家规则和 Incoterms 十个模块 | 注册初始化 | 模块均为元数据 | 不视为十个运行子系统 |
| CU-R2 | Center 默认关闭，Legacy 海关与贸易功能继续作为权威 | 框架页/配置 | 哪些实例启用 UNKNOWN；检索 `core/customs/types.py`、`apps/customs_center/` | 启用不等于替换 |
| CU-R3 | Incoterm 目录包含 EXW、FOB、FCA、CIF、CFR、DAP、DDP、CPT、CIP 和 Other | Incoterm 注册 | 仅名称目录，无责任、费用、风险转移地点规则 | 使用版本化 ICC 规则和地点 |
| CU-R4 | Incoterm 键必须属于预定义目录 | 校验 | `Other` 的自由文本细节 UNKNOWN | 其他条款需原文 |
| CU-R5 | 国家规则目录仅预置中国进口、美国出口、欧盟贸易合规三条示例 | 国家注册 | 未包含实际税则、禁限运、许可证或生效日期 | 不能当全球合规库 |
| CU-R6 | 运输方式目录仅预置海运、空运和陆运 | 运输注册 | 无承运人、航次、路线、港口、运价或跟踪 | “登记”仅分类元数据 |
| CU-R7 | 贸易单证目录包括商业发票、装箱单、提单、空运单、原产地证、检验证、保险证、进出口申报及其他 | 单证注册 | 所有类型 `implemented=false` | 文档类型不证明生成或申报 |
| CU-R8 | HS Code、税、关税、币种、港口、运输方式和贸易历史被列为特性 | 模块元数据 | 特性目录不等于规则引擎 | 分别建立权威数据源 |
| CU-R9 | 申报注册默认方向可为 import，状态 metadata_only | 申报元数据 | 无报关数据提交、回执、修改或撤销 | 建立申报状态机前不可生产使用 |
| CU-R10 | 清关注册初始状态可为 pending，但实现标志为 false | 清关元数据 | Pending 不是海关真实受理状态 | 避免把元数据状态当通关状态 |
| CU-R11 | 历史词汇包含注册、准备申报、提交清关和生成贸易单证 | 历史记录 | 是否由真实业务动作产生 UNKNOWN | 审计事件需与外部回执关联 |
| CU-R12 | Customs 与 Document Center 通过 `customs`、`shipping` 模块键及贸易单证概念相邻 | 文档归类 | 没有观察到自动桥接 | 文档事实与申报事实分开 |
| CU-R13 | 商业发票/装箱单等可由其他文档或 GFIP 路径产生 | 贸易业务 | 不代表已登记到 Customs Center | 需显式登记与版本引用 |
| CU-R14 | 订单、交付与 Customs Center 的自动触发关系 UNKNOWN | SO/DO 生命周期 | 已检索 `apps/customs_center/`、`apps/sales/`、`apps/inventory/` 未见中心调用 | 通过明确领域事件集成 |
| CU-R15 | 国家/Incoterm/运输元数据不自动计算 landed cost、关税或责任 | 报价/订单 | GFIP/GTFIP 有独立计算或智能逻辑，不属于 Center 主流程 | 不混淆模拟与合规决策 |
| CU-R16 | Customs Center 与 GTFIP 的 Incoterm 枚举不完全一致 | 跨域传递条款 | GTFIP 含 DPU，Center 用 Other 而不含 DPU | 建立版本化映射并拒绝无损失转换假设 |
| CU-R17 | GFIP 单证检查会按 Incoterm 增加要求 | 订单单证准备 | CIF/CFR 要求保险证；DDP 增加进口申报和海关单证 | 属 GFIP 规则，不是 Center 执行 |
| CU-R18 | LC 与订单 Incoterm 不一致会被标为高严重度差异 | LC 智能比对 | 属 GTFIP 辅助能力 | 决策仍需人工审核 |
| CU-R19 | 宪章禁止 AI 未经授权修改报关资料 | AI 海关辅助 | Customs Center 自身无修改工作流 | 将人类授权作为硬门 |

---

## 3. 流程

### 3.1 Customs Center 初始化

1. 确保八个 Customs 元数据表存在。
2. 注册十个海关业务模块。
3. 注册申报、清关、运输方式、Incoterm、HS Code、国家规则和贸易单证目录。
4. 写入基础历史元数据。
5. 框架页展示各目录数量和健康状态。
6. **流程止于注册与发现**，不执行实际报关或清关。

### 3.2 Incoterm 登记

1. 从预定义 Incoterm 键生成名称目录。
2. 持久化到 Incoterm 注册表。
3. 可按键解析或列出。
4. 责任边界、费用承担、风险转移地点、版本年份和合同适用性均 **UNKNOWN**；已检索 `core/customs/incoterm.py`、`apps/customs_center/incoterm_registry.py`。

### 3.3 国家规则登记

1. 初始化 CN、US、EU 三条示例规则。
2. 保存国家/区域键、名称和规则类型。
3. 标记为 metadata-only、未实现。
4. 未观察到税率、许可证、制裁、原产地或产品限制执行。

### 3.4 运输方式登记

1. 初始化海运、空运、陆运三类。
2. 保存运输键、方式和 shipping 模块归属。
3. 标记为 metadata-only、未实现。
4. 未观察到运输订单、承运人、航班/船期、港口、路线、费用、状态跟踪或签收。

### 3.5 GTFIP 订单级运输登记（相邻域）

1. GTFIP 可为订单建立物流记录，默认方式可为海运。
2. 相邻物流数据可包含订舱参考、承运人、箱号、船名/航次、航班号、跟踪号、运费、保险、ETA 和运输天数。
3. 该记录不属于 Customs Center 的 shipping registry；两者自动同步关系 **UNKNOWN**。

### 3.6 概念性贸易交界

1. 销售订单和交付单形成商业与物流来源。
2. Document/NDE 或 GFIP/GTFIP 可产生商业发票、装箱单等内容。
3. Customs Center 目录可标识所需贸易文档、Incoterm、国家、运输方式和 HS Code。
4. 实际申报、清关提交、外部回执、放行与交付回写均 **UNKNOWN / 未实现**。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| CU-V1 | Customs 记录必须有 `module_key` | Hard in validator |
| CU-V2 | `module_key` 必须属于十个模块键 | Hard in validator |
| CU-V3 | Incoterm 键必须属于十个目录值 | Hard in validator |
| CU-V4 | 贸易单证键必须属于预定义类型 | Hard in validator |
| CU-V5 | 国家键、名称和规则类型业务完整性 | Weak | 仓储字段存在，未见业务校验 |
| CU-V6 | HS Code 格式、层级和有效期 | UNKNOWN | 注册能力存在，执行校验未证实 |
| CU-V7 | Incoterm 必须携带命名地点和 ICC 版本 | Missing |
| CU-V8 | 国家规则按产品、方向、日期匹配 | Missing |
| CU-V9 | 运输登记必须有承运人/路线/港口 | Not implemented |
| CU-V10 | 申报提交前必须有完整单证 | Not implemented |
| CU-V11 | 清关状态必须来自海关回执 | Not implemented |
| CU-V12 | 报价/SO/DO 必须关联 Customs 记录 | UNKNOWN | 未见跨模块调用 |
| CU-V13 | 贸易文档版本与申报版本一致 | UNKNOWN | Customs 与 Document Center 无可靠桥接证据 |
| CU-V14 | Customs 权限与租户隔离 | UNKNOWN | 框架页和有限 API 未见完整业务 gate |
| CU-V15 | Customs/GTFIP Incoterm 枚举映射完整 | Missing | DPU 与 Other 存在差异 |
| CU-V16 | CIF/CFR/DDP 附加单证齐全 | Implemented in GFIP only | 不属于 Center validator |
| CU-V17 | LC Incoterm 与订单一致 | Advisory in GTFIP | 高严重度差异，不等于自动拒绝 |

---

## 5. 数据含义

### 5.1 Customs 元数据表

| Entity | 含义 |
|--------|------|
| `customs_registry` | 海关能力模块目录 |
| `customs_declarations` | 申报元数据，不是已提交报关单 |
| `customs_clearance` | 清关元数据，不是海关放行事实 |
| `trade_documents` | 贸易单证类型目录 |
| `hs_code_registry` | HS Code 元数据目录 |
| `country_rules` | 国家/区域规则元数据 |
| `incoterm_registry` | Incoterm 名称目录 |
| `customs_history` | Customs 元数据/事件历史 |

### 5.2 Incoterm 字段

| Field | 含义 |
|-------|------|
| `incoterm_key` | 小写规范键 |
| `incoterm_name` | EXW/FOB 等显示名称 |
| `implemented` | 是否有执行实现；当前为 false |
| `metadata` | 扩展元数据 |
| `version` | Center 软件版本，不等同 ICC Incoterms 年份 |

### 5.3 国家规则字段

| Field | 含义 |
|-------|------|
| `country_key` | 国家/区域键，如 cn、us、eu |
| `country_name` | 显示名称 |
| `rule_type` | import、export、trade_compliance 等分类 |
| `status` | 当前为 metadata_only |
| `implemented` | 当前为 false |

### 5.4 运输登记字段

| Concept | 含义 |
|---------|------|
| `shipping_key` | sea_freight、air_freight、land_transport |
| `method` | sea、air、land |
| `module_key` | shipping |
| `status` | metadata_only |
| `implemented` | false |

运输方式目录没有独立 `shipping` 数据表；其 facade 使用内存注册数据。持久化运输业务登记：**UNKNOWN / 未发现**。已检索 `core/customs/shipping.py`、`apps/customs_center/shipping_registry.py`、`database/v151_customs_center_schema.py`。

订单级运输登记存在于相邻 GTFIP 物流数据中，但与 Customs Center 无可确认的同步或外键关系。

### 5.5 贸易单证

目录中的 Commercial Invoice、Packing List、Bill of Lading、Air Waybill、Certificate of Origin、Inspection Certificate、Insurance Certificate、Export/Import Declaration 仅代表类型名称，不能证明文档已生成、签发或提交。

---

## 6. 状态词汇

| Status / flag | 使用位置 | 诚实含义 |
|---------------|----------|----------|
| `active` | Customs 模块注册 | 注册条目活动，不代表海关业务运行 |
| `metadata_only` | 申报、HS、国家规则、运输种子 | 只有元数据 |
| `pending` | 清关注册 | 概念初始状态，不是外部受理状态 |
| `completed` | Customs 历史默认 | 历史条目记录完成，不是清关完成 |
| `implemented=false` | 各注册项 | 无执行实现 |
| enabled by default = false | Customs Center | 默认不启用 |

历史事件词汇：customs_registered、declaration_prepared、clearance_submitted、trade_document_generated。由于无实际申报引擎，这些词汇不能单独证明外部海关已受理。

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `core/customs/types.py` | 模块、单证、Incoterm、特性、历史词汇及默认关闭 |
| `core/customs/customs.py` | 十模块注册与 `implemented=false` |
| `core/customs/incoterm.py` | Incoterm 目录 |
| `core/customs/country.py` | CN/US/EU 示例国家规则 |
| `core/customs/shipping.py` | 海/空/陆运输元数据 |
| `core/customs/trade_document.py` | 十种贸易单证目录 |
| `core/customs/validator.py` | 模块、Incoterm 和单证键校验 |
| `apps/customs_center/services.py` | 注册初始化与框架上下文 |
| `apps/customs_center/router.py` | 默认关闭、Legacy 权威和框架页声明 |
| `apps/customs_center/repository.py` | 注册持久化边界 |
| `database/v151_customs_center_schema.py` | 八个 Customs 元数据表及默认状态 |
| `docs/reports/V151_Volume016_Customs_Center_Report.md` | Foundation 范围与“无工作流替换”限制 |
| `apps/sales/` / `apps/inventory/` / `apps/customs_center/` | 订单/交付自动交界 UNKNOWN 的检索范围 |
| `document/nde_engine.py` | Incoterm/运输/贸易文档呈现的相邻能力 |
| `v15/gfip/` / `v15/gtfip/` | 独立贸易智能路径，不等于 Customs Center 运行实现 |
| `v15/gfip/documents.py` | Incoterm 驱动的附加单证检查 |
| `v15/gtfip/engines/trade.py` | GTFIP Incoterm 枚举及与 Center 的差异 |
| `v15/gtfip/engines/lc_ai.py` | LC 与订单 Incoterm 差异提示 |
| `v15/gtfip/repository.py` | 订单级物流登记字段 |
| `docs/constitution/volume-02-eaos/BOOK11.md` | AI 不得未经授权修改报关资料 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
