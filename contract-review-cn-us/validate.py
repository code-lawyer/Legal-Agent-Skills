#!/usr/bin/env python3
"""结构校验器：渐进式披露行预算 + 必备标题 + anti-leakage 软警告。
用法: python validate.py        在 contract-review-cn-us/ 目录下运行
退出码: 0 通过, 1 有硬错误。"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(ROOT, "references")
errors, warnings = [], []

def body_lines(path):
    """返回去掉 YAML frontmatter 后的正文行数。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.startswith("---"):
        parts = text.split("---", 2)
        text = parts[2] if len(parts) == 3 else text
    return len([l for l in text.splitlines()])

def has_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        return f.read().startswith("---")

def headings(path):
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.lstrip().startswith("#")]

def require(cond, msg):
    if not cond: errors.append(msg)

# 1) SKILL.md：有 frontmatter，body ≤ 80 行
skill = os.path.join(ROOT, "SKILL.md")
require(os.path.exists(skill), "缺 SKILL.md")
if os.path.exists(skill):
    require(has_frontmatter(skill), "SKILL.md 缺 YAML frontmatter")
    n_skill = body_lines(skill)
    require(n_skill <= 80, f"SKILL.md 正文 {n_skill} 行 > 80（违反渐进式披露）")

# 2) 框架参考文件：存在且 ≤ 260 行
FRAMEWORK = ["00-workflow.md","01-jurisdiction-routing.md","02-methodology.md",
             "06-output-and-severity.md","07-verification.md","08-redline.md"]
for name in FRAMEWORK:
    p = os.path.join(REF, name)
    if not os.path.exists(p):
        errors.append(f"缺 references/{name}")
        continue
    n = body_lines(p)
    require(n <= 260, f"references/{name} {n} 行 > 260")

# 3) 法域包：每个 rules/<法域>/ 必须有 _pack.md + _general.md
RULES = os.path.join(REF, "rules")
if os.path.isdir(RULES):
    for pack in sorted(os.listdir(RULES)):
        pdir = os.path.join(RULES, pack)
        if not os.path.isdir(pdir): continue
        packmd = os.path.join(pdir, "_pack.md")
        require(os.path.exists(packmd), f"rules/{pack}/ 缺 _pack.md")
        require(os.path.exists(os.path.join(pdir,"_general.md")), f"rules/{pack}/ 缺 _general.md")
        # _pack.md 必备标题
        if os.path.exists(packmd):
            h = " ".join(headings(packmd))
            require("法域识别信号" in h, f"rules/{pack}/_pack.md 缺『法域识别信号』")
            require("业务领域登记表" in h, f"rules/{pack}/_pack.md 缺『业务领域登记表』")
            require("推荐" in h and "MCP" in h, f"rules/{pack}/_pack.md 缺『推荐 MCP 源』")
        # 领域卡（非下划线开头的 .md）：≤150 行 + 含「领域专属失败模式」+ anti-leakage 软警告
        for fn in sorted(os.listdir(pdir)):
            if not fn.endswith(".md") or fn.startswith("_"): continue
            fp = os.path.join(pdir, fn)
            n = body_lines(fp)
            require(n <= 150, f"rules/{pack}/{fn} {n} 行 > 150")
            require("领域专属失败模式" in " ".join(headings(fp)),
                    f"rules/{pack}/{fn} 缺『领域专属失败模式』小节")
            with open(fp, encoding="utf-8") as f:
                content = f.read()
            # anti-leakage 软警告：规则卡不应硬编码精确法条号
            if re.search(r"第[\d一二三四五六七八九十百千零]+条", content):
                warnings.append(f"rules/{pack}/{fn} 出现精确法条号，确认是否应交 MCP（原则/法条分离）")

print("=== 校验结果 ===")
for w in warnings: print("⚠️ ", w)
for e in errors: print("❌ ", e)
if not errors:
    print(f"✅ 通过（{len(warnings)} 条软警告）")
    sys.exit(0)
print(f"\n失败：{len(errors)} 个硬错误")
sys.exit(1)
