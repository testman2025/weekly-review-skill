"""Markdown 报告生成器：只吃 Agent 整理好的 review-input dict.

报告章节（固化底座）：
1. 一页看板
2. 分项目分析
3. 问题清单 + 根因三类归因
4. 本周动作台账
5. 待对齐开放会话
6. 自动化运行概览
"""

from __future__ import annotations

from typing import Any

from utils import fmt_hours, safe_div, truncate


class ReportBuilder:
    """从标准 review-input JSON 渲染 Markdown."""

    def __init__(self, data: dict[str, Any]):
        self.data = data or {}

    def build(self) -> str:
        period = self.data.get("period") or {}
        start_str = period.get("start") or "—"
        end_str = period.get("end") or "—"
        source = self.data.get("source") or {}
        source_label = source.get("label") or "agent-collected"
        source_note = source.get("note") or "由 Agent 从本平台采集并整理"

        lines: list[str] = [
            f"# {start_str} ~ {end_str} 周度复盘\n",
            (
                f"> **统计周期**：{start_str}（周一）～ {end_str}（周日）\n"
                f"> **数据来源**：{source_label} — {source_note}\n\n"
            ),
        ]
        lines.extend(self._section_dashboard())
        lines.extend(self._section_projects())
        lines.extend(self._section_problems(self.data.get("problems") or []))
        lines.extend(self._section_action_log(self.data.get("actions") or {}))
        lines.extend(self._section_open_sessions())
        lines.extend(self._section_automations())
        return "\n".join(lines)

    def _section_dashboard(self) -> list[str]:
        d = self.data.get("dashboard") or {}
        wall = float(d.get("wall_clock_hours") or 0)
        active = float(d.get("active_hours") or 0)
        credits = float(d.get("credits") or 0)
        sessions = int(d.get("session_count") or 0)
        avg = d.get("avg_session_hours")
        if avg is None:
            avg = safe_div(active, sessions)
        else:
            avg = float(avg)
        long_n = int(d.get("long_session_count") or 0)
        overnight_n = int(d.get("overnight_idle_count") or 0)

        out = [
            "## 一、一页看板\n",
            "| 指标 | 数值 | 说明 |",
            "|---|---|---|",
            f"| 原始 wall-clock 时长 | **{fmt_hours(wall)}** | Agent 汇总的跨度 |",
            f"| **真实活跃时长** | **{fmt_hours(active)}** | Agent 估算的活跃时间 |",
            f"| Credit / 用量 | **{credits:.2f}** | Agent 汇总的消耗 |",
            f"| 会话数 | {sessions} 个 | 周期内相关会话 |",
            f"| 平均每会话 | {fmt_hours(float(avg))} | 活跃时长 / 会话数 |",
            f"| 跨周长会话 | {long_n} 个 | 通常 > 48h |",
            f"| 跨夜 idle 会话 | {overnight_n} 个 | 跨夜仍 idle |",
            "",
        ]
        top_models = d.get("top_models") or []
        if top_models:
            parts = []
            for m in top_models:
                if isinstance(m, dict):
                    parts.append(f"{m.get('name', '?')}({m.get('count', 0)})")
                elif isinstance(m, (list, tuple)) and len(m) >= 2:
                    parts.append(f"{m[0]}({m[1]})")
            if parts:
                out.append("**常用模型**：" + " / ".join(parts))
                out.append("")
        return out

    def _section_projects(self) -> list[str]:
        out = ["## 二、分项目分析\n"]
        projects = self.data.get("projects") or []
        if not projects:
            out.append("本周无项目数据（可由 Agent 按工作区/仓库聚合后填入）。\n")
            return out

        out.append("| 项目 | 会话数 | 活跃时长 | Credit | 备注 |")
        out.append("|---|---|---|---|---|")
        for p in projects[:20]:
            name = p.get("name") or "—"
            sessions = p.get("sessions", "—")
            hours = float(p.get("hours") or 0)
            credits = p.get("credits")
            credits_s = f"{float(credits):.2f}" if credits not in (None, "") else "—"
            notes = p.get("notes") or "—"
            out.append(
                f"| {name} | {sessions} | {fmt_hours(hours)} | {credits_s} | {notes} |"
            )
        out.append("")
        return out

    def _section_problems(self, problems: list[dict[str, Any]]) -> list[str]:
        out = [
            "## 三、问题清单 + 根因归因\n",
            (
                "> 归因三类框架：① 思路问题（边做边开新目录，没规划）；"
                "② 记忆问题（忘了之前做过）；③ 流程问题（合理分工但缺索引/引用）。"
                "三者对应完全不同的建议，禁止一刀切。\n"
            ),
            "| # | 问题 | 归因类别 | 根因 | 建议 |",
            "|---|---|---|---|---|",
        ]
        if not problems:
            out.append("| — | 暂无人工标注问题 | — | — | 请在对话中补充 |")
        for i, p in enumerate(problems, 1):
            out.append(
                f"| {i} | {p.get('description', '—')} | {p.get('category', '—')} "
                f"| {p.get('root_cause', '—')} | {p.get('suggestion', '—')} |"
            )
        out.append("")
        return out

    def _section_action_log(self, actions: dict[str, Any]) -> list[str]:
        out = ["## 四、本周动作台账\n"]

        out.append("### 4.1 当场已改\n")
        done = actions.get("done") or []
        if not done:
            out.append("暂无。\n")
        else:
            out.append("| # | 动作 | 触发来源 | 改了什么 |")
            out.append("|---|---|---|---|")
            for i, a in enumerate(done, 1):
                out.append(
                    f"| A{i} | {a.get('action', '—')} | {a.get('trigger', '—')} "
                    f"| {a.get('change', '—')} |"
                )
            out.append("")

        out.append("### 4.2 已改、需后续观察效果\n")
        observing = actions.get("observing") or []
        if not observing:
            out.append("暂无。\n")
        else:
            out.append("| # | 动作 | 怎么判断见效了 |")
            out.append("|---|---|---|")
            for i, a in enumerate(observing, 1):
                out.append(
                    f"| O{i} | {a.get('action', '—')} | {a.get('criteria', '—')} |"
                )
            out.append("")

        out.append("### 4.3 待落实\n")
        pending = actions.get("pending") or []
        if not pending:
            out.append("暂无。\n")
        else:
            out.append("| # | 建议 | 优先级 | 截止 | 状态 |")
            out.append("|---|---|---|---|---|")
            for i, a in enumerate(pending, 1):
                out.append(
                    f"| P{i} | {a.get('suggestion', '—')} | {a.get('priority', '—')} "
                    f"| {a.get('deadline', '—')} | {a.get('status', '待开始')} |"
                )
            out.append("")

        return out

    def _section_open_sessions(self) -> list[str]:
        out = ["## 五、待对齐开放会话\n"]
        sessions = self.data.get("open_sessions") or []
        if not sessions:
            out.append("本周无跨周或跨夜 idle 会话。\n")
            return out

        out.append(
            "> 机制：每周复盘交付时列出跨周(>48h)/跨夜 idle 会话，当场拍板，不留悬空。\n"
        )
        out.append("| 会话（标题前30字 + 创建时间 + 目录末段） | 跨度 | 处置结果 | 后续 |")
        out.append("|---|---|---|---|")
        for s in sessions:
            title = truncate(str(s.get("title") or "未命名"), 30)
            created = s.get("created") or "—"
            last = s.get("last_active") or "—"
            cwd_tail = truncate(str(s.get("cwd_tail") or "—"), 20)
            span = f"{created}→{last}"
            decision = s.get("decision") or "待拍板"
            follow = s.get("follow_up") or "关闭/迁移/继续"
            out.append(
                f"| 「{title}」（{created}, {cwd_tail}） | {span} | {decision} | {follow} |"
            )
        out.append("")
        return out

    def _section_automations(self) -> list[str]:
        out = ["## 六、自动化运行概览\n"]
        auto = self.data.get("automations") or {}
        items = auto.get("items") or []
        total = int(auto.get("runs_total") if auto.get("runs_total") is not None else len(items))
        success = int(auto.get("runs_success") or 0)

        if total == 0 and not items:
            out.append("本周无自动化运行记录（或本平台无此概念）。\n")
            return out

        fail = max(total - success, 0)
        out.append(f"本周运行 {total} 次，成功 {success} 次，失败/未知 {fail} 次。\n")
        if items:
            out.append("| 任务标题 | 状态 | 结果 | 来源 |")
            out.append("|---|---|---|---|")
            for r in items[:15]:
                title = truncate(str(r.get("title") or "未命名"), 24)
                status = r.get("status") or "—"
                result = r.get("result") or "—"
                source = truncate(str(r.get("source") or "—"), 20)
                out.append(f"| {title} | {status} | {result} | {source} |")
            out.append("")
        return out
