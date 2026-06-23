import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import validate as V

REQUIRED_REFS = ["00-workflow.md","01-intake-scoping.md","02-retrieval.md",
    "03-research-mode.md","04-case-mode.md","05-output-research.md",
    "06-output-case.md","07-citation-currency.md","08-library-maintenance.md"]

def _make_skill(root):
    os.makedirs(os.path.join(root, "references"))
    os.makedirs(os.path.join(root, "corpus", "statutes"))
    os.makedirs(os.path.join(root, "corpus", "cases"))
    with open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write("---\nname: legal-research\ndescription: x\n---\n# 标题\n## 何时使用\n## 任务边界\n")
    for r in REQUIRED_REFS:
        with open(os.path.join(root, "references", r), "w", encoding="utf-8") as f:
            f.write("# " + r + "\n内容\n")
    for k in ("statutes", "cases"):
        with open(os.path.join(root, "corpus", k, "_index.md"), "w", encoding="utf-8") as f:
            f.write("| 路径 |\n|---|\n")

def test_complete_skill_has_no_errors(tmp_path):
    _make_skill(str(tmp_path))
    errors, _ = V.check(str(tmp_path))
    assert errors == []

def test_missing_reference_is_error(tmp_path):
    _make_skill(str(tmp_path))
    os.remove(os.path.join(str(tmp_path), "references", "02-retrieval.md"))
    errors, _ = V.check(str(tmp_path))
    assert any("02-retrieval.md" in e for e in errors)

def test_oversized_skill_body_is_error(tmp_path):
    _make_skill(str(tmp_path))
    with open(os.path.join(str(tmp_path), "SKILL.md"), "a", encoding="utf-8") as f:
        f.write("\n".join("x" for _ in range(60)))
    errors, _ = V.check(str(tmp_path))
    assert any("SKILL.md" in e and "50" in e for e in errors)

def test_missing_corpus_index_is_error(tmp_path):
    _make_skill(str(tmp_path))
    os.remove(os.path.join(str(tmp_path), "corpus", "cases", "_index.md"))
    errors, _ = V.check(str(tmp_path))
    assert any("cases/_index.md" in e for e in errors)
