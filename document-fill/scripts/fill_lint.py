#!/usr/bin/env python3
"""fill_lint.py — 文书填充计划的确定性闸门。
读取填充计划 JSON，机检来源锚定完整性与状态合法性，输出覆盖率账本；有硬错误退出码非 0。
用法: python fill_lint.py <fill_plan.json>"""
import json, re, sys

VALID_STATUS = {"extracted", "inferred", "user_confirmed", "ambiguous", "gap", "pending_drafting"}
VALID_SLOT_TYPE = {"fact", "legal_claim", "argument"}

def _norm(s):
    """消除格式噪声（collapse 空白），用于 Mode-2 逐字比对；数字与文字精确保留。"""
    return re.sub(r"\s+", "", s or "")

def lint_item(item, idx):
    errors = []
    sid = item.get("slot_id", f"#{idx}")
    st = item.get("status")
    stype = item.get("slot_type")
    if stype not in VALID_SLOT_TYPE:
        errors.append(f"[{sid}] slot_type 非法或缺失: {stype!r}")
    if st not in VALID_STATUS:
        errors.append(f"[{sid}] status 非法或缺失: {st!r}")
        return errors  # 状态非法则后续判定无意义
    if stype == "argument" and st != "pending_drafting":
        errors.append(f"[{sid}] 论证型 slot 必须 status=pending_drafting（论证不由本 skill 填），实际 {st}")
    if st == "pending_drafting" and stype != "argument":
        errors.append(f"[{sid}] pending_drafting 只能用于 argument 型 slot，实际 slot_type={stype}")
    if st == "extracted":
        span = item.get("source_span") or {}
        if not item.get("value", ""):
            errors.append(f"[{sid}] extracted 缺 value")
        if not (span.get("source_id") and span.get("quote") and span.get("locator")):
            errors.append(f"[{sid}] extracted 的 source_span 必须含 source_id/quote/locator")
        elif _norm(item.get("value", "")) not in _norm(span["quote"]):
            errors.append(f"[{sid}] Mode-2 校验失败：value「{item.get('value', '')}」未在 source_span.quote 逐字命中")
    elif st == "inferred":
        if not item.get("value"):
            errors.append(f"[{sid}] inferred 缺 value")
        if not item.get("formula"):
            errors.append(f"[{sid}] inferred 缺 formula")
        if not item.get("inferred_from"):
            errors.append(f"[{sid}] inferred 缺 inferred_from（所依据锚点）")
    elif st == "user_confirmed":
        if not item.get("value"):
            errors.append(f"[{sid}] user_confirmed 缺 value")
        if not item.get("confirmed_at"):
            errors.append(f"[{sid}] user_confirmed 缺 confirmed_at")
        if not item.get("confirmation_note"):
            errors.append(f"[{sid}] user_confirmed 缺 confirmation_note")
    elif st == "ambiguous":
        if item.get("value") is not None:
            errors.append(f"[{sid}] ambiguous 的 value 必须为 null（取值须留在 candidates 中并列，不得预先定论）")
        cands = item.get("candidates") or []
        if len(cands) < 2:
            errors.append(f"[{sid}] ambiguous 须至少 2 个 candidates 并列交人裁决")
        elif any(not (c.get("source_span") or {}).get("quote") for c in cands):
            errors.append(f"[{sid}] ambiguous 每个 candidate 须带 source_span.quote")
    elif st == "gap":
        if item.get("value"):
            errors.append(f"[{sid}] gap 不应有 value（未找到即留空）")
    return errors

def lint_plan(plan):
    errors = []
    ledger = {k: 0 for k in VALID_STATUS}
    if not isinstance(plan, list):
        return (["填充计划必须是 JSON 数组"], ledger)
    seen_slot_ids = set()
    dup_slot_ids = set()
    for i, item in enumerate(plan):
        errors.extend(lint_item(item, i))
        st = item.get("status")
        if st in ledger:
            ledger[st] += 1
        sid = item.get("slot_id")
        if sid is not None:
            if sid in seen_slot_ids:
                dup_slot_ids.add(sid)
            seen_slot_ids.add(sid)
    for sid in sorted(dup_slot_ids):
        errors.append(f"[{sid}] slot_id 在计划内重复出现，必须全局唯一")
    return (errors, ledger)

def main(argv):
    if len(argv) != 2:
        print("用法: python fill_lint.py <fill_plan.json>")
        return 2
    with open(argv[1], encoding="utf-8") as f:
        plan = json.load(f)
    errors, ledger = lint_plan(plan)
    print("=== 覆盖率账本 ===")
    for k in ["extracted", "inferred", "user_confirmed", "ambiguous", "gap", "pending_drafting"]:
        print(f"  {k}: {ledger[k]}")
    if errors:
        print(f"\n=== {len(errors)} 个硬错误 ===")
        for e in errors:
            print("❌ ", e)
        return 1
    print("\n✅ 通过：所有取证项锚定完整、Mode-2 逐字命中")
    return 0

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
