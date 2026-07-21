# review-input 约定

Agent 采集本平台会话事实后，填入本结构；skill 只做复盘流程与可选 Markdown 渲染。

## 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `period.start` / `period.end` | 是 | `YYYY-MM-DD` |
| `source.label` | 否 | 数据来源标签，如 `agent-collected` |
| `source.note` | 否 | 补充说明 |
| `dashboard` | 建议 | 一页看板指标（小时、credits、会话数等） |
| `projects[]` | 建议 | 分项目：`name`, `sessions`, `hours`, `credits`, `notes` |
| `problems[]` | 否 | 问题与根因（思路/记忆/流程） |
| `actions` | 否 | `done` / `observing` / `pending` |
| `open_sessions[]` | 否 | 跨周 / 跨夜待对齐 |
| `automations` | 否 | 自动化运行概览 |

完整示例见同目录 `review-input.example.json`。

## 谁负责什么

- **Agent**：用本平台能力读取会话/用量，整理成上述 JSON（或在对话中等价填齐）。
- **Skill**：规定章节与归因框架；可选 `python -m cli --input …` 渲染 Markdown。
