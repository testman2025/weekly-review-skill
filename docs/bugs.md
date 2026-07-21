# Bug / 问题记录

## 2026-07-21：ClawHub 评测误判为「仅支持 WorkBuddy」

### 现象

ClawHub / SkillSpector 综合评述写到：「只支持特定的 workbuddy 数据库」「对于使用 workbuddy 的用户……」，与产品定位不符。

### 根因

介绍与代码文案过度绑定 `workbuddy.db`（CLI help、MCP tool description、报告数据来源、默认路径探测命名），导致评审模型把「默认发现路径之一」理解成「唯一支持的产品」。

实际上：

- **运行时**：任意可安装 Skill / MCP 的 Agent 都可用；
- **数据源**：任意含兼容 `sessions` 表的本地 SQLite；WorkBuddy 只是自动发现候选之一。

### 修复（v1.1.2）

- 重写 `SKILL.md` / README 描述：明确 agent-agnostic、非 WorkBuddy 专用。
- CLI / MCP / 报告文案改为「本地 AI 会话库」。
- `discover_db_path` 支持 `WEEKLY_REVIEW_DB`，并探测多种常见路径。
- `session_usage` / `automations` / `automation_runs` 表缺失时跳过，不强制整库 schema。
- 报告中展示真实 `db_path`。

### 验证

- 本地用任意路径 `--db-path` 指向兼容库可生成报告。
- 重新发布 ClawHub `weekly-review@1.1.2` 后，评述应不再写死 WorkBuddy-only。
