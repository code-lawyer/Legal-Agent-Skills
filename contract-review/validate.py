#!/usr/bin/env python3
"""结构校验器：渐进式披露行预算 + 必备标题 + anti-leakage 软警告。
用法: python validate.py        在 contract-review/ 目录下运行
退出码: 0 通过, 1 有硬错误。"""
import os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(ROOT, "references")
errors, warnings = [], []

def body_lines(path):
    """返回去掉 YAML frontmatter 后的正文行数。只把整行 --- 当作分隔符。"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if lines and lines[0].strip() == "---":
        try:
            end = lines.index("---", 1)   # 下一个独立成行的 ---
            lines = lines[end + 1:]
        except ValueError:
            pass
    return len(lines)

def has_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        return f.read().startswith("---")

def headings(path):
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.lstrip().startswith("#")]

def section_text(path, heading_kw):
    """返回标题含 heading_kw 的小节正文（到下一个同级或更高级标题前）。"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    out, capture, level = [], False, 0
    for l in lines:
        s = l.lstrip()
        if s.startswith("#"):
            hl = len(s) - len(s.lstrip("#"))
            if capture and hl <= level:
                break
            if heading_kw in l:
                capture, level = True, hl
                continue
        if capture:
            out.append(l)
    return "\n".join(out)

def require(cond, msg):
    if not cond: errors.append(msg)

# 1) SKILL.md：有 frontmatter，body ≤ 80 行
skill = os.path.join(ROOT, "SKILL.md")
require(os.path.exists(skill), "缺 SKILL.md")
if os.path.exists(skill):
    require(has_frontmatter(skill), "SKILL.md 缺 YAML frontmatter")
    n_skill = body_lines(skill)
    require(n_skill <= 80, f"SKILL.md 正文 {n_skill} 行 > 80（违反渐进式披露）")

# 2) 框架参考文件：glob 自动发现所有数字前缀 .md，存在且 ≤ 260 行
for p in sorted(glob.glob(os.path.join(REF, "[0-9]*.md"))):
    n = body_lines(p)
    require(n <= 260, f"references/{os.path.basename(p)} {n} 行 > 260")
# 核心框架文件必须存在
for name in ["00-workflow.md","01-jurisdiction-routing.md","02-methodology.md",
             "06-output-and-severity.md","07-verification.md","08-redline.md"]:
    require(os.path.exists(os.path.join(REF, name)), f"缺 references/{name}")

# 3) 法域包：每个 rules/<法域>/ 必须有 _pack.md + _general.md
RULES = os.path.join(REF, "rules")
if os.path.isdir(RULES):
    for pack in sorted(os.listdir(RULES)):
        pdir = os.path.join(RULES, pack)
        if not os.path.isdir(pdir): continue
        packmd = os.path.join(pdir, "_pack.md")
        require(os.path.exists(packmd), f"rules/{pack}/ 缺 _pack.md")
        genmd = os.path.join(pdir, "_general.md")
        require(os.path.exists(genmd), f"rules/{pack}/ 缺 _general.md")
        if os.path.exists(genmd):
            ng = body_lines(genmd)
            require(ng <= 200, f"rules/{pack}/_general.md {ng} 行 > 200（违反渐进式披露）")
        # _pack.md 必备标题 + 解析业务领域登记表登记的卡文件名
        registered = set()
        if os.path.exists(packmd):
            h = " ".join(headings(packmd))
            require("法域识别信号" in h, f"rules/{pack}/_pack.md 缺『法域识别信号』")
            require("业务领域登记表" in h, f"rules/{pack}/_pack.md 缺『业务领域登记表』")
            require("推荐" in h and "MCP" in h, f"rules/{pack}/_pack.md 缺『推荐 MCP 源』")
            registered = set(re.findall(r"([A-Za-z0-9_\-]+\.md)",
                                        section_text(packmd, "业务领域登记表")))
        # 领域卡（非下划线开头的 .md）：≤150 行 + 含「领域专属失败模式」+ anti-leakage 软警告
        existing = set()
        for fn in sorted(os.listdir(pdir)):
            if not fn.endswith(".md") or fn.startswith("_"): continue
            existing.add(fn)
            fp = os.path.join(pdir, fn)
            n = body_lines(fp)
            require(n <= 150, f"rules/{pack}/{fn} {n} 行 > 150")
            require("领域专属失败模式" in " ".join(headings(fp)),
                    f"rules/{pack}/{fn} 缺『领域专属失败模式』小节")
            with open(fp, encoding="utf-8") as f:
                content = f.read()
            # anti-leakage 软警告：规则卡不应硬编码精确法条号
            if re.search(r"第[\d一二三四五六七八九十百千零]+条(?![件款])", content):
                warnings.append(f"rules/{pack}/{fn} 出现精确法条号，确认是否应交 MCP（原则/法条分离）")
        # 登记表 ↔ 卡文件 双向一致性
        for fn in sorted(registered - existing):
            errors.append(f"rules/{pack}/_pack.md 登记表指向 {fn}，但该领域卡不存在（悬空登记→运行时读取失败）")
        for fn in sorted(existing - registered):
            warnings.append(f"rules/{pack}/{fn} 未登记进 _pack.md 业务领域登记表（孤儿卡→路由层永不加载）")

print("=== 校验结果 ===")
for w in warnings: print("⚠️ ", w)
for e in errors: print("❌ ", e)
if not errors:
    print(f"✅ 通过（{len(warnings)} 条软警告）")
    sys.exit(0)
print(f"\n失败：{len(errors)} 个硬错误")
sys.exit(1)
