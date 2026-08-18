---
name: document-fill
description: 给一份文书模板 + 本案知识库，按模板取证填充、产出干净文书 + 溯源/缺口报告。当用户要求「按案卷/知识库填一份模板/表单/文书」时使用。
---

# 文书模板填充（按本案知识库取证填空）

## 文件定位（先读）
本 skill 由多个文件组成。下文所有 `references/…`、`scripts/…` 路径均**相对于本 SKILL.md 所在目录**。开始前先确定该目录（你被指向或读取本文件时所在的位置），之后所有读取都基于它解析，不要用当前工作目录去找。

## 何时使用
- 用户给了一份文书模板/表单（起诉状、答辩状、合同模板等占位符文本）+ 本案知识库（案卷材料、证据、笔录等），要求按模板把待填项填好。
- 用户明确要求「按案卷填一份模板」「把这份表单填了」「用知识库填这份文书」。
- 上游技能路由到文书填充。

## 任务边界
本技能只做**模板 × 本案知识库 的取证填充**，产出干净文书 + 溯源/缺口报告。不做以下事项：
- 说理论证、法律主张的论证性文字撰写 → 路由 `legal-research`（论证）或起草类技能（成文）
- 法律问题研究、类案检索 → 路由 `legal-research`
- 合同审查、条款风险评估、红线稿 → 路由 `contract-review`

## 硬不变量（常驻，不可跳过）
无论任务大小、读没读全深层文件，以下底线始终生效：
- **闭世界**：只使用本案材料（知识库内文件）取证；本案材料之外的任何来源（模型记忆、常识、网络）一律不得作为填入值的依据。
- **宁可查不到，也不编造**：材料中确实找不到的待填项，写「未在本案材料中找到」，绝不脑补、绝不用推测值冒充事实。
- **缺口显性标注**：找不到、待人工补充的待填项必须在填充计划与最终文书中显性标出（`status: gap`），不得静默留白或悄悄跳过。
- **每个填入值挂且仅挂一个状态标签**：`extracted` / `inferred` / `user_confirmed` / `ambiguous` / `gap` / `pending_drafting` 六选一，不得混用或省略；各状态必填字段见 `references/_templates/fill-plan-contract.md`。
- **Mode-2 强约束**：`status: extracted` 的 `value` 必须能在其 `source_span.quote` 的原文字符串中逐字命中，不允许同义改写、数值换算或跨句拼接冒充摘录；此规则由 `scripts/fill_lint.py` 机检强制执行。
- **论证型待填项一律留空**：`slot_type: argument`（如"事实与理由"这类说理性文字）不属于本 skill 的填空范围，一律 `status: pending_drafting`，交起草/论证环节处理，不由本 skill 代写。

## 执行顺序（按需读取，不要一次读全）
1. 读 `references/00-workflow.md`，了解主流程与阶段划分。
2. 探测/接入本案知识库时读 `references/10-kb-access.md`。
3. 识别模板待填项、逐项取证填充时读 `references/20-slot-and-fill.md`。
4. 出稿（渲染文书）与出溯源/缺口报告时读 `references/30-output-and-report.md`。

## 按需读取索引
- `references/00-workflow.md` — 主流程与阶段划分
- `references/10-kb-access.md` — 本案知识库探测与接入
- `references/20-slot-and-fill.md` — 待填项识别 + 取证填充规则
- `references/30-output-and-report.md` — 出稿方式 + 溯源/缺口报告格式
- `references/_templates/fill-plan-contract.md` — 填充计划 JSON 契约（字段表 + 各 status 必填字段 + Mode-2 说明）
- `scripts/fill_lint.py` — 填充计划确定性闸门：机检来源锚定完整性与状态合法性，输出覆盖率账本
- `scripts/fill_docx.py` — 把填充计划渲染进模板；docx 优先，缺 python-docx 或模板非 docx 时降级为 markdown 并显式返回 `degraded=True`

读取失败必须明说，不静默跳过。
