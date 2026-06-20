# 合同审查 Skill（中美双法域）

Claude Code 技能：判定合同受中国法/美国法/跨境管辖，按法域加载可插拔规则包，逐条审查并产出双轴风险问题清单与可选 Word 红线稿。

## 安装
将 `contract-review-cn-us/` 放入 Claude Code 技能目录（如 `~/.claude/skills/`），或按你的插件机制注册。`SKILL.md` 为入口。

## 设计三层
- 法域中立方法骨架（references/02）
- 可插拔法域规则包（references/rules/<法域>/）
- 法域路由层（references/01）

## 扩展
- 加业务领域：在对应 `rules/<法域>/_pack.md` 登记表加一行 + 按 `references/_templates/domain-card-template.md` 新建一个卡。
- 加法域（如香港）：按 `references/_templates/pack-template.md` 新建 `rules/hk/` 目录，路由层自动发现。

## 校验
改完跑 `python validate.py` 检查行预算/必备标题/anti-leakage 软警告。

## MCP（可选）
验证层可插拔：接上各法域 `_pack.md` 声明的 MCP 源则实时核验法条，未接则回退模型知识并标 `[模型知识-未验证]`。

## 边界
只做合同审查 + 可选 Word 红线稿。不做起草、企业核验、续约提醒、流程图、版本对比、实务画像。
