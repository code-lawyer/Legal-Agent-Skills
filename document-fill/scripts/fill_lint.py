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
    if st == "extracted":
        span = item.get("source_span") or {}
        if not item.get("value"):
            errors.append(f"[{sid}] extracted 缺 value")
        if not (span.get("source_id") and span.get("quote") and span.get("locator")):
            errors.append(f"[{sid}] extracted 的 source_span 必须含 source_id/quote/locator")
    elif st == "inferred":
        if not item.get("formula"):
            errors.append(f"[{sid}] inferred 缺 formula")
        if not item.get("inferred_from"):
            errors.append(f"[{sid}] inferred 缺 inferred_from（所依据锚点）")
    elif st == "user_confirmed":
        if not item.get("confirmed_at"):
            errors.append(f"[{sid}] user_confirmed 缺 confirmed_at")
    elif st == "ambiguous":
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
    for i, item in enumerate(plan):
        errors.extend(lint_item(item, i))
        st = item.get("status")
        if st in ledger:
            ledger[st] += 1
    return (errors, ledger)
