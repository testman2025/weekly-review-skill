---
name: weekly-review
description: >
  Agent-fed weekly retrospective locked to the six-chapter template
  (dashboard table + one-liner + optional PNG charts, theme projects,
  root-cause triage, action ledger, open sessions, automations, optional
  fact-corrections). Host Agent collects facts; this skill defines structure
  and can render Markdown. Use for weekly-review / 周度复盘 / 本周复盘.
version: 1.2.3
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

**固化底座，不固化成品。** 宿主 Agent 采集本平台事实；输出必须贴合定稿六章模板（参考用户已定稿的周度复盘 Markdown）。

## 适用 / 不适用

- **适用**：每周定期复盘；长会话对齐；标准化归因与台账。
- **不适用**：实时监控；非会话类复盘；替你写公众号成品；替 Agent 读各平台私有存储。

## 输出结构（锁定）

1. **一页看板**：`| 指标 | 数值 | 口径说明 |` + **一句话结论** + 可选「辅助图表」PNG 路径  
2. **分项目分析**：`### 2.x 主题（时长/会话）` + `| 维度 | 内容 |`（做了什么 / DB cwd / 磁盘核对 / 低效 / 提示词）；其他用简表  
3. **问题清单 + 根因三类归因** + **做得好的（正面范本）**  
4. **本周动作台账 ★**：当场已改 / 观察 / 待落实（或待落实→执行结果）  
5. **待对齐开放会话**  
6. **自动化概览**  
7. **事实更正**（可选，有核对推翻时必写）

**图表约定**：渲染器生成两张定稿样式图——横向「时间投入分布」、双栏「低效归因 + Token 趋势」（SVG）。数据来自 `charts_data`。看板主表仍是 `| 指标 | 数值 | 口径说明 |`。

## 输入

见 `schema/review-input.example.json` 与 `schema/README.md`。

## 操作流程

1. 安装本 skill。  
2. Agent 采集会话/用量，**Glob/ls 核对磁盘**后再归因。  
3. 填 `review-input`（或对话等价结构）；需要图时先出 PNG 再填 `dashboard.charts`。  
4. 按六章输出，或 `python -m cli --input review-input.json -o YYYY-MM-DD周度复盘.md`。  
5. 对开放会话当场拍板。

### CLI

```bash
cd {SKILL_DIR}
python -m cli --input schema/review-input.example.json -o 周度复盘.md
# 图表默认写到报告同目录；关闭：加 --no-charts
```

### MCP

工具 `run_weekly_review`，参数 `review_input`（对象）。
