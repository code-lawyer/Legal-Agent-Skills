#!/usr/bin/env python3
"""语料库工具：frontmatter 解析、记录校验、索引行生成、索引↔文件一致性检查。
仅标准库。供 08 录入流水线与 validate.py 共用。"""
import os, sys, glob
from collections import Counter
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_FIELDS = {
    "statutes": ["法名", "发文机关", "条号范围", "公布日期", "施行日期", "效力状态", "来源"],
    "cases": ["案号", "法院", "审级", "案由", "裁判日期", "裁判要旨", "关键词", "来源"],
}
# 案例 frontmatter 还含可选「当事人(可脱敏)」，不强制。

def parse_frontmatter(text):
    """解析顶部 --- YAML 平铺标量（key: value）。无 frontmatter 返回 {}。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    meta = {}
    for line in lines[1:end]:
        s = line.strip()
        if not s or s.startswith("#") or ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta

def validate_record(meta, kind):
    msgs = []
    for field in REQUIRED_FIELDS[kind]:
        if not meta.get(field, "").strip():
            msgs.append(f"缺必备字段「{field}」")
    return msgs

def index_row(meta, kind, relpath):
    relpath = relpath.replace("\\", "/")
    if kind == "cases":
        gist = meta.get("裁判要旨", "")
        gist = gist[:40] + "…" if len(gist) > 40 else gist
        cells = [meta.get("案号", ""), meta.get("法院", ""), meta.get("审级", ""),
                 meta.get("案由", ""), meta.get("裁判日期", ""), gist, relpath]
    else:
        cells = [meta.get("法名", ""), meta.get("发文机关", ""), meta.get("条号范围", ""),
                 meta.get("施行日期", ""), meta.get("效力状态", ""), relpath]
    return "| " + " | ".join(c.replace("|", "／") for c in cells) + " |"

def _indexed_paths(index_path):
    """解析 _index.md 表格，取每行最后一个非空单元格为路径。返回 (paths, case_numbers)。"""
    paths, case_numbers = [], []
    if not os.path.exists(index_path):
        return paths, case_numbers
    with open(index_path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not any(cells):
                continue
            # 跳过表头与分隔行（分隔行单元格全是 --- 形式）
            if all(set(c) <= set("-: ") for c in cells if c):
                continue
            if cells[-1] == "路径":
                continue  # 表头（末列恒为"路径"）
            path = cells[-1].replace("\\", "/")
            paths.append(path)
            case_numbers.append(cells[0])
    return paths, case_numbers

def check_consistency(corpus_kind_dir, kind, index_path):
    files = set()
    for p in glob.glob(os.path.join(corpus_kind_dir, "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, corpus_kind_dir).replace("\\", "/")
        if os.path.basename(rel) == "_index.md":
            continue
        files.add(rel)
    indexed, case_numbers = _indexed_paths(index_path)
    indexed_set = set(indexed)
    orphans = sorted(files - indexed_set)
    dangling = sorted(indexed_set - files)
    counts = Counter(c for c in case_numbers if c)
    duplicates = sorted(c for c, n in counts.items() if n > 1) if kind == "cases" else []
    return {"orphans": orphans, "dangling": dangling, "duplicates": duplicates}
