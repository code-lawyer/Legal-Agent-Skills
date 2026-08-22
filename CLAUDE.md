# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 本仓库是什么

面向**文件系统类 AI agent**的一组**中文法律执业级 Agent Skills**。内容规则为主、工具代码为辅。
**交付单元是整个 skill 文件夹，不是单个 `SKILL.md`**——只交 `SKILL.md` 一个文件，agent 会读不到
`references/`、`rules/` 里的正文。当前有三个 skill：`contract-review/`（中美双法域合同审查）、
`legal-research/`（法律研究与类案检索）、`document-fill/`（按本案知识库给文书模板取证填充）。

## 先读：作者宪章（PRINCIPLES.md）

顶层 `PRINCIPLES.md` 是**做 skill 时的最高原则（作者宪章）**，约束的是作者/你，**不是终端 agent**；
它**不写进任何 SKILL.md 正文，skill 运行时不读它**。**动手改任何 skill 或造新 skill 前先通读它**，
并按四层原则（元层 M / 工程 E / 法律 L / 产品 P）自检。几条最常踩的：

- **E1 自包含**：每个 skill **零依赖本库其他 skill**，可单独下载使用；**不建共享底座**，需要相同内容就
  各自复制一份。skill 内所有引用路径相对该 `SKILL.md` 目录解析，禁止越出本 skill 目录。
- **E3 只补模型做不到/会跳过的**：**不要把 LLM 本就会的法学方法论**（三段论、目的解释、IRAC、类推……）
  写进 skill 去"提示"它——纯浪费 token。skill 的价值只在五处：①来源核验/防幻觉 ②不可靠的领域事实
  （条号/阈值/最新司法解释状态/强制条款）③易跳步骤的强制函数 ④格式与法域行文惯例 ⑤工具编排。
- **L1 防幻觉第一**：法条/案例绝不靠模型记忆；每条法律命题挂且仅挂一个来源标签。

宪章若需修订，改 `PRINCIPLES.md` 并在其《变更日志》追加一行起因。

## 常用命令

要求 Python 3.8+。

```bash
pip install -r requirements-dev.txt              # 装 python-docx + pytest（开发/测试栈）

# 结构校验——改动任一 skill 的 references/ 或 rules/ 后必跑，绿了才提交
python contract-review/validate.py               # 预期 ✅ 通过（退出码 0；有硬错误退 1）
python legal-research/validate.py                # 同上

# 单元测试
python -m pytest contract-review/scripts/test_redline_docx.py legal-research/tests/ -q
python -m pytest contract-review/scripts/test_redline_docx.py -q -k <关键字>   # 跑单个测试
```

CI（`.github/workflows/ci.yml`）在每次 push / PR 跑上述 validate + pytest 全部，作为合并前门禁；
打 tag 由 `release-skill.yml` 自动校验 + 打包 + 发 Release，校验不过不发布。

## 架构大图（跨文件才能看懂的部分）

**渐进式披露是核心架构。** 每个 skill 的 `SKILL.md` 只放常驻底线 + 按需读取索引；正文分层进
`references/`（法域中立骨架、输出模板、验证、终检门）与 `rules/<法域>/`（可插拔规则包）。agent 运行时
**分阶段按需读取**，既省 token 又保证深层规则不被跳过。`validate.py` 用**行预算**把这套结构钉死：
SKILL.md ≤80 行（contract）/≤130（research），references 数字前缀文件 ≤260，`_general.md` ≤200，
领域卡 ≤150。改内容时别把该分层的东西塞回 SKILL.md。

**三个 skill 边界互斥、彼此路由**：合同相关 → `contract-review`；法律问题论证/类案检索 →
`legal-research`；按本案知识库给文书模板取证填充 → `document-fill`（论证说理留空、路由回研究/起草）。
均不做起草论证、续约提醒、流程图。改一个 skill 的边界描述时，注意其余 skill 的路由指向要对得上。

**contract-review 的可插拔法域包**：方法骨架（`references/02-methodology.md`）法域无关；中/美法规则各自
成包 `references/rules/cn/`、`rules/us/`。路由层按合同的**法律选择条款**判定法域（**绝不看合同语言**）
并加载对应包。每个包内：`_pack.md`（法域识别信号 + 业务领域登记表 + 推荐 MCP 源）、`_general.md`（通用）、
若干**领域卡**（如 `nda.md`、`sale-of-goods.md`，须含「领域专属失败模式」小节）。**加领域**＝在
`_pack.md` 登记表加一行 + 按 `references/_templates/domain-card-template.md` 新建卡；**加法域**＝按
`references/_templates/pack-template.md` 新建 `rules/<法域>/`，路由层零改动自动发现。`validate.py` 强制
**登记表↔卡文件双向一致**（悬空登记＝硬错误；孤儿卡＝软警告），并对领域卡里出现的**精确法条号**发
anti-leakage 软警告（原则/法条分离——精确条号应交 MCP 核验，别硬编码进规则卡）。

**MCP 法律库接入是两种模式，别混**：
- `contract-review`：MCP 核验是**可选加速器**——核心审查方法论无外部依赖也能跑，接上则实时核验。
- `legal-research`：MCP 是**硬前置**——没有可靠法律库就没有真研究/检索。未接则先引导用户接入
  （`references/09-mcp-setup.md`）、暂停正式产出；唯一例外是用户**显式 opt-in** 的通篇水印降级草稿。

不写死任何具体 MCP 名，运行时发真实探测调用（不只看配置）。推荐源为元典（chineselaw.com），用户填
**本人 Token**；Token 绝不写入 skill 文件、不提交仓库、不随报告输出（仓库只给占位符，见 `SECURITY.md`）。

**来源标签防幻觉（两 skill 共有）**：每条法律命题挂且仅挂一个来源标签（`[MCP核验:…]` /
`[模型知识-未验证]` 等），标签描述"实际来源行为"而非"自信程度"；三轴正交（验证渠道/权威位阶/处置状态）。
`legal-research` 报告产出前必过 `references/48-qc-gate.md` 的 QC 七项**终检门**，不过按**精确回退目标**退回
对应步骤补正，回退设**上限**防死循环。

**红线脚本 `contract-review/scripts/redline_docx.py`**（纯 Python + `python-docx`，运行期只需
`python-docx`）：把 agent 生成的**修订计划**（JSON 数组，每项含 `action`/`anchor_text` 等，
`validate_plan()` 预检必填字段与动作合法性）渲染成真实 Word 修订痕迹（`w:ins`/`w:del`）+ 批注。
**它只渲染、不做法律判断。** 未装 `python-docx` 时自动降级为 markdown 对照稿并返回 `degraded=True`，
不静默失败。锚点匹配是**段落内**范围（`anchor_text` 须能在单段落内定位）；同段多修订已有回归测试。

## 约定

- **只留 main 分支**：本地和云端都只保留 `main`，不新建功能分支（用户明确要求）。
- **TDD**：先写失败测试→看它失败→最小实现；bug 修复必须带复现测试。
- **提交前**：改动 skill 正文后务必跑对应 `validate.py` + pytest，全绿再提交。
- 进度看板 `ROADMAP.md`；变更 `CHANGELOG.md`；贡献流程 `CONTRIBUTING.md`。
