# 合同审查 Skill — 跨 agent 可移植性调整设计

> 日期：2026-06-20
> 状态：设计已确认
> 关联：在 `contract-review/` 现有 skill 之上做可移植性硬化（非重构）

---

## 1. 目标与范围

让 `contract-review` skill 在**任意文件系统类 agent**（Claude Code / Codex / Cursor / Cline / Copilot CLI / Gemini CLI 等能读文件、能遍历目录的 agent）中都能无障碍运行，而不仅限 Claude Code。

### 已确认决策

| 决策项 | 结论 |
|---|---|
| Agent 覆盖范围 | 仅文件系统类 agent；不含纯聊天/无文件系统 agent |
| 架构 | 保留现有多文件 + 渐进式披露，不重构 |
| 触发方式 | 自含 + 手动唤起为基准；自动触发交给各 agent 原生机制（文档说明） |
| 改动范围 | 仅 `SKILL.md`、`references/01-jurisdiction-routing.md`、`references/08-redline.md`、`README.md` |

### 明确排除

- 不做单文件打包版（面向纯聊天 agent，不在本次范围）
- 不生成各 agent 自动触发配置文件（AGENTS.md / .cursorrules / 插件 manifest）
- 不改动方法论、规则包、验证层、输出格式等任何已有逻辑

---

## 2. 要解决的三个跨 agent 障碍

1. **文件自定位缺失**：SKILL.md 用裸相对路径，未声明相对于 skill 自身目录。非 Claude-Code agent 可能以当前工作目录解析 → 读不到 → 渐进披露链断裂，退化为通用回答。
2. **工具专属词**："glob" 等绑定特定运行时的动词，不通用。
3. **触发假设**：默认 Claude-Code frontmatter 自动发现；手动唤起路径未明示。

---

## 3. 调整内容（5 项）

### 3.1 SKILL.md 加"自定位规则"（核心）

在 SKILL.md 标题之后、"何时使用"之前加一段：

> **文件定位（先读）**：本 skill 由多个文件组成。下文所有 `references/…`、`rules/…` 路径均**相对于本 SKILL.md 所在目录**。开始前先确定该目录（你被指向或读取本文件时所在的位置），之后所有读取都基于它解析，不要用当前工作目录去找。

### 3.2 工具中立措辞

- "glob `rules/*/_pack.md`" → "列出 `rules/` 下每个子目录，读取其中的 `_pack.md`"。
- 消除其余任何工具专属动词，统一用"读取/列出/查看"。

### 3.3 手动唤起入口

保留 frontmatter；"何时使用"补一条：

> - 或当被明确要求用本 skill 审查合同、或被指向本 `SKILL.md` 时。

### 3.4 折叠两个运行障碍修复

- 路径基准（§3.1 已解决）。
- `08-redline.md` 第 6 步 "写入版本记录" → "在对话中报告修订稿路径、修订计划与 QA 检查结果（本 skill 不维护工作区/版本记录）"。
- 红线工具表述中立化："用 Documents 技能 / OOXML 工具" → "用本环境可用的 OOXML/docx 生成能力（如 Claude Code 的 Documents 技能，或其他 docx 工具）"，保留已有"无工具则优雅退化"段不变。

### 3.5 README 增"各 agent 快速上手 + 运行要求"

**(a) 各 agent 安装/唤起表**（文件系统类）：Claude Code / Codex / Cursor / Cline / Copilot CLI / Gemini CLI + 通用基准（任意可读目录，让 agent 读取并遵循 SKILL.md）。自动触发依赖各 agent 原生机制；本表只保证"手动指向 SKILL.md"在所有文件系统 agent 可用。

**(b) 运行要求**：纯审查路径零外部依赖；Word 红线稿需 OOXML/docx 能力（无则按 08 §二 退化）；MCP 可选（未接回退模型知识并标注）。

---

## 4. 验收标准

- SKILL.md 含自定位规则 + 手动唤起条目；路径在"以 SKILL.md 目录为基准"下全部可解析。
- 全 skill 无 "glob" 等工具专属动词。
- `08-redline.md` 无指向未定义工作区的写入指令；红线工具表述中立且保留退化路径。
- README 含各 agent 上手表 + 运行要求说明。
- `python validate.py` 全绿（SKILL.md ≤80 行、08 ≤260 行未被突破）。

---

## 5. 待实施清单

1. SKILL.md：自定位规则段 + 手动唤起条目 + 工具中立措辞。
2. references/01-jurisdiction-routing.md：glob → 通用动作。
3. references/08-redline.md：版本记录改报告 + 红线工具中立化。
4. README.md：各 agent 上手表 + 运行要求。
5. validate.py 确认全绿。
