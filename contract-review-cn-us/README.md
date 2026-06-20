# 合同审查 Skill（中美双法域）

面向**文件系统类 AI agent**（能读文件、能遍历目录：Claude Code / Codex / Cursor / Cline / Copilot CLI / Gemini CLI 等）的技能：判定合同受中国法/美国法/跨境管辖，按法域加载可插拔规则包，逐条审查并产出双轴风险问题清单与可选 Word 红线稿。

## 安装与唤起

把 `contract-review-cn-us/` 整个文件夹放到 agent 能读到的位置，让 agent 读取并遵循 `SKILL.md`（入口）。skill 会自定位：所有内部路径都相对于 `SKILL.md` 所在目录解析，与当前工作目录无关。

| Agent | 放置位置 | 唤起方式 |
|---|---|---|
| Claude Code | `~/.claude/skills/contract-review-cn-us/` 或按插件机制注册 | frontmatter 自动触发；或显式"用合同审查 skill" |
| Codex | 项目内可读路径 | 指向 SKILL.md / 按其 skill 约定 |
| Cursor / Cline | 项目内可读路径 | @ 引用或指向 SKILL.md |
| Copilot CLI | 项目内可读路径 | 指向 SKILL.md |
| Gemini CLI | 项目内可读路径 | activate / 指向 SKILL.md |
| 通用基准 | 任意 agent 可读目录 | 让 agent 读取并遵循 `SKILL.md` |

自动触发依赖各 agent 原生机制；上表只保证"手动指向 `SKILL.md`"在所有文件系统 agent 都能跑起来。

## 运行要求
- 纯合同审查路径：**零外部依赖**。
- Word 红线稿：需环境具备 OOXML/docx 生成能力；无则按 `references/08-redline.md` §二 退化为问题清单交付。
- MCP 法规核验：**可选**；接上则实时核验，未接回退模型知识并标 `[模型知识-未验证]`。

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
