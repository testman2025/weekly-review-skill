# weekly-review-skill (Weekly Review Skill)

![版本](https://img.shields.io/badge/version-1.1.2-blue)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![许可证](https://img.shields.io/badge/license-MIT-green)

一句话简介：与具体 Agent 无关的周度复盘 skill——固化复盘底座，不固化每周成品；支持 CLI / MCP / Agent SKILL，数据源为兼容的本地 SQLite（非 WorkBuddy 专用）。

---

## 📖 目录 (Table of Contents)

- [项目介绍](#-项目介绍)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [快速上手](#-快速上手)
- [安装与配置](#-安装与配置)
- [使用说明](#-使用说明)
- [发布到 ClawHub](#-发布到-clawhub)
- [许可证](#-许可证)

---

## 📝 项目介绍 (Description)

**为什么做这个项目？**
> 周度复盘容易拍脑袋：缺客观会话数据、缺统一归因框架、每周重写格式。需要一套可复用的复盘底座。

**它做了什么？**
> 可安装到任意支持 Skill / MCP 的 Agent。只读**兼容 schema** 的本地 AI 会话库（SQLite，`--db-path` / `WEEKLY_REVIEW_DB` 指定；WorkBuddy 仅为自动发现候选之一），产出一页看板、分项目分析、根因三类归因、动作台账、待对齐开放会话与自动化概览。每周具体项目名与人工改进项由使用者通过 `--notes` 或对话补充。

---

## ✨ 功能特性 (Features)

- ✅ CLI：生成 Markdown 复盘报告或原始 JSON
- ✅ MCP server：stdio JSON-RPC 暴露 `run_weekly_review`
- ✅ Agent SKILL：安装后可对话触发「周度复盘 / weekly-review」
- ✅ 零第三方依赖，仅 Python 标准库；无网络请求、只读数据库
- ✅ Agent 无关：OpenClaw / Cursor / Claude Code 等均可安装使用
- ✅ 数据源无关：任意兼容 `sessions` 表的本地 SQLite（非 WorkBuddy 专用）
- ✅ 可发布到 ClawHub（个人号），slug：`weekly-review`

---

## 🛠 技术栈 (Tech Stack)

- **语言**: Python ≥ 3.10（标准库：`sqlite3` / `json` / `argparse` / `datetime` / `pathlib`）
- **形态**: Agent Skill（`SKILL.md`）+ CLI + MCP
- **分发**: GitHub 源码仓库 + ClawHub skill 注册表

---

## 🚀 快速上手 (Getting Started)

### 前置依赖 (Prerequisites)

- Python ≥ 3.10
- （可选）本机 AI 会话库 SQLite（兼容 `sessions` 表；可用 `--db-path` 或 `WEEKLY_REVIEW_DB` 指定）

### 从 ClawHub 安装

```bash
openclaw skills install weekly-review
# 或
clawhub install weekly-review
```

### 从源码安装

```bash
git clone https://github.com/testman2025/weekly-review-skill.git
cd weekly-review-skill
cd skills/weekly-review
python -m cli --help
```

---

## 📦 安装与配置 (Installation)

本 skill **自包含**于 `skills/weekly-review/`：将整个目录放入 agent 的 skills 路径即可，**无需 `pip install`**。

MCP 配置示例：

```json
{
  "mcpServers": {
    "weekly-review": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": { "PYTHONPATH": "/path/to/skills/weekly-review" }
    }
  }
}
```

---

## 📘 使用说明 (Usage)

### CLI

```bash
cd skills/weekly-review

# 默认生成上周报告
python -m cli -o weekly-report.md

# 指定周期并附加人工标注
python -m cli --start 2026-07-13 --end 2026-07-19 --notes notes.json -o report.md
```

`notes.json` 示例见 `examples/notes-example.json`。

### 作为 Agent Skill

复制 `skills/weekly-review/` 到所用 agent 的 skills 目录（例如 `~/.agents/skills/weekly-review/`），对话触发「做本周复盘」即可。

### 报告章节

1. 一页看板（wall-clock、真实活跃时长、Credit 消耗、会话数、跨周/跨夜会话）
2. 分项目分析（按 cwd 自动聚合）
3. 问题清单 + 根因三类归因（思路/记忆/流程）
4. 本周动作台账（当场已改 / 待观察 / 待落实）
5. 待对齐开放会话（>48h 跨周、跨夜 idle）
6. 自动化运行概览

---

## 🚢 发布到 ClawHub

发布单位是 **`skills/weekly-review/`**（含 `SKILL.md`），以**个人号**发布，不传 `--owner`。

```bash
# 安装 CLI（任选其一）
npm i -g clawhub

# 登录个人 GitHub 账号
clawhub login
clawhub whoami

# 预检
clawhub skill publish ./skills/weekly-review \
  --slug weekly-review \
  --name "Weekly Review" \
  --version 1.1.2 \
  --changelog "Clarify agent-agnostic + any compatible session DB (not WorkBuddy-only)." \
  --dry-run

# 正式发布（确认 dry-run 无误后）
clawhub skill publish ./skills/weekly-review \
  --slug weekly-review \
  --name "Weekly Review" \
  --version 1.1.2 \
  --changelog "Clarify agent-agnostic + any compatible session DB (not WorkBuddy-only)."
```



新版本可能需通过 ClawHub 安全扫描后才会出现在公开安装列表。

---

## 📄 许可证 (License)

- 本仓库源码：MIT
- 经 ClawHub 发布的 skill：按平台统一条款（MIT-0）分发
