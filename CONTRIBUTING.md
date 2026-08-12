# 贡献指南

欢迎为 Legal-Agent-Skills 贡献。本项目是**内容规则为主、工具代码为辅**的 skill
仓库，交付单元是整个 skill 文件夹（不是单个 `SKILL.md`）。

## 环境

- Python 3.8+
- 安装开发/测试依赖：`pip install -r requirements-dev.txt`（含 `python-docx` 与
  `pytest`）。运行期 skill 本身只需 `python-docx`（见
  `contract-review/scripts/requirements.txt`）。

## 提交前必须绿

```bash
# 1) 结构校验（改动 references/ 或 rules/ 后必跑）
python contract-review/validate.py      # 预期 ✅ 通过
python legal-research/validate.py       # 预期 ✅ 通过

# 2) 单元测试
python -m pytest contract-review/scripts/test_redline_docx.py legal-research/tests/ -q
```

CI（`.github/workflows/ci.yml`）会在每次 push / PR 跑上述全部；本地先跑绿再提交。

## 扩展 contract-review

- **加业务领域**：在对应 `rules/<法域>/_pack.md` 登记表加一行 + 按
  `references/_templates/domain-card-template.md` 新建一个领域卡。
- **加法域**（如香港）：按 `references/_templates/pack-template.md` 新建
  `rules/hk/` 目录，路由层自动发现。
- 改完跑 `python contract-review/validate.py` 确认登记表↔卡文件双向一致。

## 修订计划（红线脚本）

`redline_docx.py` 只渲染修订计划、不做法律判断。计划为 JSON 数组，每项按动作带
必填字段（`validate_plan()` 会校验）：

- `replace`：`anchor_text` + (`tracked_changes` | `clean_version`)
- `delete`：`anchor_text`
- `insert`：`anchor_text` + `clean_version`
- `comment`：`anchor_text`

## 代码与提交约定

- 遵循 TDD：先写失败测试，看它失败，再写最小实现（bug 修复必须带复现测试）。
- 提交信息用祈使句、说明「为什么」；改动 skill 正文后务必跑校验与测试。
- 不把任何真实 API Token 写入 skill 文件或提交（见 `SECURITY.md`）。

## 免责

本仓库 skill 产出为初步专业分析、不构成最终法律意见；据此行动前须经执业律师复核。
