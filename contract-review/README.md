# 合同审查 Skill（中美双法域）

面向**文件系统类 AI agent**（能读文件、能遍历目录：Claude Code / Codex / Cursor / Cline / Copilot CLI / Gemini CLI 等）的技能：判定合同受中国法/美国法/跨境管辖，按法域加载可插拔规则包，逐条审查并产出双轴风险问题清单与可选 Word 红线稿。

> ⚠️ **交付单元是整个 `contract-review/` 文件夹，不是单个 `SKILL.md`。** SKILL.md 只是入口索引，正文（流程/方法/规则）在 `references/` 与 `rules/` 里，运行时由 agent 按需读取。只把 SKILL.md 一个文件交出去会导致 agent 读不到这些文件。

## 一、获取

**方式 A（推荐，给使用者）—— 从 Releases 下载压缩包**
到本仓库 [Releases](../../releases) 下载 `contract-review-<版本>.zip`，解压即得到完整的 `contract-review/` 文件夹。

**方式 B（给想改/想扩展的人）—— 克隆源码**
```
git clone https://github.com/Tsinglaw/Legal-Agent-Skills.git
```
skill 位于 `contract-review/`。

## 二、使用

解压/克隆后，把 `contract-review/` 文件夹交给 agent，三选一：

1. **放进 agent 的 skill 目录**（有 skill 机制的 agent，可自动触发）。
2. **指向 SKILL.md**（任意文件系统 agent，手动唤起）：让 agent 读取并遵循 `contract-review/SKILL.md`。
3. **直接把 zip 丢给有 shell 的 agent**：让它先解压，再读 `contract-review/SKILL.md`。

skill 会自定位：所有内部路径都相对于 `SKILL.md` 所在目录解析，与当前工作目录无关。

| Agent | 放置位置 | 唤起方式 |
|---|---|---|
| Claude Code | `~/.claude/skills/contract-review/` 或按插件机制注册 | frontmatter 自动触发；或显式"用合同审查 skill" |
| Codex | 项目内可读路径 | 指向 SKILL.md / 按其 skill 约定 |
| Cursor / Cline | 项目内可读路径 | @ 引用或指向 SKILL.md |
| Copilot CLI | 项目内可读路径 | 指向 SKILL.md |
| Gemini CLI | 项目内可读路径 | activate / 指向 SKILL.md |
| 通用基准 | 任意 agent 可读目录 | 让 agent 读取并遵循 `SKILL.md` |

自动触发依赖各 agent 原生机制；上表只保证"手动指向 `SKILL.md`"在所有文件系统 agent 都能跑起来。纯聊天、无文件系统能力的 agent 不在支持范围内（拿到 zip 也无法当 skill 用）。

## 三、运行要求
- 纯合同审查路径：**零外部依赖**。
- Word 红线稿：需环境具备 OOXML/docx 生成能力；无则按 `references/08-redline.md` §二 退化为问题清单交付。
- MCP 法规核验：**可选**；接上则实时核验，未接回退模型知识并标 `[模型知识-未验证]`。

## 四、设计三层
- 法域中立方法骨架（`references/02-methodology.md`）
- 可插拔法域规则包（`references/rules/<法域>/`）
- 法域路由层（`references/01-jurisdiction-routing.md`）

## 五、扩展
- 加业务领域：在对应 `rules/<法域>/_pack.md` 登记表加一行 + 按 `references/_templates/domain-card-template.md` 新建一个卡。
- 加法域（如香港）：按 `references/_templates/pack-template.md` 新建 `rules/hk/` 目录，路由层自动发现。
- 改完跑 `python validate.py`：检查行预算、必备标题、登记表↔卡文件一致性、anti-leakage 软警告。

## 六、发布（维护者）
打 tag 即由 GitHub Actions 自动校验 + 打包 + 发 Release：
```
git tag v1.0.0
git push origin v1.0.0
```
workflow 见 `.github/workflows/release-skill.yml`，校验不过不发布。

## 七、MCP（可选）
验证层可插拔：接上各法域 `_pack.md` 声明的 MCP 源则实时核验法条，未接则回退模型知识并标 `[模型知识-未验证]`。

## 八、边界
只做合同审查 + 可选 Word 红线稿。不做起草、企业核验、续约提醒、流程图、版本对比、实务画像。每份正式审查交付都附免责声明（不构成最终法律意见，需主办律师复核）。
