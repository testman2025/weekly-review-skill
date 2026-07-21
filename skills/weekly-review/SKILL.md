---
name: weekly-review
description: >
  Agent-fed weekly retrospective: the host Agent collects session facts from
  its own platform; this skill defines the review structure (dashboard,
  per-project, root-cause triage, action ledger, open sessions) and can render
  Markdown from a standard review-input JSON. Use for weekly-review /
  周度复盘 / 本周复盘 / 一周总结.
version: 1.2.0
category: 办公效率
read_when:
  - 用户说"做周度复盘 / 本周复盘 / 跑一下 weekly review"
  - 用户想清理或对齐跨周、跨夜还开着的会话
  - 用户希望把复盘流程标准化、沉淀成可复用模板
  - 每周固定时间（如周日）触发复盘
metadata:
  openclaw:
    requires:
      bins:
        - python
    emoji: "📊"
    homepage: https://github.com/testman2025/weekly-review-skill
    os:
      - macos
      - linux
      - windows
---

# weekly-review（周度复盘 skill）

跨平台周度复盘底座：**各平台 Agent 负责读本机会话/用量并整理事实**；本 skill 负责「复盘看什么、怎么归因、怎么落台账」，以及可选的 Markdown 渲染。

## 适用场景

- **每周定期复盘**，需要客观数据（活跃时长、会话数、用量、跨周/跨夜会话）支撑。
- **会话 / 工作区越开越多**，需要清理或对齐仍处于 idle 的长会话。
- **复盘流程标准化**：把「该看什么、怎么归因」沉淀为可复用模板。

## 不适用场景

- **实时会话监控 / 告警**：离线周度分析，不常驻推送。
- **非会话类复盘**：代码审查质量、财务报表等不在范围内。
- **替你写公众号/周报成品**：只产出结构化底座，正文由你写。
- **替 Agent 读各平台私有存储**：本 skill **不**内置各产品数据库适配器；采集由宿主 Agent 完成。

## 设计原则

**固化底座，不固化成品；Agent 采数，Skill 定结构。**

| 职责 | 谁做 |
|------|------|
| 读本平台会话 / 用量 / 历史 | **宿主 Agent**（用自己的工具与权限） |
| 章节结构、根因三类、动作台账 | **本 skill** |
| 把标准 JSON 打成 Markdown | **本 skill**（可选 CLI / MCP） |

## 输入

标准事实包 `review-input`（对话中填齐亦可），字段见 `schema/README.md` 与 `schema/review-input.example.json`：

- `period`：起止日期（必填）
- `dashboard`：看板指标
- `projects[]`：分项目
- `problems[]` / `actions`：问题与动作台账（常需人工补）
- `open_sessions[]`：待对齐开放会话
- `automations`：可选

## 输出

固定六章 Markdown：一页看板、分项目分析、问题+根因三类归因、动作台账、待对齐开放会话、自动化概览。

## 其他约束

- 归因三类：思路 / 记忆 / 流程；禁止一刀切「收敛到单一工作区」。
- 长会话须先读内容/标题再处置，不能只看时长。
- 跨周阈值建议 >48h；跨夜 idle 建议次日 06:00 后仍活跃/未关。
- 可选渲染器仅依赖 Python ≥ 3.10 标准库；无网络、无密钥。

## 如何使用 / 操作流程

1. **安装**本 skill 到所用 Agent 的 skills 目录（或 ClawHub：`openclaw skills install weekly-review`）。
2. **Agent 采集**：用本平台能力汇总本周会话、用量、项目分布、长会话/跨夜列表（不要假设统一 SQLite）。
3. **填结构**：写入 `review-input` JSON，或在对话中按同名字段组织；问题与改进建议与用户对齐后写入 `problems` / `actions`。
4. **出报告**（二选一）：
   - 对话中直接按六章输出 Markdown；或
   - `python -m cli --input review-input.json -o 周度复盘.md`
5. **拍板**：对 `open_sessions` 逐条确认关闭 / 续作 / 归档。

### CLI 渲染（可选）

```bash
cd {SKILL_DIR}
python -m cli --input schema/review-input.example.json -o 周度复盘.md
```

### MCP（可选）

工具 `run_weekly_review`，参数 `review_input`（对象）。**不接受 db_path**；采集由 Agent 完成后再调用。

```json
{
  "mcpServers": {
    "weekly-review": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": { "PYTHONPATH": "{SKILL_DIR}" }
    }
  }
}
```
