# review-input 约定

对齐定稿模板：`# YYYY-MM-DD 周度复盘（weekly-review skill · 六章结构）`。

Agent 采集事实后填本结构；skill 只渲染结构。**图表**用 `dashboard.charts` 引用已生成的 PNG 路径（辅助图表），不以 Mermaid 为主。

## 图表

渲染时默认在报告同目录生成两张 **SVG**（标准库、无 pip）：

- `chart-时间分布-YYYY-MM-DD.svg`
- `chart-归因Token-YYYY-MM-DD.svg`

报告看板用 Markdown 图片语法嵌入：`![title](path)`。  
也可用 `--charts-dir` 指定目录，或 `--no-charts` 关闭。

Agent 若已用 ImageGen/其他工具产出 PNG，可直接填 `dashboard.charts` 路径，CLI 不会覆盖已有 charts（除非重新生成）。


| 字段 | 说明 |
|------|------|
| `period` | `start` / `end`（必填） |
| `meta` | `title` / `methodology` / `version_note` / `task_split` |
| `source.note` | 数据来源一行说明 |
| `dashboard.metrics[]` | `{name,value,note}` 看板表 |
| `dashboard.summary` | 一句话结论 |
| `dashboard.charts[]` | 辅助图 PNG 相对路径 |
| `projects[]` | `{title, dimensions{做了什么,…}}` 主题分节 |
| `other_projects[]` | `{name,hours,note}` |
| `problems[]` / `positives[]` | 问题表 + 正面范本 |
| `actions` | `done` / `observing` / `pending` |
| `open_sessions[]` | 待对齐会话 |
| `automations.narrative` | 自动化概览（条目列表或长文） |
| `corrections*` | 可选第七章事实更正 |

完整示例：`review-input.example.json`。
