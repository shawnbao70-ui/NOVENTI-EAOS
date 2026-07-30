# 测量、Sample360 分析块与图片

## Scope与证据强度

本页覆盖测量、样品需求描述、材料分析、质量评估、供应商匹配和图片。强证据表明这些数据由人工表单追加；未见仪器导入、自动计算、分析审批或版本选择。AI/enrichment 只附加页面参与者，不能证明自动产出分析。

存在重要渲染差异：Sample360 服务返回 measurement、requirement、material_analysis、quality_assessment 和 supplier_matching，但当前模板还循环 `images`、`materials`、`logs`；这些键在该服务显式上下文中未见赋值。

## 业务规则（稳定ID）

1. **SA-R01** 每次保存测量都插入新 `sample_measurements` 行，不覆盖旧记录。
2. **SA-R02** 样品详情和 Sample360 默认只读取该样品 id 最大/最新的一条测量。
3. **SA-R03** 测量字段包括长、宽、厚、重、节距、齿数、材质和硬度。
4. **SA-R04** `sample_requirements` 独立保存机器、应用、环境、寿命、目标价、OEM/包装/品牌/认证、市场和年需求。
5. **SA-R05** 样品需求块不是 `business_requirements` 主实体；两者仅可通过另行追溯字段关联。
6. **SA-R06** 材料分析每次追加一行，包含主材、表层、芯层、增强材、硬度、密度、温区、等级、风险和备注。
7. **SA-R07** 质量评估每次追加一行，保存五类分数、整体等级和备注；系统未自动计算整体等级。
8. **SA-R08** 供应商匹配允许同一样品保存多条候选记录，并在 Sample360 查询时连接供应商名称。
9. **SA-R09** 固定图片槽位 image1/image2/image3 直接保存在 samples 主记录，并以固定文件名覆盖同槽内容。
10. **SA-R10** 通用图片上传另写 `sample_images`，可保留多条，默认 image_type 为 Other。
11. **SA-R11** 图片上传先调用统一图片安全校验；通用上传还使用安全文件名。
12. **SA-R12** 通用图片删除检查 `Samples.delete`，删除磁盘文件及数据库行；固定槽位删除只置空字段，未见同等权限门且未删除磁盘文件。
13. **SA-R13** 详情页真实查询并展示通用图片；Sample360 当前服务/模板的 images/materials/logs 上下文存在不一致。
14. **SA-R14** 测量、分析、评估和供应商保存路由未见 Samples.edit 服务端权限检查。
15. **SA-R15** Sample360 附加 lifecycle/AI/automation/intelligence 等参与者，但异常被吞掉，Legacy 人工数据仍是可确认事实。
16. **SA-R16** 测量及四类分析 POST 路由存在，但当前 `templates/sample*` 未找到对应录入表单；“可写后端”不等于“可从现有 UI 操作”。
17. **SA-R17** Object360 Sample runtime 只在普通详情页尝试附加；`/sample360/{id}` 服务未调用该 runtime，因此 shadow bundle 不是 Sample360 模板的数据权威。

## 流程

### 测量与分析

1. 在样品详情提交测量，系统追加一条记录。
2. 打开详情或 Sample360 时只取最新测量。
3. Sample360 可分别提交需求、材料分析、质量评估和供应商匹配。
4. 各提交独立插入并提交，不形成统一分析版本或“分析完成”状态。
5. Sample360 再尝试附加生命周期和企业参与者；失败不阻断基础页面。

### 图片

- 固定槽：上传到 `uploads/samples/sample_{id}_{slot}.{ext}`，把文件名写入 samples 的 image1–3。
- 多图：时间戳+安全原名保存到同目录，并插入 `sample_images`。
- 删除：多图删除文件与行；固定槽只清数据库字段。

## 校验（强/弱/缺失）

1. **SA-V01（强/类型）** 测量数值由 FastAPI 转为 float/int。
2. **SA-V02（强）** 图片必须通过统一 upload image 校验。
3. **SA-V03（强）** 固定槽扩展名限制为 jpg/jpeg/png/webp/gif，否则回退 jpg。
4. **SA-V04（强）** 通用图片删除要求 Samples.delete。
5. **SA-V05（弱）** 固定槽只处理 1–3 分支，但路由未显式拒绝其他 slot。
6. **SA-V06（缺失）** 测量值未见非负、单位、合理范围或必填校验。
7. **SA-V07（缺失）** 质量分数未见 0–100 或统一量表校验。
8. **SA-V08（缺失）** overall_grade、quality_grade、risk_level 未见枚举约束。
9. **SA-V09（缺失）** 各分析保存未先确认 sample_id 存在。
10. **SA-V10（缺失）** 分析保存未见编辑权限、审核或锁定校验。
11. **SA-V11（缺失）** 未见图片数量、尺寸、分辨率、重复内容或说明必填规则。
12. **SA-V12（缺失）** 未见分析版本、有效记录标记或并发控制。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sample_measurements` | 样品测量历史表 |
| `length/width/thickness` | 未带单位的尺寸数值 |
| `weight` | 未带单位的重量数值 |
| `pitch/teeth` | 传动类样品的节距与齿数 |
| `material/hardness` | 测量记录上的材质与硬度文本 |
| `sample_requirements` | 样品层应用与商业需求描述 |
| `target_price/annual_demand` | 样品需求块中的商业参考数值 |
| `sample_material_analysis` | 人工材料层次与风险记录 |
| `sample_quality_assessment` | 五项评分和整体等级记录 |
| `sample_supplier_matching` | 样品候选供应商、价格、MOQ、交期和质量分 |
| `image1/image2/image3` | samples 主记录上的固定图片槽 |
| `sample_images` | 多图附件记录 |
| `image_type` | 通用上传固定写 Other |
| `create_date` | 通用图片上传时间 |
| latest by id | 页面选择最近分析/测量的实际策略 |

## 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Measurement | 一条人工测量记录 |
| Material Analysis | 人工材料分析记录 |
| Quality Assessment | 人工评分记录 |
| Supplier Matching | 人工候选供应商记录 |
| Other | 通用图片默认类型 |
| risk_level | 自由文本风险标签 |
| overall_grade | 自由文本整体等级 |
| Analyzed / Approved | UNKNOWN；未见分析状态机 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SA-E01 | 测量为 INSERT，页面只取最新一条 | 强 | `apps/sample/services.py` |
| SA-E02 | 四类 Sample360 附属数据分别插入 | 强 | `apps/sample/services.py`、`router.py` |
| SA-E03 | 分析表字段 DDL | 强 | `runtime/v14/legacy_support.py` |
| SA-E04 | 固定三槽图片写 samples 字段 | 强 | `apps/sample/services.py`、`templates/sample_detail.html` |
| SA-E05 | 通用图片写文件和 sample_images | 强 | `apps/sample/services.py` |
| SA-E06 | 通用删除有权限且删除文件/行 | 强 | `apps/sample/services.py` |
| SA-E07 | Sample360 服务显式 ctx 与模板变量不一致 | 强（缺口） | `apps/sample/services.py`、`templates/sample360.html` |
| SA-E08 | core/sample metadata 只把 measurements/images 列为领域表 | 中 | `core/sample/metadata.py` |
| SA-E09 | A-017 强调页面诚实与无自动入库 | 强 | `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` |
| SA-E10 | Sample 模板未发现测量/分析 POST 表单 | 强（缺失证据） | `templates/samples.html`、`sample_detail.html`、`sample360.html` |
| SA-E11 | 历史稳定性报告记录 Sample360 运行异常 | 中 | `docs/reports/V15_RUNTIME_STABILITY_REPORT.md` |

## UNKNOWN + 已查路径

1. **尺寸、重量、硬度的正式单位 UNKNOWN。** 已查路径：DDL、Sample forms、locales、Sample报告。
2. **测量仪器导入或自动采集 UNKNOWN。** 已查路径：`apps/sample/`、API routes、templates、business_modules。
3. **哪一条分析记录是批准/生效版本 UNKNOWN。** 已查路径：analysis表、services查询、Sample360。
4. **整体等级和风险等级的枚举/计算公式 UNKNOWN。** 已查路径：save handlers、templates、reports。
5. **分析编辑、复核和职责分离 UNKNOWN。** 已查路径：Sample router、permission、approval module。
6. **固定槽文件替换/删除后的孤儿文件清理 UNKNOWN。** 已查路径：upload/delete slot service、uploads逻辑。
7. **Sample360 中 images/materials/logs 最终由哪个 runtime 注入 UNKNOWN。** 已查路径：Sample service、core/sample、Object360 hook、template。
8. **图片是否带主图、角度、标注和拍摄日期语义 UNKNOWN。** 已查路径：sample_images DDL、上传表单与服务。
9. **AI participant 是否在其他部署生成持久分析 UNKNOWN。** 已查路径：Sample service hooks、enterprise participant接口、报告。
10. **Sample360 历史 HTTP 500 的当前根因与是否已修复 UNKNOWN。** 已查路径：稳定性报告、Sample service、模板变量与 runtime hooks。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\core\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
