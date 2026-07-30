# 商业 Incoterms 与海关交界

## Scope与证据强度

本页覆盖 Incoterms 在 Quote→SO→DO→Invoice 主链、NDE 文档、Customs Center 及 GFIP/GTFIP 平行链中的存在与传播。

- **强证据：** 商业表写入列、转换服务、NDE、Customs registry、GFIP/GTFIP 代码。
- **中证据：** `business_modules` 和工程报告用于确认边界，不作为运行事实替代品。
- **明确缺失：** 主商业链没有 Incoterms 持久字段，也没有 named place、风险转移或 ICC 2020 规则引擎。
- **交叉引用：** 海关治理资料仅作为边界证据；本页不复制治理正文。

## 业务规则

1. **IC-R01** Customs Center 注册 EXW、FOB、FCA、CIF、CFR、DAP、DDP、CPT、CIP、OTHER 十类键。
2. **IC-R02** 所有 Customs Incoterm registry 项均标记未实现，中心默认不启用。
3. **IC-R03** Customs Center 自述不替换 Legacy 贸易功能，只提供元数据基础。
4. **IC-R04** Customs validator 只校验键是否属于注册集合，未暴露为 Quote/SO 写入门。
5. **IC-R05** 报价商业头有币种、汇率、有效期、付款条款、交期和备注，没有 Incoterms 字段。
6. **IC-R06** Zero Duplicate 提供付款和交期默认值，不提供 Incoterms 默认。
7. **IC-R07** Quote 转 SO 传播客户、金额、行项和追溯 ID，不传播贸易术语。
8. **IC-R08** NDE 的 Incoterms 仅从额外上下文取得；报价打印没有注入，通常为空。
9. **IC-R09** `delivery_time` 是交期文本，不等于 Incoterms 的 named place。
10. **IC-R10** GFIP 订单拥有独立 Incoterms 字段，默认 FOB。
11. **IC-R11** 从 SO 创建 GFIP 订单不会继承商业主链术语，而是落到 GFIP 默认 FOB。
12. **IC-R12** GFIP 成本引擎对 EXW/FOB 将海运费和保险置零；这是 GFIP 启发式，不是主 Invoice 规则。
13. **IC-R13** GFIP 单证清单会按 CIF/CFR、DDP 增加保险或进口/海关单证。
14. **IC-R14** GFIP 关务策略根据术语给出清关责任文案，但不是完整报关执行引擎。
15. **IC-R15** GTFIP 支持集合含 DPU，而 Customs registry 用 OTHER 不含 DPU，两套词表不一致。
16. **IC-R16** NDE 有 port、freight、insurance 展示槽，但 Quote/SO/DO 没有对应持久化来源。
17. **IC-R17** 主链没有风险转移点字段或状态机。
18. **IC-R18** GFIP/GTFIP、NDE 和 Customs Center 三轨并列，不能互相替代为商业单据事实。

## 流程

### 主商业链

1. Quote 保存付款条款和交期，但不保存 Incoterms 或 named place。
2. Quote 打印构建 NDE 时未注入 Incoterms，模板条件通常不显示该行。
3. Quote 转 SO、SO 建 DO 均不传播术语、港口、运费或保险责任。
4. DO→AR/Invoice 也不读取 Incoterms；运费和保险展示默认零。

### Customs Center

1. 启动时按 feature flag 注册中心。
2. 服务把术语键 seed 到 registry，并将 implemented 保持为 false。
3. 页面与健康 API读取元数据；没有业务 CRUD 或主链写入。

### GFIP/GTFIP 平行链

1. SO 可建立 GFIP twin，但创建时使用默认 FOB，而非继承商业条款。
2. GFIP 根据术语形成成本、关务建议和单证清单。
3. GTFIP 可将 LC 识别术语与 GFIP 订单比较并提示差异。
4. 这些结果未回写 Quote/SO/DO/Invoice。

## 校验

1. **IC-V01** Customs 术语键必须属于十项 registry 集合。
2. **IC-V02** Customs 模块键必须属于中心模块集合。
3. **IC-V03** Trade Document 键必须属于文档类型集合。
4. **IC-V04** GFIP 创建请求的 Incoterms 是自由字符串，默认 FOB，没有枚举约束。
5. **IC-V05** GTFIP LC 比对忽略大小写，差异时给出修正/重谈建议。
6. **IC-V06** Quote validator 只做角色权限，不校验 Incoterms。
7. **IC-V07** Sales validator 没有领域级贸易术语规则。
8. **IC-V08** Finance validator 只校验金额，不校验术语或运费责任。
9. **IC-V09** NDE 只在术语有值时显示，属于展示条件而非必填。
10. **IC-V10** GFIP ready-to-ship 会检查按术语扩展后的单证是否 ready/verified。
11. **IC-V11** 主链缺少 named place 与术语组合校验。
12. **IC-V12** 主链缺少大小写归一、版本（2010/2020）和 ICC 责任规则校验。

## 数据含义

| 数据 | 含义 |
|---|---|
| `quotes.payment_term` | 付款条件，不是贸易术语 |
| `quotes.delivery_time` | 交期文本，不是 named place |
| `quotes.currency` / `exchange_rate` | 商业币种与汇率 |
| `nde.doc_info.incoterms` | 文档展示槽，默认空 |
| `nde.doc_info.delivery` | 交期/交付文本展示 |
| `nde.financial.freight` | 文档运费展示槽，默认零 |
| `nde.financial.insurance` | 文档保险展示槽，默认零 |
| `nde.logistics.port` | 港口展示槽，无主链数据库来源 |
| `incoterm_registry.incoterm_key` | Customs Center 小写术语键 |
| `incoterm_registry.implemented` | 是否有真实业务实现；当前为 false |
| `gfip_orders.incoterms` | GFIP 平行履约链术语，默认 FOB |
| `gfip_shipments.origin_port` | GFIP 装运港 |
| `gfip_shipments.destination_port` | GFIP 目的港 |
| `country_plugin.incoterms_default` | 国家插件默认术语槽，当前为空 |
| clearance strategy | GFIP 对责任/清关方式的启发式建议 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `implemented=false` | Customs registry 只有元数据 |
| `metadata_only` | Shipping/Customs 能力仅注册层 |
| feature flag false | Customs Center 默认关闭 |
| `healthy` | Registry 数量符合预期，不代表业务实现 |
| `active` | GFIP 订单默认状态 |
| `sales_order` | GFIP 初始阶段 |
| `pending` | GFIP shipment 或文档待处理 |
| `ready` / `verified` | GFIP 单证准备/核验状态 |
| LC discrepancy | GTFIP 发现信用证与订单术语不一致 |

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | Quote 写入列无 Incoterms | 强 | `apps/quotation/repository.py` |
| E2 | Quote→SO 不传播 Incoterms | 强 | `apps/sales/services.py`、`v15/business_lifecycle/workflow.py` |
| E3 | NDE 仅从 extra 接收术语 | 强 | `document/nde_engine.py` |
| E4 | 报价打印未注入术语 | 强 | `apps/quotation/services.py` |
| E5 | Customs 注册十项且 implemented false | 强 | `core/customs/incoterm.py` |
| E6 | Customs Center 默认关闭 | 强 | `core/customs/types.py` |
| E7 | 工程报告确认 metadata only | 中 | `docs/reports/V151_Volume016_Customs_Center_Report.md` |
| E8 | GFIP 默认 FOB 且不从 SO 继承 | 强 | `v15/gfip/platform.py`、`v15/gfip/repository.py` |
| E9 | GFIP 按术语调整成本和单证 | 强 | `v15/gfip/cost_engine.py`、`v15/gfip/documents.py` |
| E10 | NDE 模板只条件显示术语 | 强 | `templates/documents/components/doc_info.html` |
| E11 | business modules 未定义术语契约 | 中 | `business_modules/quotation.md`、`business_modules/sales.md` |
| E12 | 未找到 risk transfer 实现 | 强（缺失证据） | `apps/`、`core/customs/`、`document/` |

## UNKNOWN

1. **运行迁移是否给 Quote 增加 Incoterms 列 UNKNOWN/未发现。** 已查 `database/upgrade_patch.py` 与 Legacy DDL。
2. **V14 巨型残留是否另有术语表单 UNKNOWN。** 已查 quotation apps、模板和关键 Legacy 路径，未全量运行实例。
3. **Invoice 路径是否在某部署注入 extra.incoterms UNKNOWN。** 已查 Finance 服务、路由和 NDE。
4. **Customs validator 是否被外部未纳入模块间接调用 UNKNOWN。** 已查全库引用。
5. **目标 governance/customs 文档路径 UNKNOWN。** Legacy 根下未发现 `governance/` 目录；已用 Customs 报告作只读交叉证据。
6. **客户默认 Incoterms 字段 UNKNOWN。** 已查默认解析、Customer/Quotation 关键路径。
7. **生产环境是否打开 Customs Center feature flag UNKNOWN。** 代码默认 false，未检查部署配置。
8. **GFIP 与 Customs registry 的未来统一规则 UNKNOWN。** 已查 Shipment 模块说明和 Vol016 报告。
9. **ICC 2020 版本与 named place 标准化 UNKNOWN。** 已查 core/customs、GFIP/GTFIP 和文档组件。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\core\customs\`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\workflow.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gfip\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\gtfip\`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\manifest\`
- `H:\Workspace\EZAM_CRM - 9.0\database\upgrade_patch.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V151_Volume016_Customs_Center_Report.md`
