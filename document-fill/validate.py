#!/usr/bin/env python3
"""document-fill 结构校验（stdlib）。行预算 + 必备文件/引用 + SKILL 硬不变量锚点 + 无悬空引用。
用法: python validate.py（在 document-fill/ 下）。退出码 0 通过 / 1 有硬错误。"""
import os, re, sys

REQUIRED_REFS = ["00-workflow", "10-kb-access", "20-slot-and-fill", "30-output-and-report"]
SKILL_ANCHORS = ["宁可查不到，也不编造", "闭世界", "缺口"]
SKILL_BUDGET = 100
REF_BUDGET = 260
REF_RE = re.compile(r"references/(\d{2}-[a-z-]+)\.md")

def _body_line_count(text):
    """去掉 YAML frontmatter 后的正文行数。只把整行 --- 当分隔符。"""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        try:
            lines = lines[lines.index("---", 1) + 1:]
        except ValueError:
            pass
    return len(lines)

def validate_skill(root):
    errors = []
    refs_dir = os.path.join(root, "references")
    skill = os.path.join(root, "SKILL.md")
    skill_text = ""

    if not os.path.exists(skill):
        errors.append("缺 SKILL.md")
    else:
        with open(skill, encoding="utf-8") as f:
            skill_text = f.read()
        if not skill_text.startswith("---"):
            errors.append("SKILL.md 缺 YAML frontmatter")
        n = _body_line_count(skill_text)
        if n > SKILL_BUDGET:
            errors.append(f"SKILL.md 正文 {n} 行 > {SKILL_BUDGET}（违反渐进式披露）")
        for a in SKILL_ANCHORS:
            if a not in skill_text:
                errors.append(f"SKILL.md 缺硬不变量锚点「{a}」")

    if not os.path.exists(os.path.join(root, "README.md")):
        errors.append("缺 README.md")

    existing = set()
    texts = [skill_text]
    if os.path.isdir(refs_dir):
        for fn in sorted(os.listdir(refs_dir)):
            if fn.endswith(".md"):
                existing.add(fn[:-3])
                with open(os.path.join(refs_dir, fn), encoding="utf-8") as f:
                    text = f.read()
                texts.append(text)
                n = _body_line_count(text)
                if n > REF_BUDGET:
                    errors.append(f"references/{fn} {n} 行 > {REF_BUDGET}")
    for name in REQUIRED_REFS:
        if name not in existing:
            errors.append(f"缺 references/{name}.md")

    for t in texts:
        for ref in REF_RE.findall(t):
            if ref not in existing:
                errors.append(f"悬空引用 references/{ref}.md（被引用但不存在）")

    return errors

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    errors = validate_skill(root)
    print("=== document-fill 校验 ===")
    for e in errors:
        print("❌ ", e)
    if not errors:
        print("✅ 通过")
        return 0
    print(f"失败：{len(errors)} 个硬错误")
    return 1

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
