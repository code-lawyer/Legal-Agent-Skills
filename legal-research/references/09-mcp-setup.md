# MCP 接入指南（必备前置）

本 skill 的立身之本是**可核验的法律库**：没有专业法律库 MCP，就没有真正的法律研究/检索——拿模型记忆里的法条案例充数正是最危险的幻觉源。因此**接入法律库 MCP 是硬前置**，不是可选加速器。运行时若未探测到任何法律库 MCP，`00-routing-intake.md` 的「MCP 前置门」会**先引导用户接入、暂停正式产出**（唯一例外是用户显式要求的、通篇水印的降级草稿）。级联与前置逻辑见 `10-retrieval-core.md` 与 `00-routing-intake.md`，本 skill 不写死任何具体 MCP 名称。

本文件提供一个**推荐源的现成接入方式**，帮使用者尽快接上、让 skill 正常工作。用哪家法律库由使用者决定，但**至少要接一个**。

---

## 推荐源：元典（chineselaw.com）

元典提供法条库与案例库的 HTTP MCP。本 skill 的两条检索路径分别对应：

| MCP | 用途 | 本 skill 用它做 |
|---|---|---|
| `yuandian-law` | 法条 / 司法解释检索 | 研究模式「法律框架」步、时效强制核验 |
| `yuandian-case` | 裁判文书检索 | 「司法实践」步、检索模式类案归纳 |
| `yuandian-company`（可选） | 企业信息核验 | **不在本 skill 范围**（企业核验属其他技能），列出仅供完整性参考 |

### 第一步：获取你自己的 API Token

到元典开放平台 **https://open.chineselaw.com** 注册并申请 API Token（形如 `sk-********`）。**Token 是你的密钥**，与费用/额度绑定，请妥善保管、不要提交进代码仓库或公开分享。

### 第二步：把下面这段加进你宿主 agent 的 MCP 配置

把 `<在此填入你的元典API-Token>` 替换成第一步拿到的 Token，然后写入你所用 agent 的 MCP 配置文件（Claude Code / Cursor / Cline 等的 `mcpServers` 段；具体配置文件位置见各 agent 文档）：

```json
{
  "mcpServers": {
    "yuandian-law": {
      "type": "http",
      "url": "https://open.chineselaw.com/mcp/law/stream",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer <在此填入你的元典API-Token>"
      }
    },
    "yuandian-case": {
      "type": "http",
      "url": "https://open.chineselaw.com/mcp/case/stream",
      "headers": {
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer <在此填入你的元典API-Token>"
      }
    }
  }
}
```

> 需要企业核验能力（本 skill 不用）时，可再加一段 `yuandian-company`，`url` 为 `https://open.chineselaw.com/mcp/company/stream`，headers 同上。

### 第三步：重启 / 重连 agent，让它加载新的 MCP

多数宿主 agent 需要重启或重新加载配置后才会连上新加的 MCP。之后本 skill 每次执行"检索核验"动作时会**实际探测**到 `yuandian-law` / `yuandian-case`，命中即标 `[MCP核验:元典/条号或案号/日期]`，"源名"填实际接上的 MCP 名。

---

## 安全线

- **Token 即密钥**：只填进你本机 / 你账户的 agent 配置，**绝不写入本 skill 文件、不提交仓库、不随报告输出**。
- 本文件与整个 skill **不内置任何真实 Token**，只给占位符；任何看到真实 Token 出现在 skill 文件里的情况都属泄露，应立即在元典后台轮换密钥。
- 未接 MCP 完全可用：skill 会诚实标 `[模型知识-未验证]` 并在"来源与核验"节集中披露，据此行动前请人工核实高风险命题。
