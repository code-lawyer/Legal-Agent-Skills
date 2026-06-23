---
name: legal-research
description: 法律研究与案例检索。当用户要求做法律研究/出研究报告/论证某法律问题/某争议点法律依据时使用；当用户要求检索类案/出案例检索报告/查某类纠纷裁判规则/裁判倾向/同案同判时使用；当用户要把案例/法条录入到库、或把 Word 判决转入库时使用。
---

# 法律研究与案例检索

## 文件定位（先读）
本 skill 由多个文件组成。下文所有 `references/…`、`corpus/…` 路径均**相对于本 SKILL.md 所在目录**。开始前先确定该目录（你被指向或读取本文件时所在的位置），之后所有读取都基于它解析，不要用当前工作目录去找。

## 何时使用
- **研究类**：做法律研究、出研究报告、论证某法律问题、查某争议点法律依据。
- **检索类**：检索类案、出案例检索报告、查某类纠纷裁判规则/裁判倾向/同案同判。
- **库维护类**：把案例/法条录入库、把 Word 判决转入库、更新本地语料库。

## 任务边界
本技能只做**法律研究报告 + 案例检索报告 + 本地语料库维护**。不做以下事项：
- 合同审查 → 请使用 `contract-review`
- 合同起草、企业核验、尽调合规、续约提醒、流程图

## 执行顺序（按需读取，不一次读全）
1. 先读 `references/00-workflow.md` — 判定模式（研究/检索/复合/库维护）并路由。
2. 按命中模式按需读对应分支文件，不预加载全部 reference。
3. 库维护模式直接走 `references/08-library-maintenance.md`，不经过研究/检索分析链。

## 按需读取索引
- `references/00-workflow.md` — 主流程 + 四模式路由 + 数据流骨架
- `references/01-intake-scoping.md` — 建档：法律问题界定 / 事实模式提取
- `references/02-retrieval.md` — 公共检索核验层（本地库优先→MCP→回退）+ 三轮检索 + 注入防御
- `references/03-research-mode.md` — 研究模式论证骨架（法框→学说→司法实践→结论）
- `references/04-case-mode.md` — 检索模式类案归纳（检索式构造→筛选→裁判规则→倾向统计）
- `references/05-output-research.md` — 法律研究报告结构模板
- `references/06-output-case.md` — 案例检索报告结构模板
- `references/07-citation-currency.md` — 公共引证规范 + 时效强制核验 + 来源标签
- `references/08-library-maintenance.md` — 库维护流水线：makeitdown 转换→法律结构化→索引写入
