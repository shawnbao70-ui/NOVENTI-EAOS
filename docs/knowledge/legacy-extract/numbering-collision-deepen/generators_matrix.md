# 业务编号生成器矩阵（Generators Matrix）— Legacy Knowledge

**Evidence strength:** Strong for active generators and schema; mixed for runtime ownership of parallel DO/legacy helpers  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页对照 Opportunity、Requirement、Quote、SO、DO 与 Sample 的活动编号算法。核心发现是：各模块没有共享序列表；算法混用全表 `COUNT(*)+1`、秒级时间戳和源实体 ID 派生。相同前缀也不代表共享 sequence。

交叉引用 `../document-ops/numbering.md`，并纠正“Quote 当日计数”的易误读：日期进入格式，但序号来自全表 count。

## 2. Generator Matrix

| Entity | Active format | Sequence source | Persisted column | Constraint | Parallel/difference |
|--------|---------------|-----------------|------------------|------------|---------------------|
| Opportunity | `OPP-YYYYMMDD-NNNN` | whole-table COUNT+1 | `opportunity_code` | UNIQUE | intelligence OPP UUID is advisory object, not same table |
| Requirement | `REQ-YYYYMMDD-NNNN` | whole-table COUNT+1 | `requirement_code` | UNIQUE | custom caller code allowed |
| New Quote | `QTYYYYMMDDNNN` | whole-table COUNT+1 | `quote_no` | no observed UNIQUE | date prefix + global count |
| Copy Quote | `QTYYYYMMDDHHMMSS` | wall clock second | `quote_no` | no observed UNIQUE | differs from new Quote |
| Sample→Quote | `QTYYYYMMDDHHMMSS` | wall clock second | `quote_no` | no observed UNIQUE | same timestamp family |
| SO | `SO{quote_id:04d}` | source quote PK | `so_no` | no observed UNIQUE | application guard by quote_id |
| DO Sales path | `DOYYYYMMDDHHMMSS` | wall clock second | `do_no` | no observed UNIQUE | create_delivery_order |
| DO Inventory path | `DO{so_id:04d}` | source SO PK | `do_no` | no observed UNIQUE | `_legacy_convert_do` |
| Sample | `SPYYYYMMDDHHMMSS` | wall clock second | `sample_no` | no observed UNIQUE | helper family may use `SM` elsewhere |

## 3. Business Rules

| ID | Rule | Evidence / consequence |
|----|------|------------------------|
| GM-R1 | OPP 默认编号由 lifecycle repository `next_code` 生成 | caller 可显式覆盖 |
| GM-R2 | REQ 使用同一 `next_code`，但独立表和前缀 | 不共享数字空间 |
| GM-R3 | `next_code` 读取全表 count，不按日期过滤 | 日期变更不重置序号 |
| GM-R4 | OPP/REQ 格式包含 UTC 日期和四位序号 | 时区与其他本地 datetime 路径不同 |
| GM-R5 | 新 Quote 用本地当前日期 + 全表 quote count+1 | 不是当日 count |
| GM-R6 | Quote 复制不用主 generator | 改用秒级时间戳 |
| GM-R7 | Sample→Quote 也用秒级时间戳 | 同秒可与 copy 冲突 |
| GM-R8 | Quotation utils 的时间戳 helper 未成为新建主路径 | 工具存在不等于 authority |
| GM-R9 | SO number 由 quote PK 派生 | 不依赖 SO 自增或共享 sequence |
| GM-R10 | SO guard 查询 quote_id，不查询 so_no | 编号不是防重权威 |
| GM-R11 | Sales DO 使用秒级时间戳 | 同秒不同 SO 可同号 |
| GM-R12 | Inventory DO 使用 SO PK 派生 | 同 SO 重复调用可同号 |
| GM-R13 | 两个 DO 格式可共存于同一列 | 外部解析不能假设长度 |
| GM-R14 | Sample 主写入使用 `SP` + 秒级时间戳 | 无随机/计数尾码 |
| GM-R15 | 状态变化不重新编号 | 编号是创建快照 |
| GM-R16 | ID 派生号只在源 ID 唯一时格式唯一 | 重复业务转换仍需 DB/应用 guard |
| GM-R17 | prefix/padding 是模块内文案契约 | 不构成数据库 sequence |
| GM-R18 | OPP intelligence 的 UUID OPP object 与 lifecycle OPP row 不同 | 不应混入 persisted sequence |
| GM-R19 | NDE/Print 可派生展示号 | 不证明数据库存在对应单据 |
| GM-R20 | EAOS 不得把各前缀拼接为一个全局编号域 | 无共享 sequence 证据 |
| GM-R21 | Quote count 未使用已有 scoped-count helper | 多租户下仍读取全表 cardinality |
| GM-R22 | Sales/runtime 中另有 SO/Sample timestamp helpers | 未接主写入，构成潜在第三格式而非权威 |

## 4. Process

1. OPP/REQ：读取表 count→拼 UTC date/prefix→insert→DB UNIQUE 最终裁决。
2. New Quote：读取 quotes count→拼 local date→insert。
3. Copy/Sample Quote：直接取当前秒→insert。
4. Convert SO：使用 quote ID 拼号→应用层查 quote_id→insert。
5. Create DO：根据入口选择 timestamp 或 SO ID 派生→insert。
6. Add Sample：当前秒拼 `SP`→insert。

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| GM-V1 | OPP code 唯一 | DB UNIQUE |
| GM-V2 | REQ code 唯一 | DB UNIQUE |
| GM-V3 | Quote number 唯一 | Missing |
| GM-V4 | SO number 唯一 | Missing |
| GM-V5 | DO number 唯一 | Missing |
| GM-V6 | Sample number 唯一 | Missing |
| GM-V7 | count+1 必须原子 | Missing |
| GM-V8 | timestamp 同秒必须去重/retry | Missing |
| GM-V9 | SO/DO source 应仅转换一次 | Partial application guards |
| GM-V10 | caller-supplied OPP/REQ code 必须格式规范 | Missing |
| GM-V11 | 所有模块使用统一 timezone | Missing |
| GM-V12 | parallel generators 必须收敛 | Missing |

## 6. Data Semantics

| Field / concept | Honest meaning |
|-----------------|----------------|
| `opportunity_code` | lifecycle Opportunity 业务显示号 |
| `requirement_code` | lifecycle Requirement 业务显示号 |
| `quote_no` | Quote 对外/搜索/打印编号，格式多轨 |
| `so_no` | Quote ID 派生的 SO 显示号 |
| `do_no` | timestamp 或 SO ID 派生的 DO 号 |
| `sample_no` | Sample timestamp 显示号 |
| table count | 当前行数快照，不是 sequence |
| date segment | 创建时日期文本，不保证日内序列 |
| timestamp second | 秒级时间文本，不保证唯一 |
| source PK | ID 派生号的输入 |
| prefix | 模块/文档类别提示 |
| padding | 最小显示宽度，不限制更大数字 |
| DB UNIQUE | OPP/REQ 的最终冲突保护 |
| application guard | SO 等转换前存在性检查 |
| document_number | NDE 展示值或派生值 |
| UUID OPP advisory ID | intelligence object 标识，非 lifecycle code |

## 7. State Vocabulary

| Term | Meaning |
|------|---------|
| generated | 应用已计算，尚未证明 insert 成功 |
| persisted | 编号已写业务表 |
| duplicate | 同一业务号多行或 insert 冲突 |
| display-derived | 打印时临时拼接 |
| source-derived | 由上游 PK 拼号 |
| timestamp-derived | 由当前秒拼号 |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 非 Enterprise 启动下 DO owner | sales/inventory/platform routers、bootstrap |
| OPP/REQ 自定义 code 的 UI 允许范围 | lifecycle routes/templates/repository |
| Quote count 是否 tenant scoped | quotation repository、tenant query、schema |
| 生产数据库是否手工给业务号加 unique | runtime/database migrations |
| 时间戳生成是否受 server timezone/clock drift | datetime/config/deployment docs |
| 同秒批量 Sample/DO/Quote 的生产碰撞 | tests/scripts/reports |
| SM helper 是否仍有活动调用 | runtime generator/facade/full-repo callers |
| NDE 派生 Invoice/Statement 号是否落库 | document/print/finance |
| SO/DO padding 超四位后的外部兼容 | templates/integrations/reports |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `v15/business_lifecycle/repository.py` | next_code、OPP/REQ create |
| `database/business_lifecycle_schema.py` | OPP/REQ UNIQUE |
| `apps/quotation/services.py` | New/Copy/Sample Quote generators |
| `apps/quotation/repository.py` | global quote count 与 insert |
| `apps/quotation/utils.py` | 未接新建主路径的 timestamp helper |
| `apps/quotation/quote_pages.py` | legacy Quote generators |
| `apps/sales/services.py` | SO ID-derived、DO timestamp |
| `apps/sales/repository.py` | SO/DO inserts |
| `apps/sales/utils.py` | 未接主 Convert 的 SO timestamp helper |
| `apps/inventory/services.py` | SO-ID-derived DO path |
| `apps/inventory/v14_residual.py` | parallel DO path |
| `apps/sample/services.py` | SP timestamp |
| `apps/sample/v14_residual.py` | Sample parallel route |
| `runtime/v14/legacy_support.py` | Quote/SO/DO/Sample schemas/helpers |
| `document/nde_engine.py` | display document numbers |
| `business_modules/quotation.md` | module boundary |
| `business_modules/sales.md` | order authority |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Quote→SO owner |
| `docs/knowledge/legacy-extract/document-ops/numbering.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
