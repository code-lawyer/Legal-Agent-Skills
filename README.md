# Legal Agent Skills

面向**文件系统类 AI agent**（能读文件、能遍历目录：Claude Code / Codex / Cursor / Cline / Copilot CLI / Gemini CLI 等）的一组**中文法律执业级 Agent Skills**。

每个 skill 是一个自包含文件夹：入口 `SKILL.md` 只放常驻底线与按需读取索引，正文（流程 / 方法 / 规则 / 报告模板 / 终检门）在 `references/` 与 `rules/` 里，运行时由 agent 按需分阶段读取——**渐进式披露**，既省 token 又保证深层规则不被跳过。

> ⚠️ **交付单元是整个 skill 文件夹，不是单个 `SKILL.md`。** 只把 `SKILL.md` 一个文件交出去，agent 会读不到 `references/`、`rules/` 里的正文。

---

## 一、项目用途

把"资深执业律师会怎么做"沉淀成 agent 可直接执行的结构化流程，覆盖两类高频法律工作：

| Skill | 交付物 | 何时触发 |
|---|---|---|
| **[`contract-review/`](contract-review/)** | 双轴风险问题清单 + 可选 Word 红线稿 | 审查/审阅/markup 合同、检查条款、看 NDA/MSA/SaaS/买卖等协议 |
| **[`legal-research/`](legal-research/)** | 法律研究报告 / 类案检索报告 | 论证某法律问题、查争议点法律依据、检索类案、归纳裁判规则/裁判倾向 |

两个 skill 边界互斥、彼此路由：合同相关 → `contract-review`；法律问题论证或类案检索 → `legal-research`。均**不做**合同起草、企业核验、尽调合规、续约提醒、流程图。

---

## 二、核心特色

**1. 防幻觉是第一设计目标。**
法条/案例不能靠模型记忆——那是最危险的幻觉源。两个 skill 都要求每条法律命题**挂且仅挂一个来源标签**（`[MCP核验:…]` / `[模型知识-未验证]` 等），标签描述"实际来源行为"而非"自信程度"；三轴正交（验证渠道 / 权威位阶 / 处置状态），互不冒充。

**2. 可插拔、可核验的法律库接入。**
不写死任何具体 MCP 名称，运行时**实际发探测调用**（不只看配置）。
- `contract-review`：MCP 法规核验为**可选加速器**——核心审查方法论无外部依赖也能跑，接上则实时核验。
- `legal-research`：MCP 是**硬前置**——没有可靠法律库就没有真研究/检索；未接则先引导用户接入、暂停正式产出，唯一例外是用户显式 opt-in 的通篇水印降级草稿。

**3. 法域中立 + 可插拔规则包（contract-review）。**
方法骨架（`02-methodology.md`）法域无关；中国法/美国法规则各自成包（`rules/cn/`、`rules/us/`），路由层按合同的法律选择条款判定并加载——**判定法域只看法律选择条款，绝不看合同语言**。加一个新法域（如香港）零改动路由层。

**4. 单一终检门 + 精确回退（legal-research）。**
报告产出前必过 QC 七项终检门，不通过按精确回退目标退回对应步骤补正；回退次数设上限防死循环——诚实标注不确定性优于卡死不交付。

**5. 真实 Word 修订痕迹，不许伪造。**
`contract-review/scripts/redline_docx.py`（纯 Python + `python-docx`）把修订计划渲染成真实 `w:ins`/`w:del` 修订痕迹 + 批注；未装 `python-docx` 时自动降级为 markdown 对照稿并明确告知，不静默失败。

**6. `validate.py` 把结构漂移堵在提交前。**
仅用标准库，检查行预算、必备文件/标题、无悬空引用、登记表↔卡文件双向一致性、SKILL.md 硬不变量锚点、anti-leakage 软警告。改完就跑，绿了再提交。

---

## 三、使用方法

解压/克隆后，把**整个 skill 文件夹**交给 agent，三选一：

1. **放进 agent 的 skill 目录**（有 skill 机制的 agent，可自动触发）。
2. **指向 `SKILL.md`**（任意文件系统 agent，手动唤起）：让 agent 读取并遵循 `contract-review/SKILL.md` 或 `legal-research/SKILL.md`。
3. **直接把 zip 丢给有 shell 的 agent**：让它先解压，再读对应 `SKILL.md`。

skill 会自定位：所有内部路径都相对 `SKILL.md` 所在目录解析，与当前工作目录无关。纯聊天、无文件系统能力的 agent 不在支持范围内。

| Agent | 放置位置 | 唤起方式 |
|---|---|---|
| Claude Code | `~/.claude/skills/<skill>/` 或按插件机制注册 | frontmatter 自动触发；或显式"用合同审查/法律研究 skill" |
| Codex / Cursor / Cline / Copilot CLI / Gemini CLI | 项目内可读路径 | 指向 `SKILL.md` / 按各自 skill 约定 |
| 通用基准 | 任意 agent 可读目录 | 让 agent 读取并遵循 `SKILL.md` |

### 接入法律库 MCP（推荐）

推荐源为**元典**（chineselaw.com），到 <https://open.chineselaw.com> 申请**你自己的 API Token**，按 `legal-research/references/09-mcp-setup.md` 把 `yuandian-law` / `yuandian-case` 两个 HTTP MCP 加进宿主 agent 的 `mcpServers` 配置、重连即可。

> **Token 即密钥**：只填进你本机/你账户的 agent 配置，**绝不写入 skill 文件、不提交仓库、不随报告输出**。本仓库不内置任何真实 Token，只给占位符。

---

## 四、开发与校验

要求 **Python 3.8+**。校验脚本仅用标准库；红线脚本的测试需要 `python-docx`。

```bash
# 校验 skill 结构完整性（每次修改 references/ 或 rules/ 后运行）
python contract-review/validate.py         # 预期：✅ 通过
cd legal-research && python validate.py     # 预期：✅ 通过

# 单元测试
python -m pytest contract-review/scripts/test_redline_docx.py   # 需 python-docx
python -m pytest legal-research/tests/                          # 纯标准库
```

### 扩展 contract-review

- **加业务领域**：在对应 `rules/<法域>/_pack.md` 登记表加一行 + 按 `references/_templates/domain-card-template.md` 新建一个领域卡。
- **加法域**（如香港）：按 `references/_templates/pack-template.md` 新建 `rules/hk/` 目录，路由层自动发现。
- 改完跑 `python contract-review/validate.py` 确认一致性。

---

## 五、获取与发布

**下载（使用者）**：到本仓库 [Releases](../../releases) 下载 `<skill>-<版本>.zip`，解压得到完整的 skill 文件夹。

**克隆（维护者）**：

```bash
git clone https://github.com/Tsinglaw/Legal-Agent-Skills.git
```

打 tag 即由 GitHub Actions（`.github/workflows/release-skill.yml`）自动校验 + 打包 + 发 Release，校验不过不发布。

---

## 六、免责声明

本仓库的 skill 产出为基于所提供材料及检索结果的**初步专业分析，不构成最终法律意见**，不替代主办律师对具体个案的判断与签字责任。所引法条及司法解释以检索时现行版本为准；标注 `[模型知识-未验证]` 的命题不得作为诉讼或法律交付物的唯一依据。据此行动前请经执业律师复核确认。

---

## 七、仓库结构

```
Legal-Agent-Skills/
├── contract-review/          # 中美双法域合同审查 skill
│   ├── SKILL.md              #   入口：常驻底线 + 按需读取索引
│   ├── references/           #   流程/方法/输出/验证/红线 + 规则包 rules/<法域>/ + 条款库
│   ├── scripts/              #   redline_docx.py（真实 Word 修订痕迹）
│   └── validate.py
├── legal-research/           # 法律研究与类案检索 skill
│   ├── SKILL.md
│   ├── references/           #   路由/检索核验/骨架/护栏/报告模板/终检门/MCP 接入
│   └── validate.py
├── docs/superpowers/         # 设计规格与实现计划（specs / plans）
└── .github/workflows/        # 打 tag 自动校验 + 打包 + 发 Release
```
