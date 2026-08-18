import os, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("df_validate", os.path.join(ROOT, "validate.py"))
df_validate = importlib.util.module_from_spec(spec); spec.loader.exec_module(df_validate)

def _mk(tmp, skill_md, refs):
    os.makedirs(os.path.join(tmp, "references"), exist_ok=True)
    with open(os.path.join(tmp, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(skill_md)
    with open(os.path.join(tmp, "README.md"), "w", encoding="utf-8") as f:
        f.write("# document-fill\n")
    for name, body in refs.items():
        with open(os.path.join(tmp, "references", name), "w", encoding="utf-8") as f:
            f.write(body)

GOOD_SKILL = ("---\nname: document-fill\n---\n# 文书填充\n"
              "闭世界：只用本案材料。宁可查不到，也不编造。缺口显性标注。\n"
              "见 references/00-workflow.md\n")
REFS = {f"{n}.md": f"# {n}\n内容\n" for n in
        ["00-workflow", "10-kb-access", "20-slot-and-fill", "30-output-and-report"]}

def test_good_skill_passes(tmp_path):
    _mk(str(tmp_path), GOOD_SKILL, REFS)
    assert df_validate.validate_skill(str(tmp_path)) == []

def test_missing_ref_fails(tmp_path):
    refs = dict(REFS); del refs["10-kb-access.md"]
    _mk(str(tmp_path), GOOD_SKILL, refs)
    assert any("10-kb-access" in e for e in df_validate.validate_skill(str(tmp_path)))

def test_missing_anchor_fails(tmp_path):
    _mk(str(tmp_path), "---\nname: x\n---\n# 文书填充\n没有铁律\n", REFS)
    assert any("锚点" in e for e in df_validate.validate_skill(str(tmp_path)))

def test_dangling_ref_fails(tmp_path):
    skill = GOOD_SKILL + "另见 references/99-ghost.md\n"
    _mk(str(tmp_path), skill, REFS)
    assert any("悬空引用" in e for e in df_validate.validate_skill(str(tmp_path)))
