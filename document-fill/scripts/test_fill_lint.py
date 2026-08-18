import json, os, subprocess, sys
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

def test_extracted_value_must_appear_verbatim_in_quote():
    bad = {"slot_id": "m", "slot_label": "M", "slot_type": "fact",
           "template_context": "{{m}}", "status": "extracted", "value": "李四欠款50万元",
           "source_span": {"source_id": "_md/借条.md", "quote": "李四借款", "locator": "p1"}}
    assert any("Mode-2" in e for e in fill_lint.lint_item(bad, 0))

def test_extracted_verbatim_with_whitespace_noise_passes():
    ok = {"slot_id": "m", "slot_label": "M", "slot_type": "fact",
          "template_context": "{{m}}", "status": "extracted", "value": "张 三",
          "source_span": {"source_id": "a", "quote": "原告张三 到庭", "locator": "p1"}}
    assert fill_lint.lint_item(ok, 0) == []

def test_extracted_missing_value_key_does_not_crash():
    bad = dict(VALID); bad.pop("value")
    errs = fill_lint.lint_item(bad, 0)
    assert any("缺 value" in e for e in errs)

def test_inferred_missing_value_fails():
    bad = {"slot_id": "i", "slot_label": "I", "slot_type": "fact",
           "template_context": "{{i}}", "status": "inferred", "value": "",
           "formula": "a+b", "inferred_from": ["x"]}
    errs = fill_lint.lint_item(bad, 0)
    assert any("缺 value" in e for e in errs)

def test_user_confirmed_missing_value_fails():
    bad = {"slot_id": "u", "slot_label": "U", "slot_type": "fact",
           "template_context": "{{u}}", "status": "user_confirmed", "value": "",
           "confirmed_at": "2026-08-17T10:00:00", "confirmation_note": "口头确认"}
    errs = fill_lint.lint_item(bad, 0)
    assert any("缺 value" in e for e in errs)

def test_user_confirmed_missing_confirmation_note_fails():
    bad = {"slot_id": "u", "slot_label": "U", "slot_type": "fact",
           "template_context": "{{u}}", "status": "user_confirmed", "value": "2023年3月1日",
           "confirmed_at": "2026-08-17T10:00:00"}
    errs = fill_lint.lint_item(bad, 0)
    assert any("confirmation_note" in e for e in errs)

def test_pending_drafting_on_fact_fails():
    bad = {"slot_id": "f", "slot_label": "F", "slot_type": "fact",
           "template_context": "{{f}}", "status": "pending_drafting", "value": None}
    errs = fill_lint.lint_item(bad, 0)
    assert any("pending_drafting" in e for e in errs)

def test_pending_drafting_on_legal_claim_fails():
    bad = {"slot_id": "lc", "slot_label": "LC", "slot_type": "legal_claim",
           "template_context": "{{lc}}", "status": "pending_drafting", "value": None}
    errs = fill_lint.lint_item(bad, 0)
    assert any("pending_drafting" in e for e in errs)

def test_ambiguous_with_nonnull_value_fails():
    bad = {"slot_id": "b", "slot_label": "B", "slot_type": "fact",
           "template_context": "{{b}}", "status": "ambiguous", "value": "甲",
           "candidates": [
               {"value": "甲", "source_span": {"source_id": "a", "quote": "甲", "locator": "p1"}},
               {"value": "乙", "source_span": {"source_id": "b", "quote": "乙", "locator": "p2"}}]}
    errs = fill_lint.lint_item(bad, 0)
    assert any("value" in e and "ambiguous" in e for e in errs)

def test_duplicate_slot_id_fails():
    plan = [dict(VALID), dict(VALID)]
    errors, _ = fill_lint.lint_plan(plan)
    assert any("slot_id" in e and "重复" in e for e in errors) or any(VALID["slot_id"] in e for e in errors)

def test_cli_exit_codes():
    base = ["python", os.path.join(HERE, "fill_lint.py")]
    assert subprocess.run(base + [os.path.join(HERE, "sample_fill_plan.json")]).returncode == 0
    assert subprocess.run(base + [os.path.join(HERE, "sample_fill_plan.invalid.json")]).returncode == 1
