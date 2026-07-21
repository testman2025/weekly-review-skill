# weekly-review-skill (Weekly Review Skill)

![版本](https://img.shields.io/badge/version-1.2.2-blue)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![许可证](https://img.shields.io/badge/license-MIT-green)

一句话简介：跨平台周度复盘 skill——**Agent 采集本平台数据，Skill 固化复盘结构与可选渲染**。

---

## 目录

- [项目介绍](#项目介绍)
- [功能特性](#功能特性)
- [快速上手](#快速上手)
- [使用说明](#使用说明)
- [发布到 ClawHub](#发布到-clawhub)
- [许可证](#许可证)

---

## 项目介绍

**为什么做？** 周度复盘缺统一结构；各平台会话存储格式各异，不应由 skill 去猜。

**做什么？** 宿主 Agent 用自己的能力读本机会话/用量，整理成 `review-input`；本 skill 规定六章复盘与根因框架，并可把 JSON 渲染成 Markdown。

---

## 功能特性

- Agent 采数 + Skill 定结构（真正跨平台）
- 标准 `review-input` JSON（`skills/weekly-review/schema/`）
- CLI / MCP 可选渲染（Python ≥ 3.10，仅标准库）
- ClawHub 可发布，slug：`weekly-review`

---

## 快速上手

```bash
git clone https://github.com/testman2025/weekly-review-skill.git
cd weekly-review-skill/skills/weekly-review
python -m cli --input schema/review-input.example.json -o weekly-report.md
```

或从 ClawHub：`openclaw skills install weekly-review`

---

## 使用说明

1. Agent 汇总本周会话事实 → 填入 `review-input`
2. 对话按六章输出，或 CLI：`python -m cli -i review-input.json -o 周度复盘.md`
3. 对开放会话当场拍板

字段说明见 [`skills/weekly-review/schema/README.md`](skills/weekly-review/schema/README.md)。

旧版「直接读 SQLite」代码已移至 `skills/weekly-review/legacy/`，**非公开主路径**。

---

## 发布到 ClawHub

```bash
clawhub login
clawhub skill publish ./skills/weekly-review \
  --slug weekly-review \
  --name "Weekly Review" \
  --version 1.2.2 \
  --changelog "Agent-fed review: host Agent collects facts; skill renders structure."
```

---

## 许可证

- 本仓库：MIT
- ClawHub 分发：MIT-0
