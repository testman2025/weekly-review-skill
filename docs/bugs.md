# Bug / 问题记录

## 2026-07-21：ClawHub 评测误判为「仅支持 WorkBuddy」

### 现象

评述写「只支持特定的 workbuddy 数据库」。

### 根因

文案与默认路径过度绑定产品名；且 skill 自己读 SQLite，会被理解成绑死某存储。

### 修复（v1.1.2 → v1.2.0）

- **v1.1.2**：淡化 WorkBuddy 文案、扩大路径发现（仍不够）。
- **v1.2.0（定位修正）**：公开主路径改为 **Agent 采集 + review-input JSON**；SQLite 分析器移入 `legacy/`；文档明确「读存储是宿主 Agent 的事」。

---

## 2026-07-21：跨平台应靠 Agent 读存储，而非 skill 适配各库

### 决策

不为各平台写 DB/JSONL 适配器。Skill 只提供结构与渲染；采集由 Cursor / Claude / OpenClaw 等宿主完成。
