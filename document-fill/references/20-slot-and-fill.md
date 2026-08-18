# 待填项识别 + 取证填充纪律 + 五态标签

## 待填项识别：两条路，给每项定 slot_type

- **显式占位符**（优先路径）：模板作者留下的显性标记，常见形态 `{{slot_id}}`、连续下划线
  `____`、方括号提示 `【原告姓名】`。这类标记本身就给出了 `slot_id`/`slot_label` 的线索，直接抽取。
- **语义推断**（次要路径，补漏用）：模板没有显式标记，但结构上明显要填的位置——空白表格单元格、
  占位字符 "XXX"、留白日期栏等。仅在通读全文确认显式占位符已扫完之后，用它补充遗漏项，不作为
  主路径独立使用（避免把叙述性正文误判成待填项）。
- 每个待填项确定后，赋一个 `slot_type`（三选一，决定后续填充方式与允许的 `status` 集合）：
  - `fact`：客观事实（姓名、日期、金额、地址等）。
  - `legal_claim`：诉讼请求/法律主张的数额或表述（如"请求判令支付违约金 X 元"）。
  - `argument`：论证性文字（如"事实与理由""答辩意见"整段说理）——这类项**不填空**，见下方
    「论证型一律 pending_drafting」。

## 状态标签表（与 `references/_templates/fill-plan-contract.md` 完全一致）

每个待填项填入值后，**挂且仅挂一个状态标签**，不得混用、不得省略：

| 状态 | 含义 | 必填字段 | 适用 slot_type |
|---|---|---|---|
| `extracted` | 从案卷原文直接摘取 | `source_span{source_id,quote,locator}`；`value` 必须在 `quote` 中逐字命中（Mode-2） | fact / legal_claim |
| `inferred` | 由多个来源推算得出，非原文直接摘取 | `formula`（推算口径说明）+ `inferred_from`（非空来源引用列表） | fact / legal_claim |
| `user_confirmed` | 卷内无据，经用户口头/书面确认 | `confirmed_at`（ISO 时间戳）+ `confirmation_note` | fact / legal_claim |
| `ambiguous` | 多个来源给出互相冲突的值，尚未裁定 | `candidates`（≥2 项，每项自带独立 `source_span`）；`value` 必须为 `null` | fact / legal_claim |
| `gap` | 穷尽检索仍无法确定 | 无额外必填；`value` 必须为 `null` | fact / legal_claim |
| `pending_drafting` | 论证性文字，留待起草阶段生成 | 无额外必填；`value` 必须为 `null`；只能用于 argument | argument |

字段释义与 Mode-2 强约束（`extracted.value` 必须能在对应 `quote` 里逐字找到，不允许同义改写/数值
换算/跨句拼接冒充摘录）详见 `references/_templates/fill-plan-contract.md`；本文件只给挑选哪个状态
的判断规则，不重复契约字段表。

## 挑状态的判断顺序

对每个 `fact`/`legal_claim` 待填项，按下列顺序判断，选到第一个成立的状态即停：

1. 检索到**唯一**且能逐字支持的原文片段 → `extracted`。
2. 没有能直接逐字支持的原文，但能靠**多个**来源合理推算出值（如金额加总、期限换算）→
   `inferred`，写清 `formula` 和 `inferred_from`。
3. 检索不到，也推算不出，但用户当场给出了确认值 → `user_confirmed`，记录 `confirmed_at` 和
   `confirmation_note`。
4. 检索到**两个及以上互相冲突**的候选值，且不能靠现有材料裁定哪个对 → `ambiguous`，把候选并列
   交给人裁决，**绝不擅自取舍其中一个当作定论**，也不得各打五十大板私自取平均值。
5. 穷尽以上手段仍无结果 → `gap`，留空、不编造。

`argument` 型待填项不进入以上判断流程，直接 `pending_drafting`——这是 SKILL.md 硬不变量之一，见
`references/00-workflow.md` 阶段④。

## 法律主张型（legal_claim）的额外纪律

- `legal_claim` 的值本身仍要遵守上面五态判断：要么能锚到案件事实（`extracted`/`inferred`），要么
  是用户确认/存疑/缺口，不因为它带"法律"字样就允许凭模型知识直接给数。
- 如果该主张涉及**法律定性**是否成立（例如某笔款项能否定性为"违约金"而非"赔偿金"），这是法律判断
  而非事实取证，本 skill 不越权替用户下结论；可选接入法律库 MCP 做核验（若已配置且探测可用），
  核验结果作为参考信息附注在报告里，不改变待填项本身的取值流程。未接入 MCP 时不强求，按上面五态
  规则正常处理即可，不因缺 MCP 而卡流程。

## 产物

阶段③④结束后的产物是一份**符合 `references/_templates/fill-plan-contract.md` 契约**的填充计划
JSON 数组：每个待填项一个对象，字段名与 `status` 取值严格按契约来，不自行发明新字段名或新状态值。
这份 JSON 是喂给 `scripts/fill_lint.py` 机检、再喂给 `scripts/fill_docx.py` 渲染的唯一输入。
