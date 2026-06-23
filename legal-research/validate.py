#!/usr/bin/env python3
"""skill 结构校验：SKILL.md frontmatter + 行预算 + 必备标题；references 齐全 + 行预算；
corpus 索引存在。用法: 在 legal-research/ 下 python validate.py。退出码 0 通过 / 1 硬错误。"""
import os, sys, glob
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_REFS = ["00-workflow.md","01-intake-scoping.md","02-retrieval.md",
    "03-research-mode.md","04-case-mode.md","05-output-research.md",
    "06-output-case.md","07-citation-currency.md","08-library-maintenance.md"]

def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def _body_lines(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            lines = lines[lines.index("---", 1) + 1:]
        except ValueError:
            pass
    return len(lines)

def _headings_text(text):
    return " ".join(l.strip() for l in text.splitlines() if l.lstrip().startswith("#"))

def check(root):
    errors, warnings = [], []
    def require(cond, msg):
        if not cond:
            errors.append(msg)
    skill = os.path.join(root, "SKILL.md")
    require(os.path.exists(skill), "缺 SKILL.md")
    if os.path.exists(skill):
        skill_text = _read(skill)
        require(skill_text.startswith("---"), "SKILL.md 缺 YAML frontmatter")
        n = _body_lines(skill_text)
        require(n <= 50, f"SKILL.md 正文 {n} 行 > 50（违反渐进式披露）")
        h = _headings_text(skill_text)
        require("何时使用" in h, "SKILL.md 缺『何时使用』标题")
        require("任务边界" in h, "SKILL.md 缺『任务边界』标题")
    ref = os.path.join(root, "references")
    for name in REQUIRED_REFS:
        require(os.path.exists(os.path.join(ref, name)), f"缺 references/{name}")
    for p in sorted(glob.glob(os.path.join(ref, "*.md"))):
        n = _body_lines(_read(p))
        require(n <= 260, f"references/{os.path.basename(p)} {n} 行 > 260")
    for k in ("statutes", "cases"):
        idx = os.path.join(root, "corpus", k, "_index.md")
        require(os.path.exists(idx), f"缺 corpus/{k}/_index.md")
    return errors, warnings

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    errors, warnings = check(root)
    print("=== 校验结果 ===")
    for w in warnings: print("⚠️ ", w)
    for e in errors: print("❌ ", e)
    if not errors:
        print(f"✅ 通过（{len(warnings)} 条软警告）")
        sys.exit(0)
    print(f"\n失败：{len(errors)} 个硬错误")
    sys.exit(1)

if __name__ == "__main__":
    main()
