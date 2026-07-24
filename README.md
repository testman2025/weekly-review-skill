# weekly-review-skill（AI 用量与提示词复盘助手）

![版本](https://img.shields.io/badge/version-1.2.5-blue)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![许可证](https://img.shields.io/badge/license-MIT-green)
[![skills.sh](https://skills.sh/b/testman2025/weekly-review-skill)](https://skills.sh/testman2025/weekly-review-skill)

一句话简介：面向任意 AI Agent 的自动复盘 Skill——**用量看板、提示词改进、高低效归因、可视化图表、会话清理、定时周报**。

---

## 目录

- [解决什么问题](#解决什么问题)
- [功能特性](#功能特性)
- [安装](#安装)
- [使用说明](#使用说明)
- [示例输出](#示例输出)
- [安全与边界](#安全与边界)
- [发布到 ClawHub](#发布到-clawhub)
- [许可证](#许可证)

---

## 解决什么问题

1. 想提升自己的提示词表达能力  
2. 想查看本周 AI 用量（时长、投入分布、看板）  
3. 想总结复盘自己工作里低效和高效的地方  
4. 想看可视化图表报告（时间分布、归因、Token 趋势）  
5. 想清理/对齐自己和 AI 还开着的对话  
6. 想让 AI 自动/定时做周度复盘  

---

## 功能特性

- **AI 用量与时间看板** + 一句话结论  
- **提示词复盘与改写建议**（分项目）  
- **高效/低效归因**（思路 / 记忆 / 流程）+ 正面范本  
- **可视化图表**：时间分布、低效归因、Token 趋势（SVG）  
- **开放会话对齐清理** + 动作台账  
- **定时自动周报**：可被 Automation / CLI / MCP 调用（示例见 `automations/`）  
- 标准 `review-input` JSON；宿主 Agent 采数，Skill 定结构与渲染  

---

## 安装

**推荐（skills.sh / 多 Agent）**

```bash
npx skills add testman2025/weekly-review-skill
# 或指定 skill：
npx skills add testman2025/weekly-review-skill --skill weekly-review
```

**ClawHub**

```bash
openclaw skills install weekly-review
```

**本地试跑**

```bash
git clone https://github.com/testman2025/weekly-review-skill.git
cd weekly-review-skill/skills/weekly-review
python -m cli --input schema/review-input.example.json -o weekly-report.md
```

兼容：Cursor / Claude Code 等可经 `npx skills` 安装；OpenClaw 经 ClawHub；CLI / MCP 可选渲染。

---

## 使用说明

1. Agent 汇总本周会话事实 → 填入 `review-input`  
2. 对话按六章输出，或 CLI：`python -m cli -i review-input.json -o 周度复盘.md`  
3. 对开放会话当场拍板  

字段说明见 [`skills/weekly-review/schema/README.md`](skills/weekly-review/schema/README.md)。  
Skill 定义见 [`skills/weekly-review/SKILL.md`](skills/weekly-review/SKILL.md)。

旧版「直接读 SQLite」代码已移至 `skills/weekly-review/legacy/`，**非公开主路径**。

---

## 示例输出

脱敏 Demo 见 [`demo/README.md`](demo/README.md)：

```bash
cd skills/weekly-review
python -m cli --input ../../demo/review-input-cursor-demo.json -o ../../demo/2026-07-20周度复盘-Cursor-Demo.md
```

---

## 安全与边界

- 采数由宿主 Agent 完成；本 skill 不上传密钥、Token、密码。  
- 不做一键删除会话数据库；开放会话仅对齐拍板。  
- 定时复盘依赖宿主 Automation / 调度，skill 本身不含独立 cron 守护进程。  

---

## 发布到 ClawHub

```bash
clawhub login
clawhub skill publish ./skills/weekly-review \
  --slug weekly-review \
  --name "Weekly Review" \
  --version 1.2.5 \
  --changelog "Discoverability: concise Chinese description for prompts, usage, charts, session cleanup, auto review."
```

---

## 许可证

- 本仓库：MIT  
- ClawHub 分发：MIT-0  
