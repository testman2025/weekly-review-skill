"""Markdown 报告生成器.

遵循今天（7/20）复盘确立的底座结构：
1. 一页看板
2. 分项目分析
3. 问题清单 + 根因三类归因
4. 本周动作台账
5. 待对齐开放会话
6. 自动化运行概览

不固化成品：具体项目名、归因内容、改进项由调用方/运行时输入决定。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .analyzer import ProjectBucket, ReviewResult, SessionRecord
from .utils import fmt_hours, safe_div, truncate


class ReportBuilder:
    def __init__(self, result: ReviewResult):
        self.r = result

    def build(self, user_notes: dict[str, Any] | None = None) -> str:
        """生成完整 Markdown 报告."""
        notes = user_notes or {}
        lines: list[str] = []
        start_str = self.r.period_start.strftime("%Y-%m-%d")
        end_str = self.r.period_end.strftime("%Y-%m-%d")

        lines.append(f"# {start_str} ~ {end_str} 周度复盘\n")
        lines.append(
            f"> **统计周期**：{start_str}（周一）～ {end_str}（周日）\n"
            f"> **数据来源**：`{self._db_path_hint()}`\n\n"
        )

        lines.extend(self._section_dashboard())
        lines.extend(self._section_projects())
        lines.extend(self._section_problems(notes.get("problems", [])))
        lines.extend(self._section_action_log(notes.get("actions", {})))
        lines.extend(self._section_open_sessions())
        lines.extend(self._section_automations())

        return "\n".join(lines)

    def _db_path_hint(self) -> str:
        return "workbuddy.db"

    def _section_dashboard(self) -> list[str]:
        r = self.r
        avg_session = safe_div(r.real_active_seconds, len(r.sessions))
        out = [
            "## 一、一页看板\n",
            "| 指标 | 数值 | 说明 |",
            "|---|---|---|",
            f"| 原始 wall-clock 时长 | **{fmt_hours(r.total_wall_seconds)}** | 从最早会话到最晚活跃的跨度 |",
            f"| **真实活跃时长** | **{fmt_hours(r.real_active_seconds)}** | 基于 session_usage.used 估算 |",
            f"| Credit 消耗 | **{r.total_credits:.2f}** | 来自 session_usage.credit_json 求和 |",
            f"| 会话数 | {len(r.sessions)} 个 | 含创建或活跃落在周期内的会话 |",

            f"| 平均每会话 | {fmt_hours(avg_session)} | 真实活跃时长 / 会话数 |",
            f"| 跨周长会话 | {len(r.long_sessions)} 个 | 创建到最后活跃 > 48h |",
            f"| 跨夜 idle 会话 | {len(r.overnight_sessions)} 个 | 最后活跃落在次日 06:00 之后 |",
            "",
        ]
        if r.top_models:
            out.append("**常用模型**：" + " / ".join(f"{m}({c})" for m, c in r.top_models))
            out.append("")
        return out

    def _section_projects(self) -> list[str]:
        out = ["## 二、分项目分析\n"]
        if not self.r.project_buckets:
            out.append("本周无项目数据。\n")
            return out

        out.append("| 项目 | 会话数 | 活跃时长 | Credit | 备注 |")
        out.append("|---|---|---|---|---|")
        for b in self.r.project_buckets[:10]:
            credits = f"{b.credits:.2f}" if b.credits else "—"
            out.append(
                f"| {b.name} | {len(b.sessions)} | {fmt_hours(b.total_seconds)} | {credits} | 由 cwd 末级自动聚合 |"
            )
        out.append("")
        return out

    def _section_problems(self, problems: list[dict[str, Any]]) -> list[str]:
        out = [
            "## 三、问题清单 + 根因归因\n",
            "> 归因三类框架：① 思路问题（边做边开新目录，没规划）；② 记忆问题（忘了之前做过）；③ 流程问题（合理分工但缺索引/引用）。三者对应完全不同的建议，禁止一刀切。\n",
            "| # | 问题 | 归因类别 | 根因 | 建议 |",
            "|---|---|---|---|---|",
        ]
        if not problems:
            out.append("| — | 暂无人工标注问题 | — | — | 请在下周期复盘时补充 |")
        for i, p in enumerate(problems, 1):
            cat = p.get("category", "—")
            root = p.get("root_cause", "—")
            suggestion = p.get("suggestion", "—")
            desc = p.get("description", "—")
            out.append(f"| {i} | {desc} | {cat} | {root} | {suggestion} |")
        out.append("")
        return out

    def _section_action_log(self, actions: dict[str, Any]) -> list[str]:
        out = ["## 四、本周动作台账\n"]

        # 当场已改
        out.append("### 4.1 当场已改\n")
        done = actions.get("done", [])
        if not done:
            out.append("暂无。\n")
        else:
            out.append("| # | 动作 | 触发来源 | 改了什么 |")
            out.append("|---|---|---|---|")
            for i, a in enumerate(done, 1):
                out.append(
                    f"| A{i} | {a.get('action','—')} | {a.get('trigger','—')} | {a.get('change','—')} |"
                )
            out.append("")

        # 已改、需观察
        out.append("### 4.2 已改、需后续观察效果\n")
        observing = actions.get("observing", [])
        if not observing:
            out.append("暂无。\n")
        else:
            out.append("| # | 动作 | 怎么判断见效了 |")
            out.append("|---|---|---|")
            for i, a in enumerate(observing, 1):
                out.append(
                    f"| O{i} | {a.get('action','—')} | {a.get('criteria','—')} |"
                )
            out.append("")

        # 待落实
        out.append("### 4.3 待落实\n")
        pending = actions.get("pending", [])
        if not pending:
            out.append("暂无。\n")
        else:
            out.append("| # | 建议 | 优先级 | 截止 | 状态 |")
            out.append("|---|---|---|---|---|")
            for i, a in enumerate(pending, 1):
                out.append(
                    f"| P{i} | {a.get('suggestion','—')} | {a.get('priority','—')} | {a.get('deadline','—')} | {a.get('status','待开始')} |"
                )
            out.append("")

        return out

    def _section_open_sessions(self) -> list[str]:
        out = ["## 五、待对齐开放会话\n"]
        combined = self.r.long_sessions + [
            s for s in self.r.overnight_sessions if s not in self.r.long_sessions
        ]
        if not combined:
            out.append("本周无跨周或跨夜 idle 会话。\n")
            return out

        out.append(
            "> 机制：每周复盘交付时列出跨周(>48h)/跨夜 idle 会话，当场拍板，不留悬空。\n"
        )
        out.append("| 会话（标题前30字 + 创建时间 + 目录末段） | 跨度 | 处置结果 | 后续 |")
        out.append("|---|---|---|---|")
        for s in combined:
            created = s.created_at.strftime("%m/%d") if s.created_at else "—"
            last = s.last_activity_at.strftime("%m/%d") if s.last_activity_at else "—"
            span = f"{created}→{last}"
            title = truncate(s.title, 30)
            cwd_tail = truncate(Path(s.cwd).name or "default", 20)
            out.append(f"| 「{title}」（{created}, {cwd_tail}） | {span} | 待拍板 | 关闭/迁移/继续 |")
        out.append("")
        return out

    def _section_automations(self) -> list[str]:
        out = ["## 六、自动化运行概览\n"]
        if not self.r.automation_runs:
            out.append("本周无自动化运行记录。\n")
            return out

        success = sum(1 for r in self.r.automation_runs if r.get("result_success"))
        total = len(self.r.automation_runs)
        out.append(f"本周运行 {total} 次，成功 {success} 次，失败 {total - success} 次。\n")
        out.append("| 任务标题 | 状态 | 结果 | 来源目录 |")
        out.append("|---|---|---|---|")
        for r in self.r.automation_runs[:10]:
            title = truncate(r.get("thread_title") or "未命名", 24)
            status = r.get("status") or "—"
            result = "成功" if r.get("result_success") else "失败/未知"
            cwd = truncate(r.get("source_cwd") or "—", 20)
            out.append(f"| {title} | {status} | {result} | {cwd} |")
        out.append("")
        return out
