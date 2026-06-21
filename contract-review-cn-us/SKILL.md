---
name: contract-review-cn-us
description: 中美双法域合同审查。判定合同受中国法/美国法/跨境管辖，按法域加载规则包，逐条审查并产出双轴风险问题清单与可选 Word 红线稿。当用户要求审查/审阅/markup 合同、检查条款、看 NDA/MSA/SaaS/买卖等协议时使用。
---

# 合同审查（中美双法域）

## 文件定位（先读）
本 skill 由多个文件组成。下文所有 `references/…`、`rules/…` 路径均**相对于本 SKILL.md 所在目录**。开始前先确定该目录（你被指向或读取本文件时所在的位置），之后所有读取都基于它解析，不要用当前工作目录去找。

## 何时使用
- 用户要求审查、审阅、markup、检查一份合同或其中条款。
- 用户问某条款在中国法或美国法下是否有效/有风险/如何修改。
- 上游技能路由到合同审查。
- 或当被明确要求用本 skill 审查合同、或被指向本 `SKILL.md` 时。

## 任务边界
本技能只做**合同审查 + 可选 Word 红线稿**。不做合同起草、企业核验、续约提醒、版本对比、流程图、实务画像。

## 执行顺序（按阶段按需读取，不要一次读全）
1. 读 `references/00-workflow.md`，按四阶段推进。
2. 阶段2 判定法域时，列出 `references/rules/` 下每个子目录、各读其中的 `_pack.md` 清单（极小），不读规则正文。
3. 阶段3 深审时，读 `references/02-methodology.md` + 判定法域包的 `_general.md` + 命中业务领域那一个卡；跨境才读第二法域包。
4. 出问题清单读 `references/06-output-and-severity.md`；涉精确法条调 `references/07-verification.md`；要红线稿才读 `references/08-redline.md`。

## 按需读取索引
- `references/00-workflow.md` — 四阶段主流程
- `references/01-jurisdiction-routing.md` — 法域判定与跨境
- `references/02-methodology.md` — 法域中立审查骨架 + 失败模式 + 大输入纪律
- `references/rules/<法域>/` — 可插拔规则包（_pack.md 清单 / _general.md 通用 / 领域卡）
- `references/06-output-and-severity.md` — 双轴评级 + 问题卡 + 来源标签 + 备忘录
- `references/07-verification.md` — MCP 验证接口 + 三轮检索 + 注入防御
- `references/08-redline.md` — Word 红线七步 QA

## 输出底线
- 不跳过用户材料；读取失败必须说明。
- 不用模型记忆替代法律核验；引用法规/案例必须带来源标签之一（见 06）并注明核验状态。
- 材料不足提示缺口，不静默脑补。
- 检查表是底线不是上限：超出审查卡的法律问题照常作答并说明；学理问题直接答，不硬塞进文件审查流程。
- 正式审查交付附免责声明（不构成最终法律意见、需主办律师复核）；格式见 `references/06-output-and-severity.md`。
