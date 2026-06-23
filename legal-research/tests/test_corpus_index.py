import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import corpus_index as ci

CASE_MD = """---
案号: (2023)京01民终12345号
法院: 北京市第一中级人民法院
审级: 二审
案由: 劳动争议
裁判日期: 2023-09-15
当事人: 甲公司 / 乙
裁判要旨: 用人单位未在竞业限制期内支付经济补偿满三个月，劳动者可请求解除竞业限制约定。
关键词: 竞业限制, 经济补偿, 解除
来源: 北大法宝
---
# 正文
本院认为……
"""

def test_parse_frontmatter_reads_flat_scalars():
    meta = ci.parse_frontmatter(CASE_MD)
    assert meta["案号"] == "(2023)京01民终12345号"
    assert meta["审级"] == "二审"
    assert meta["来源"] == "北大法宝"

def test_parse_frontmatter_no_frontmatter_returns_empty():
    assert ci.parse_frontmatter("# 只有正文\n没有 frontmatter") == {}

def test_validate_record_passes_complete_case():
    meta = ci.parse_frontmatter(CASE_MD)
    assert ci.validate_record(meta, "cases") == []

def test_validate_record_flags_missing_case_field():
    meta = ci.parse_frontmatter(CASE_MD)
    del meta["案号"]
    msgs = ci.validate_record(meta, "cases")
    assert any("案号" in m for m in msgs)

def test_validate_record_flags_empty_field():
    meta = ci.parse_frontmatter(CASE_MD)
    meta["案由"] = ""
    msgs = ci.validate_record(meta, "cases")
    assert any("案由" in m for m in msgs)

def test_index_row_case_is_pipe_delimited_and_has_path():
    meta = ci.parse_frontmatter(CASE_MD)
    row = ci.index_row(meta, "cases", "劳动争议/(2023)京01民终12345号.md")
    assert row.startswith("|") and row.rstrip().endswith("|")
    assert "(2023)京01民终12345号" in row
    assert "劳动争议/(2023)京01民终12345号.md" in row

def test_check_consistency_detects_orphan_dangling_dup(tmp_path):
    kind_dir = tmp_path / "cases"
    sub = kind_dir / "劳动争议"
    sub.mkdir(parents=True)
    # 文件存在且被索引
    (sub / "a.md").write_text("x", encoding="utf-8")
    # 孤儿：文件存在未被索引
    (sub / "orphan.md").write_text("x", encoding="utf-8")
    index = kind_dir / "_index.md"
    index.write_text(
        "| 案号 | 法院 | 审级 | 案由 | 裁判日期 | 要旨 | 路径 |\n"
        "|---|---|---|---|---|---|---|\n"
        "| A | 法院 | 一审 | 劳动争议 | 2023 | 摘 | 劳动争议/a.md |\n"
        "| A | 法院 | 一审 | 劳动争议 | 2023 | 摘 | 劳动争议/dup.md |\n"   # 案号 A 重复 + 悬空
        , encoding="utf-8")
    res = ci.check_consistency(str(kind_dir), "cases", str(index))
    assert "劳动争议/orphan.md" in res["orphans"]
    assert "劳动争议/dup.md" in res["dangling"]
    assert "A" in res["duplicates"]

def test_committed_seed_row_matches_index_row():
    """锁定列契约：种子案例的 frontmatter 经 index_row 生成的行，必须逐字出现在
    committed 的 cases/_index.md 中。防止 index_row 列序与 _index.md 表头/行三处漂移。"""
    base = os.path.join(os.path.dirname(__file__), "..")
    rel = "劳动争议/(2023)京01民终12345号.md"
    seed = os.path.join(base, "corpus", "cases", "劳动争议", "(2023)京01民终12345号.md")
    with open(seed, encoding="utf-8") as f:
        meta = ci.parse_frontmatter(f.read())
    expected = ci.index_row(meta, "cases", rel)
    with open(os.path.join(base, "corpus", "cases", "_index.md"), encoding="utf-8") as f:
        index_md = f.read()
    assert expected in index_md
