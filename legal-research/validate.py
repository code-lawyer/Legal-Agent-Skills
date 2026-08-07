#!/usr/bin/env python3
"""legal-research 结构校验（stdlib）。检查文件完整性、无悬空引用、必备标题、
行预算、SKILL.md 硬不变量、corpus 残留软警告。"""
import os
import re
import sys

REQUIRED_REFS = [
    "00-routing-intake", "10-retrieval-core", "20-research-skeleton",
    "21-case-skeleton", "30-analysis-guardrails", "40-output-research",
    "41-output-case", "48-qc-gate", "49-citation-disclaimer",
]
LINE_BUDGET = {"SKILL.md": 130, "30-analysis-guardrails.md": 180}
DEFAULT_REF_BUDGET = 260
SKILL_ANCHORS = ["必须挂且仅挂一个", "终检门", "免责声明"]
LEAKAGE = ["corpus", "本地库", "makeitdown", "corpus_index"]
REF_PATH_RE = re.compile(r"(?:references/)?((?:\d{2})-[a-z-]+)\.md")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def validate_skill(skill_dir):
    errors, warnings = [], []
    refs_dir = os.path.join(skill_dir, "references")

    # 1. 必备文件
    for base in ["SKILL.md", "README.md"]:
        if not os.path.isfile(os.path.join(skill_dir, base)):
            errors.append(f"缺失必备文件：{base}")
    present_refs = set()
    for name in REQUIRED_REFS:
        p = os.path.join(refs_dir, name + ".md")
        if os.path.isfile(p):
            present_refs.add(name)
        else:
            errors.append(f"缺失必备 reference：{name}.md")

    # 收集所有 md 文件
    md_files = []
    if os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
        md_files.append(os.path.join(skill_dir, "SKILL.md"))
    if os.path.isfile(os.path.join(skill_dir, "README.md")):
        md_files.append(os.path.join(skill_dir, "README.md"))
    if os.path.isdir(refs_dir):
        for fn in sorted(os.listdir(refs_dir)):
            if fn.endswith(".md"):
                md_files.append(os.path.join(refs_dir, fn))

    existing_ref_stems = {
        fn[:-3] for fn in os.listdir(refs_dir) if fn.endswith(".md")
    } if os.path.isdir(refs_dir) else set()

    for path in md_files:
        text = _read(path)
        base = os.path.basename(path)
        lines = text.splitlines()

        # 3. 必备 H1（仅 references）
        if os.path.dirname(path).endswith("references"):
            first = next((ln for ln in lines if ln.strip()), "")
            if not first.startswith("# "):
                errors.append(f"{base}：缺首行 H1 标题（须以 '# ' 开头）")

        # 2. 悬空引用
        for m in REF_PATH_RE.finditer(text):
            stem = m.group(1)
            if stem not in existing_ref_stems:
                errors.append(f"{base}：悬空引用 {m.group(0)}（目标不存在）")

        # 5. 行预算
        budget = LINE_BUDGET.get(base, DEFAULT_REF_BUDGET if base not in ("README.md",) else None)
        if budget is not None and len(lines) > budget:
            errors.append(f"{base}：行数 {len(lines)} 超预算 {budget}")

        # 6. corpus 残留（迁移/历史行豁免）
        for ln in lines:
            if ("迁移" in ln) or ("历史" in ln):
                continue
            for kw in LEAKAGE:
                if kw in ln:
                    warnings.append(f"{base}：疑似 corpus 残留「{kw}」— {ln.strip()[:40]}")

    # 4. SKILL.md 硬不变量
    skill_path = os.path.join(skill_dir, "SKILL.md")
    if os.path.isfile(skill_path):
        stext = _read(skill_path)
        for anchor in SKILL_ANCHORS:
            if anchor not in stext:
                errors.append(f"SKILL.md：缺硬不变量锚点「{anchor}」")

    return errors, warnings


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    errors, warnings = validate_skill(skill_dir)
    print("=== 校验结果 ===")
    for w in warnings:
        print(f"⚠️  {w}")
    if errors:
        for e in errors:
            print(f"❌ {e}")
        print(f"❌ 失败（{len(errors)} 错误 / {len(warnings)} 软警告）")
        sys.exit(1)
    print(f"✅ 通过（{len(warnings)} 条软警告）")


if __name__ == "__main__":
    main()
