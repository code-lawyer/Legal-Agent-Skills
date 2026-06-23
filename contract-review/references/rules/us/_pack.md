# 规则包：美国法

## 法域识别信号
- "governed by the laws of the State of <州名>"、"State of New York/Delaware/California" 等具体州 + "United States"
- "this Agreement shall be governed by ... laws of <US state>"
- 注意：美国合同法以州法为主，须捕获**具体州名**；仅写"US law"而无州名时标注[需确认具体州]

## 业务领域登记表
| 关键词 | 领域卡文件 |
|---|---|
| sale/purchase/supply/goods/购销 | sale-of-goods.md |
| services/SaaS/subscription/cloud | services-saas.md |
| NDA/confidentiality/CDA | nda.md |

## 推荐 MCP 源
- 商用库：Westlaw / LexisNexis / Bloomberg Law 类（判例、州法典、UCC 各州采纳）。
- 免费/自建：Cornell LII、CourtListener、各州立法网站（state legislature）——可自建为 MCP 源。
- 选源须按 governing law 所在**具体州**校验，州法差异显著。验证层据此探测；未接则回退模型知识 + `[模型知识-未验证]`。

## 输出提示
- 工作成果页眉：可用「Confidential — Attorney Work Product」（美国法 work-product / privilege 概念存在）；具体保护范围按事项与州法确认。

## 包元信息
- 法域 slug：us
- 维护者：<填写>　更新日期：2026-06-19
- 覆盖范围：美国州法商事合同。州法差异显著，须按具体州校验。
