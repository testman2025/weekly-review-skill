---
name: weekly-review
description: >
  Agent-agnostic weekly retrospective from any compatible local AI session
  SQLite DB (not tied to WorkBuddy or a single product): dashboard, per-project
  breakdown, root-cause triage, action ledger, open sessions. Installable on
  OpenClaw / Cursor / Claude Code / any MCP-capable agent. Use for weekly-review
  / 周度复盘 / 本周复盘 / 一周总结.
version: 1.1.2
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

一个**与具体 Agent 产品无关**的周度复盘 skill。可安装到 OpenClaw、Cursor、Claude Code，或任何支持 Agent Skill / MCP 的运行时。它把「复盘该看什么、怎么归因、怎么落台账」固化成可复用底座；每周具体项目、人工改进项由使用者或运行时输入。

**不是 WorkBuddy 专用。** WorkBuddy 会话库只是自动发现路径之一；你可以用 `--db-path` / 环境变量 `WEEKLY_REVIEW_DB` 指向任意兼容 schema 的本地 SQLite。

## 适用场景

- **每周定期复盘**，想要客观数据（真实活跃时长、会话数、Credit 消耗、跨周/跨夜会话）支撑，而不是拍脑袋。
- **会话 / 工作区越开越多**，需要清理或对齐跨周、跨夜仍处于 idle 的长会话。
- **复盘流程标准化**：团队或个人想把"复盘该看什么、怎么归因"沉淀为可复用模板，减少每次从头设计。

## 不适用场景

- **实时会话监控 / 告警**：本 skill 是离线周度分析，不常驻、不主动推送。
- **非会话类数据复盘**：如代码审查质量、财务报表、用户行为分析——它只吃「会话 / 工作记录」数据。
- **替你写公众号文章或周报正文**：本 skill 只产出结构化复盘底座，成品内容由你写。
- **深度主观根因挖掘**：只提供「思路 / 记忆 / 流程」三类归因框架，最终结论要你拍板。
- **任意专有二进制格式的会话导出**：需要先落到兼容的 SQLite（见下方「数据源约定」），或由 agent 自行整理后走 `--notes`。

## 设计原则

**固化底座，不固化成品。**

- 固化：一页看板、项目分布、根因三类归因、动作台账、待对齐开放会话、自动化概览。
- 不固化：每周具体项目名、人工标注问题与改进项（由 `--notes` 传入或对话中补充）。

## 安装

本 skill **自包含**：运行代码（各 `.py` 模块）已随本目录一起提供，仅依赖 Python 标准库，**无需 `pip install`、无需额外下载**。运行环境需 Python ≥ 3.10。只读本地 SQLite 会话库，无网络请求、无密钥环境变量。

可安装到**任意**支持 Skill / MCP 的 Agent（不限某一厂商）。

### 从 ClawHub 安装（推荐）

```bash
openclaw skills install weekly-review
# 或
clawhub install weekly-review
```

安装后将所用 agent 指向已安装的 skill 目录即可。

### 手动安装

1. 将本 `weekly-review/` 目录（含 `SKILL.md` 与 `cli.py` / `mcp_server.py` / `analyzer.py` / `report.py` / `utils.py`）整体放入所用 agent 的 skills 目录，目录名保持 `weekly-review`。
2. 确保运行环境有 Python ≥ 3.10。
3. （可选）设置 `WEEKLY_REVIEW_DB` 指向你的会话库，或运行时传 `--db-path`。

## 使用方式

设 skill 目录为 `{SKILL_DIR}`（即放置本 `SKILL.md` 的 `weekly-review/` 目录）。

### 方式一：CLI 直接生成报告

在 skill 目录下执行：

```bash
cd {SKILL_DIR}
python -m cli --start {YYYY-MM-DD} --end {YYYY-MM-DD} -o 周度复盘.md
```

若需在其他目录调用，用 `PYTHONPATH` 指定 skill 目录：

```bash
PYTHONPATH={SKILL_DIR} python -m cli --start {YYYY-MM-DD} --end {YYYY-MM-DD} -o 周度复盘.md
```

### 方式二：MCP server

在你的 agent 的 MCP 配置文件中添加（`PYTHONPATH` 指向 skill 目录）：

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

然后在连接器 / MCP 管理中信任该 server 即可。

### 方式三：对话中调用

当用户说"做本周复盘"时，执行：

```bash
PYTHONPATH={SKILL_DIR} python -m cli --start {本周一} --end {本周日} -o {项目复盘目录}/周度复盘/YYYY-MM-DD周度复盘.md
```

并向用户展示关键数据，然后用 `AskUserQuestion` 让用户拍板跨周 / 跨夜会话处置。

> 注：若你是从 GitHub 仓库 `testman2025/weekly-review-skill` 安装，进入 `skills/weekly-review/` 后执行 `python -m cli` 即可，无需 `pip install`；本 SKILL.md 以"随 skill 自带、开箱即用"为默认路径。

## 输出章节

1. 一页看板
2. 分项目分析
3. 问题清单 + 根因三类归因（思路 / 记忆 / 流程）
4. 本周动作台账（当场已改 / 待观察 / 待落实）
5. 待对齐开放会话
6. 自动化运行概览

## 输入

| 输入 | 说明 | 必填 |
|------|------|------|
| `--db-path` | 本地 AI 会话库（SQLite）路径 | 否 |
| `WEEKLY_REVIEW_DB` | 环境变量形式的会话库路径（与 `--db-path` 二选一即可） | 否 |
| `--start` / `--end` | 统计周期（`YYYY-MM-DD`）；默认上周一～上周日（UTC） | 否 |
| `--notes` | 人工标注的问题/动作台账 JSON（根因与改进建议由你填写） | 否 |
| `--output` / `-o` | Markdown 报告输出路径 | 否 |
| `--json` | 输出原始 JSON 而非 Markdown | 否 |

未指定路径时，会自动探测多种常见位置（含但不限于 WorkBuddy、OpenClaw、Cursor、通用 `sessions.db`）。

## 数据源约定（Agent 无关）

**必需表 `sessions`**（字段名兼容下列列即可）：

- `id`, `cwd`, `title`, `custom_title`, `status`
- `created_at`, `updated_at`, `last_activity_at`（毫秒或秒时间戳）
- `model`, `source_mode`, `is_background_automation`

**可选表**（不存在则跳过对应指标，不报错）：

- `session_usage`：`session_id`, `used`, `size`, `credit_json`
- `automations` / `automation_runs`：自动化定义与运行记录

任何 Agent / 工具只要把会话导出或同步成上述 SQLite，即可复盘；不必使用 WorkBuddy。

## 输出

Markdown（或 JSON）结构化周度复盘报告，固定包含：一页看板、分项目分析、根因三类归因、动作台账、待对齐开放会话、自动化运行概览。

## 其他约束

- 只读本地 SQLite；不写库、不发起网络请求、不依赖第三方 pip 包。
- **运行时与数据源均不绑定单一 Agent 产品**；WorkBuddy 仅为可选自动发现路径之一。
- 报告中的根因分析与改进建议需你通过 `--notes` 或对话补充；工具负责客观数据与格式底座。
- 在 ClawHub 上发布的 skill 按平台统一许可（MIT-0）分发；本仓库源码许可证见根目录 `README.md`。
- 长会话处置必须先读会话内容 / 标题推断用途，不能只看时长。
- 归因禁止一刀切「收敛到单一工作区」，必须区分思路 / 记忆 / 流程三类根因。
- 跨周会话阈值 48h；跨夜 idle 阈值次日 06:00。

## 操作流程

1. 将本 skill 安装到所用 Agent（ClawHub 或手动复制目录）。
2. 确认本机有 Python ≥ 3.10，以及可读的兼容会话库（`--db-path` / `WEEKLY_REVIEW_DB` / 自动发现）。
3. 用 CLI / MCP / 对话触发，指定周期（或使用默认上周）。
4. 审阅报告中的看板与开放会话，用人工 notes 补齐问题与动作台账。
5. 对跨周 / 跨夜会话做处置决策（关闭 / 续作 / 归档），并记下待落实项。
