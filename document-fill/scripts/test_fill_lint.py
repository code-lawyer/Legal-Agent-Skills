import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

def _load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)

def test_samples_load_and_are_lists():
    assert isinstance(_load("sample_fill_plan.json"), list)
    assert isinstance(_load("sample_fill_plan.invalid.json"), list)
