# 规则包：<法域名>

> 复制本模板新增一个法域包：建 `rules/<slug>/` 目录，放本 `_pack.md` + `_general.md` + 若干领域卡。路由层会列出 `rules/` 下每个子目录、读取其中的 `_pack.md` 自动发现，主流程零改动。

## 法域识别信号
<governing-law 条款命中模式，逐条列。如中国法："中华人民共和国法律""PRC law""Laws of the People's Republic of China"；美国法：具体州名 + "United States">

## 业务领域登记表
| 关键词 | 领域卡文件 |
|---|---|
| 买卖/采购/供货/购销 | sale-of-goods.md |
| 服务/SaaS/订阅/技术服务 | services-saas.md |
| 保密/NDA/商业秘密 | nda.md |
| <新增领域> | <file>.md |

## 推荐 MCP 源
<本法域推荐的法规/案例检索 MCP 源名；验证层据此探测。没接则回退模型知识+标注>

## 包元信息
<维护者 / 更新日期 / 覆盖范围说明 / 法域 slug>
