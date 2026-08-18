import json, os
import fill_lint

HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)

def test_samples_load_and_are_lists():
    assert isinstance(_load("sample_fill_plan.json"), list)
    assert isinstance(_load("sample_fill_plan.invalid.json"), list)

VALID = {"slot_id": "s", "slot_label": "L", "slot_type": "fact",
         "template_context": "{{s}}", "status": "extracted", "value": "张三",
         "source_span": {"source_id": "_md/a.md", "quote": "原告张三", "locator": "p1"}}

def test_valid_extracted_passes():
    assert fill_lint.lint_item(dict(VALID), 0) == []

def test_extracted_missing_source_span_fails():
    bad = dict(VALID); bad.pop("source_span")
    errs = fill_lint.lint_item(bad, 0)
    assert any("source_span" in e for e in errs)

def test_argument_must_be_pending_drafting():
    bad = {"slot_id": "a", "slot_label": "A", "slot_type": "argument",
           "template_context": "{{a}}", "status": "extracted", "value": "x",
           "source_span": {"source_id": "a", "quote": "x", "locator": "p1"}}
    errs = fill_lint.lint_item(bad, 0)
    assert any("pending_drafting" in e for e in errs)

def test_ambiguous_needs_two_candidates():
    bad = {"slot_id": "b", "slot_label": "B", "slot_type": "fact",
           "template_context": "{{b}}", "status": "ambiguous", "value": None,
           "candidates": [{"value": "甲", "source_span": {"source_id": "a", "quote": "甲", "locator": "p1"}}]}
    assert any("candidates" in e for e in fill_lint.lint_item(bad, 0))

def test_ledger_counts_by_status():
    _, ledger = fill_lint.lint_plan(_load("sample_fill_plan.json"))
    assert ledger["extracted"] == 1 and ledger["gap"] == 1 and ledger["pending_drafting"] == 1
