# 文书填充主流程（五阶段）

> 渐进式披露：本文件只给流程骨架与跳转，不含知识库接入细节/标签规则/输出格式正文。各阶段按需读对应
> reference，不一次读全。

## 阶段①：读模板 → 识别待填项

- 通读用户提供的文书模板全文；读取失败必须明说，不静默跳过。
- 扫出全部待填位置，两条识别路并用：
  1. **显式占位符**：`{{slot_id}}`、下划线空格 `____`、方括号提示 `【…】` 等模板作者留下的显性标记。
  2. **语义推断**：模板没有占位符但结构上明显要填（如空白表格单元格、"XXX"、留白日期栏）——次要
     路径，显式占位符优先，语义推断仅用于补漏。
- 为每处待填内容建一条**待填项清单**草稿（先只记 `slot_id`/`slot_label`/`template_context`，`slot_type`
  与取值留到阶段③）。清单是后续阶段的骨架，不是最终产物。

## 阶段②：探测本案知识库

- 转 `references/10-kb-access.md`：判定案件目录是 AnyDocsMarked 知识库还是普通案卷文件夹，决定用
  哪种取证方式、要不要显性告知降级。
- 本阶段只做探测和路由决策，不取证、不填值。

## 阶段③：逐项取证填值、挂状态标签

- 转 `references/20-slot-and-fill.md`：对阶段①清单里 `slot_type: fact` / `legal_claim` 的每一项，按
  阶段②的取证方式检索本案材料，把取到的值和且仅一个状态标签（`extracted`/`inferred`/
  `user_confirmed`/`ambiguous`/`gap`）写回清单。
- 闭世界铁律贯穿全程：只用本案材料取证，材料之外的模型记忆/常识/网络一律不得作为填入值依据；
  查不到就是 `gap`，不得编造、不得脑补凑数。

## 阶段④：论证型留空、标待起草、路由出去

- 阶段①清单中 `slot_type: argument` 的项（如"事实与理由""答辩意见"这类说理性文字）一律
  `status: pending_drafting`，`value` 为 `null`——不属于本 skill 的填空范围，不由本 skill 代写。
- 这类项在报告里要显性列出"待起草清单"，并告知用户可路由到论证/起草环节续接（如需要法律论证，
  路由 `legal-research`；需要合同起草另行处理）。本 skill 不导入、不调用那些 skill 的文件，只是
  口头指路。

## 阶段⑤：机检闸门 → 出稿 + 报告

- 把阶段③④产出的完整清单整理成符合 `references/_templates/fill-plan-contract.md` 契约的填充计划
  JSON（数组，每个待填项一个对象）。
- 先跑确定性闸门，**必须 0 违规才能继续**：

  ```bash
  python scripts/fill_lint.py <plan.json>
  ```

  该脚本机检来源锚定完整性（`extracted` 是否有完整 `source_span` 且 `value` 在 `quote` 中逐字命中，
  即 Mode-2 约束）与各 `status` 必填字段是否齐全，并打印覆盖率账本（各状态计数）。
- **若 lint 报硬错误：必须回到阶段②/③重新取证或改正标签，不得跳过闸门直接出稿**，也不得为了让
  lint 通过而弱化 `value`、编造 `source_span`，或把不该是 `extracted` 的项硬标成 `extracted`。
  常见回退动作：`value` 未在 `quote` 中逐字命中 → 回阶段③换更精确的 `quote` 或降级为 `inferred`/
  `gap`；某状态缺必填字段 → 回阶段③补全或改判正确的状态。
- lint 通过（`✅ 通过：所有取证项锚定完整、Mode-2 逐字命中`，退出码 0）后才能渲染出稿：

  ```bash
  python scripts/fill_docx.py <模板> <plan.json> <输出.docx>
  ```

  docx 优先渲染；缺 `python-docx` 或模板非 `.docx` 时脚本自动降级为 markdown 并返回
  `degraded=True`，须原样告知用户，不得隐瞒降级发生过。
- 出稿之后转 `references/30-output-and-report.md`：产出溯源/缺口报告，交付给用户。

## 简单任务捷径

- 模板很短、待填项极少（个位数）且知识库探测已确定可用时，阶段①~③可以在一次通读中合并完成，
  但阶段⑤的机检闸门**不可省略**——再小的填充计划也必须过 `fill_lint.py` 才能出稿。
