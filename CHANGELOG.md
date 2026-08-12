# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式；
两个 skill（`contract-review`、`legal-research`）共用本变更日志，条目注明所属。

## [Unreleased]

### Fixed
- **contract-review / 红线脚本**：修复同一段落连续应用多个修订时，先前的
  `w:ins/w:del` 修订痕迹被顶到段首、且 prefix/suffix 文本错位的缺陷。改为就地
  改写、保留既有修订痕迹（`redline_docx.py::_rewrite_paragraph_span`）。

### Added
- **contract-review / 红线脚本**：新增修订计划 `validate_plan()` 预检门——渲染前
  校验计划形状与各动作必填字段（replace/delete/insert/comment），CLI 校验不过
  即以退出码 2 失败，避免静默产出残缺 `.docx`。
- **CI**：新增 `.github/workflows/ci.yml`，每次 push / PR 运行两个 `validate.py`
  与 `pytest`，作为合并前质量门禁（区别于仅在打 tag 时打包发布的 release 流程）。
- **开发依赖**：新增根目录 `requirements-dev.txt`（`python-docx` + `pytest`）。
- **治理**：新增 `LICENSE`（MIT）、`CHANGELOG.md`、`CONTRIBUTING.md`、
  `SECURITY.md`、`ROADMAP.md`。

## [1.1.0] - 2026-08-06

对应标签 `contract-review-v1.1.0`、`legal-research-v1.1.0`。

### contract-review
- 中美双法域合同审查：法域判定 → 按法域加载可插拔规则包 → 逐条审查 → 双轴风险
  问题清单 + 可选 Word 红线稿。
- 中国法领域卡：买卖、SaaS/服务、NDA、借贷融资、劳动；美国法：买卖、SaaS/服务、
  NDA；10 类中国法标准条款库。
- 真实 Word 修订痕迹（`w:ins`/`w:del`）+ 批注生成；无 `python-docx` 时降级为
  markdown 对照稿。
- MCP 法规核验为可选加速器（默认离线可运行）。

### legal-research
- 法律研究 / 类案检索 / 复合研究三条路径。
- MCP 硬前置、来源标签三轴、QC1–QC7 终检门 + 精确回退。

### 通用
- 渐进式披露结构、`validate.py` 结构校验、打 tag 自动校验 + 打包 + 发 Release。
