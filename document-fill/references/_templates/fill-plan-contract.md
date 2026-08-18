# 填充计划契约（Fill Plan Contract）

本文档定义"填充计划"的 JSON 结构，是 skill 正文（agent 生成填充计划）与确定性闸门
`fill_lint`（后续任务实现的校验脚本）之间的稳定接口。**agent 只按本契约产出 JSON，
不自行发明字段名或 status 取值。** 合法样例见 `../../scripts/sample_fill_plan.json`，
违反本契约的样例见 `../../scripts/sample_fill_plan.invalid.json`。

## 顶层结构

填充计划是一个 JSON **数组**，每个元素是一个"槽位"（slot）对象，对应模板中一处待填内容。

## 字段表

| 字段 | 类型 | 说明 |
|---|---|---|
| `slot_id` | str | 槽位唯一标识，数组内不可重复 |
| `slot_label` | str | 人读名称，用于报告/复核界面展示 |
| `slot_type` | str | 取值之一：`fact`（客观事实）、`legal_claim`（诉讼请求/法律主张的数额或表述）、`argument`（论证性文字，如"事实与理由"） |
| `template_context` | str | 该槽位在模板中的上下文片段，含 `{{slot_id}}` 占位符 |
| `status` | str | 取值之一：`extracted`、`inferred`、`user_confirmed`、`ambiguous`、`gap`、`pending_drafting` |
| `value` | str \| null | 最终填入模板的值；`gap`/`pending_drafting`/`ambiguous` 时为 `null` |
| `source_span` | object | `{source_id, quote, locator}`——指向来源文档的精确出处 |
| `inferred_from` | list | 参与推算的来源引用列表（如 `"_md/文件.md#p2"`） |
| `formula` | str | 推算公式/口径的文字说明 |
| `confirmed_at` | str | 用户确认时间戳（ISO 格式） |
| `confirmation_note` | str | 确认方式/背景说明 |
| `candidates` | list | 每项 `{value, source_span}`，列出并列冲突的候选值 |

## 各 status 的必填字段

- **`extracted`**（从原文直接摘取）
  必填：`source_span`。`source_span.quote` 必须是来源原文的逐字片段（见下方 Mode-2 说明），
  `value` 不得超出该 quote 所能直接支持的内容。

- **`inferred`**（由多个来源推算得出，非原文直接摘取）
  必填：`inferred_from`（非空 list）、`formula`。

- **`user_confirmed`**（卷内无据，经用户口头/书面确认）
  必填：`confirmed_at`、`confirmation_note`。

- **`ambiguous`**（多个来源给出互相冲突的值，尚未裁定）
  必填：`candidates`，且长度 **≥ 2**，每项自带独立的 `source_span`。`value` 必须为 `null`。

- **`gap`**（遍历全部来源后仍无法确定，需人工补充）
  无额外必填字段；`value` 必须为 `null`。

- **`pending_drafting`**（`argument` 类槽位，留待起草阶段生成论证文字，不属于"填空"）
  无额外必填字段；`value` 必须为 `null`。此状态只能用于 `slot_type: "argument"`。

## Mode-2 强约束：extracted 的 value 必须在 source_span.quote 逐字命中

`status = "extracted"` 代表"这是原文写的，不是模型推断/拔高的"。因此校验规则是：

> `value` 的核心内容必须能在对应 `source_span.quote` 的原文字符串中逐字找到，
> 不允许同义改写、数值换算或跨句拼接得出的结论冒充 `extracted`。

违反示例见 `sample_fill_plan.invalid.json`：

- `bad_extracted`：`quote` 只写"李四借款"，`value` 却写成"李四欠款50万元"——金额是
  拔高编造的，不在 quote 中逐字出现，应改用 `inferred`（并给出 `formula`）或降级为 `gap`。
- `bad_argument`：`slot_type` 是 `argument`（论证性文字），却用了 `status: "extracted"`——
  论证类槽位不应伪装成"原文摘录"，应使用 `pending_drafting`。
- `bad_ambiguous`：`status: "ambiguous"` 但 `candidates` 只有 1 项——不构成"并列冲突"，
  未达到 ambiguous 的最低门槛（≥2），应直接采用该唯一候选并改写为 `extracted`/`inferred`。

这类需要跨字段联合校验（而非单纯 JSON Schema 能表达）的规则，由后续任务的
`fill_lint.py` 脚本实现并强制执行；本文档只定义契约本身。
