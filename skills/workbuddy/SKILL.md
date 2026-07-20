---
summary: "周度复盘 skill：读取 workbuddy.db，生成一页看板、项目分析、根因归因、动作台账、长会话对齐。"
read_when:
  - 用户要求"周度复盘"
  - 用户要求"weekly review"
  - 每周日复盘
---

# weekly-review-skill

在 WorkBuddy 中使用通用周度复盘分析器。

## 设计原则

**固化底座，不固化成品。**

- 固化：一页看板、项目分布、根因三类归因、动作台账、待对齐开放会话、自动化概览。
- 不固化：每周具体项目名、人工标注问题与改进项。

## 安装

1. 确保本仓库已安装：
   ```bash
   cd weekly-review-skill
   pip install -e .
   ```
2. 将本 `SKILL.md` 复制到 `~/.workbuddy/skills/weekly-review/SKILL.md`。

## 使用方式

### 方式一：CLI 直接生成报告

```bash
weekly-review --start {YYYY-MM-DD} --end {YYYY-MM-DD} -o 周度复盘.md
```

### 方式二：MCP server（推荐，任何 agent 可用）

在 `~/.workbuddy/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "weekly-review": {
      "command": "weekly-review-mcp"
    }
  }
}
```

然后在 WorkBuddy 连接器管理中信任该 MCP。

### 方式三：对话中调用

当用户说"做本周复盘"时，执行：

```bash
weekly-review --start {本周一} --end {本周日} -o {项目复盘目录}/周度复盘/YYYY-MM-DD周度复盘.md
```

并向用户展示关键数据，然后用 `AskUserQuestion` 让用户拍板跨周/跨夜会话处置。

## 输出章节

1. 一页看板
2. 分项目分析
3. 问题清单 + 根因三类归因（思路/记忆/流程）
4. 本周动作台账（当场已改 / 待观察 / 待落实）
5. 待对齐开放会话
6. 自动化运行概览

## 注意事项

- 统计周期默认上周一 00:00 ~ 上周日 23:59（UTC）。
- 默认数据库路径 `~/.workbuddy/workbuddy.db`，可通过 `--db-path` 覆盖。
- 跨周会话阈值 48h，跨夜 idle 阈值次日 06:00。
- 长会话处置必须先读会话内容/标题推断用途，不能只看时长。
- 归因禁止一刀切"收敛到单一工作区"，必须区分思路/记忆/流程三类根因。
