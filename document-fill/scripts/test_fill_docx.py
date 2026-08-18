import os, json
import pytest
import fill_docx

HERE = os.path.dirname(os.path.abspath(__file__))

def _plan():
    with open(os.path.join(HERE, "sample_fill_plan.json"), encoding="utf-8") as f:
        return json.load(f)

def test_render_value_markers():
    plan = {p["slot_id"]: p for p in _plan()}
    assert fill_docx.render_value(plan["plaintiff_name"]) == "张三"
    assert "缺口" in fill_docx.render_value(plan["guarantor"])
    assert "待起草" in fill_docx.render_value(plan["legal_argument"])
    assert "存疑" in fill_docx.render_value(plan["breach_date"])

def test_fill_markdown_replaces_tokens():
    out = fill_docx.fill_markdown("原告：{{plaintiff_name}}；担保人：{{guarantor}}", _plan())
    assert "张三" in out and "{{plaintiff_name}}" not in out and "缺口" in out

def test_txt_template_degrades(tmp_path):
    tpl = tmp_path / "t.txt"; tpl.write_text("原告：{{plaintiff_name}}", encoding="utf-8")
    res = fill_docx.fill_docx(str(tpl), _plan(), str(tmp_path / "out.docx"))
    assert res["degraded"] is True
    assert "张三" in (tmp_path / "out.md").read_text(encoding="utf-8")

def test_docx_template_fills(tmp_path):
    docx = pytest.importorskip("docx")
    tpl = tmp_path / "t.docx"
    d = docx.Document(); d.add_paragraph("原告：{{plaintiff_name}}"); d.save(str(tpl))
    res = fill_docx.fill_docx(str(tpl), _plan(), str(tmp_path / "out.docx"))
    assert res["degraded"] is False
    filled = docx.Document(res["output"])
    assert "张三" in filled.paragraphs[0].text and "{{" not in filled.paragraphs[0].text

def test_render_value_none_does_not_render_literal_none():
    item = {"slot_id": "x", "slot_label": "X", "slot_type": "fact",
            "status": "extracted", "value": None}
    out = fill_docx.render_value(item)
    assert out == ""
    assert out != "None"

def test_docx_table_cell_fills(tmp_path):
    docx = pytest.importorskip("docx")
    tpl = tmp_path / "t_table.docx"
    d = docx.Document()
    table = d.add_table(rows=1, cols=1)
    table.rows[0].cells[0].paragraphs[0].add_run("{{plaintiff_name}}")
    d.save(str(tpl))
    res = fill_docx.fill_docx(str(tpl), _plan(), str(tmp_path / "out_table.docx"))
    assert res["degraded"] is False
    filled = docx.Document(res["output"])
    cell_text = filled.tables[0].rows[0].cells[0].text
    assert cell_text == "张三"
    assert "{{" not in cell_text
