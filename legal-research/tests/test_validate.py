import os
import sys
import textwrap
import pathlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from validate import validate_skill  # noqa: E402

REFS = [
    "00-routing-intake", "10-retrieval-core", "20-research-skeleton",
    "21-case-skeleton", "30-analysis-guardrails", "40-output-research",
    "41-output-case", "48-qc-gate", "49-citation-disclaimer",
]


def _skeleton(tmp_path, *, skill_md=None, refs=None, guardrail_lines=10):
    (tmp_path / "references").mkdir()
    default_skill = textwrap.dedent(
        """\
        # legal-research
        每条命题必须挂且仅挂一个来源标签。
        报告产出前必过终检门（见 48）。
        正式交付必附免责声明。
        """
    )
    (tmp_path / "SKILL.md").write_text(skill_md or default_skill, encoding="utf-8")
    (tmp_path / "README.md").write_text("# legal-research\n", encoding="utf-8")
    refs = refs if refs is not None else REFS
    for name in refs:
        body = "# " + name + "\n"
        if name == "30-analysis-guardrails":
            body += "内容\n" * guardrail_lines
        (tmp_path / "references" / (name + ".md")).write_text(body, encoding="utf-8")
    return str(tmp_path)


def test_complete_skill_passes(tmp_path):
    errors, warnings = validate_skill(_skeleton(tmp_path))
    assert errors == []


def test_missing_reference_is_error(tmp_path):
    d = _skeleton(tmp_path, refs=[r for r in REFS if r != "48-qc-gate"])
    errors, _ = validate_skill(d)
    assert any("48-qc-gate" in e for e in errors)


def test_dangling_reference_is_error(tmp_path):
    skill = "# legal-research\n必须挂且仅挂一个来源标签\n终检门\n免责声明\n见 references/99-ghost.md\n"
    errors, _ = validate_skill(_skeleton(tmp_path, skill_md=skill))
    assert any("99-ghost" in e for e in errors)


def test_missing_h1_is_error(tmp_path):
    d = _skeleton(tmp_path)
    (pathlib.Path(d) / "references" / "48-qc-gate.md").write_text("无标题\n", encoding="utf-8")
    errors, _ = validate_skill(d)
    assert any("48-qc-gate" in e and "标题" in e for e in errors)


def test_skill_missing_invariant_is_error(tmp_path):
    skill = "# legal-research\n随便写点什么\n"
    errors, _ = validate_skill(_skeleton(tmp_path, skill_md=skill))
    assert any("终检门" in e or "来源标签" in e or "免责" in e for e in errors)


def test_oversized_guardrails_is_error(tmp_path):
    errors, _ = validate_skill(_skeleton(tmp_path, guardrail_lines=200))
    assert any("30-analysis-guardrails" in e and "行" in e for e in errors)


def test_corpus_leakage_is_warning(tmp_path):
    d = _skeleton(tmp_path)
    (pathlib.Path(d) / "references" / "10-retrieval-core.md").write_text(
        "# 10-retrieval-core\n先查本地库 corpus 命中\n", encoding="utf-8"
    )
    _, warnings = validate_skill(d)
    assert any("corpus" in w or "本地库" in w for w in warnings)
