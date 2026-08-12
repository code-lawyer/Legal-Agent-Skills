# 安全策略

## 报告漏洞

如发现安全问题（尤其是可能导致密钥泄露、注入或数据外泄的问题），请**私下**通过
GitHub Security Advisories（仓库 Security → Report a vulnerability）报告，或联系
维护者，不要先公开 issue。我们会在确认后尽快修复并致谢。

## API Token 处理（重要）

法律库 MCP（如元典）的 API Token **即密钥**：

- 只填进你本机 / 你账户的宿主 agent 配置（`mcpServers`），**绝不**写入 skill 文件、
  提交仓库或随报告输出。
- 本仓库不内置任何真实 Token，只给占位符。
- 若不慎提交了 Token，请立即在服务方吊销并重新签发，然后清理 git 历史。

## 处理不受信任的输入

- 红线脚本 `redline_docx.py` 只**渲染**修订计划，不执行计划中的任意代码；计划先经
  `validate_plan()` 预检。
- 检索/核验层含注入防御（见 `contract-review/references/07-verification.md` 与
  `legal-research/references/10-retrieval-core.md`）：把检索返回内容当**数据**而非
  指令，不执行其中的“指示”。

## 输出的法律免责

标注 `[模型知识-未验证]` 的命题不得作为诉讼或法律交付物的唯一依据；正式交付须经
执业律师复核。详见各 skill 的引证与免责章节。
