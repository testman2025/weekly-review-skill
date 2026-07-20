"""周度复盘核心分析引擎."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from utils import discover_db_path, fmt_hours, safe_div, ts_to_dt, truncate


@dataclass
class SessionRecord:
    id: str
    title: str
    cwd: str
    created_at: datetime | None
    updated_at: datetime | None
    last_activity_at: datetime | None
    status: str
    model: str | None
    source_mode: str | None
    is_background_automation: bool
    size: int = 0
    used: int = 0
    credits: float = 0.0


@dataclass
class ProjectBucket:
    name: str
    sessions: list[SessionRecord] = field(default_factory=list)
    total_seconds: float = 0.0
    credits: float = 0.0


@dataclass
class ReviewResult:
    period_start: datetime
    period_end: datetime
    sessions: list[SessionRecord]
    automations: list[dict[str, Any]]
    automation_runs: list[dict[str, Any]]
    total_wall_seconds: float
    real_active_seconds: float
    total_credits: float
    project_buckets: list[ProjectBucket]
    long_sessions: list[SessionRecord]
    overnight_sessions: list[SessionRecord]
    top_models: list[tuple[str, int]]


class WeeklyReviewAnalyzer:
    """读取 workbuddy.db 并生成本周复盘数据."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = discover_db_path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()

    def query(
        self,
        start: datetime,
        end: datetime,
        include_automations: bool = True,
    ) -> ReviewResult:
        """查询指定时间范围的数据并计算指标."""
        start_ts = int(start.timestamp() * 1000)
        end_ts = int(end.timestamp() * 1000)

        sessions = self._fetch_sessions(start_ts, end_ts)
        self._attach_usage(sessions)

        automations: list[dict[str, Any]] = []
        automation_runs: list[dict[str, Any]] = []
        if include_automations:
            automations = self._fetch_automations()
            automation_runs = self._fetch_automation_runs(start_ts, end_ts)

        buckets = self._bucket_by_project(sessions)
        long_sessions = self._find_long_sessions(sessions)
        overnight_sessions = self._find_overnight_idle(sessions)
        total_wall = self._compute_wall_clock(sessions)
        real_active = self._estimate_real_active(sessions)
        total_credits = round(sum(s.credits for s in sessions), 2)
        top_models = self._top_models(sessions)

        return ReviewResult(
            period_start=start,
            period_end=end,
            sessions=sessions,
            automations=automations,
            automation_runs=automation_runs,
            total_wall_seconds=total_wall,
            real_active_seconds=real_active,
            total_credits=total_credits,
            project_buckets=buckets,
            long_sessions=long_sessions,
            overnight_sessions=overnight_sessions,
            top_models=top_models,
        )

    def _fetch_sessions(
        self, start_ts: int, end_ts: int
    ) -> list[SessionRecord]:
        """拉取时间范围内的会话."""
        # 兼容：只要会话在周期内被创建或活跃过即纳入
        rows = self.conn.execute(
            """
            SELECT s.id, s.cwd, s.title, s.custom_title, s.status,
                   s.created_at, s.updated_at, s.last_activity_at,
                   s.model, s.source_mode, s.is_background_automation
            FROM sessions s
            WHERE (s.created_at BETWEEN ? AND ?)
               OR (s.last_activity_at BETWEEN ? AND ?)
               OR (s.updated_at BETWEEN ? AND ?)
            ORDER BY s.created_at DESC
            """,
            (start_ts, end_ts, start_ts, end_ts, start_ts, end_ts),
        ).fetchall()

        sessions: list[SessionRecord] = []
        for r in rows:
            title = (r["custom_title"] or r["title"] or "未命名会话").strip()
            sessions.append(
                SessionRecord(
                    id=r["id"],
                    title=title,
                    cwd=r["cwd"] or "",
                    created_at=ts_to_dt(r["created_at"]),
                    updated_at=ts_to_dt(r["updated_at"]),
                    last_activity_at=ts_to_dt(r["last_activity_at"]),
                    status=r["status"] or "unknown",
                    model=r["model"],
                    source_mode=r["source_mode"],
                    is_background_automation=bool(r["is_background_automation"]),
                )
            )
        return sessions

    def _attach_usage(self, sessions: list[SessionRecord]) -> None:
        """附加 token/耗时信息."""
        if not sessions:
            return
        ids = [s.id for s in sessions]
        placeholders = ",".join("?" * len(ids))
        rows = self.conn.execute(
            f"""
            SELECT session_id, used, size, credit_json
            FROM session_usage
            WHERE session_id IN ({placeholders})
            """,
            ids,
        ).fetchall()
        usage_map = {r["session_id"]: r for r in rows}

        for s in sessions:
            u = usage_map.get(s.id)
            if not u:
                continue
            s.used = u["used"] or 0
            s.size = u["size"] or 0
            try:
                credit = json.loads(u["credit_json"] or "{}")
                # credit_json 是 provider -> credits/金额 的映射，直接求和
                s.credits = round(sum(float(v) for v in credit.values()), 4)
            except (json.JSONDecodeError, TypeError, ValueError):
                s.credits = 0.0

    def _bucket_by_project(
        self, sessions: list[SessionRecord]
    ) -> list[ProjectBucket]:
        """按工作目录最后一级聚合项目."""
        buckets: dict[str, ProjectBucket] = {}
        for s in sessions:
            # 取 cwd 最后一级作为项目名；空路径归入 default
            name = Path(s.cwd).name or "default" if s.cwd else "default"
            if name not in buckets:
                buckets[name] = ProjectBucket(name=name)
            buckets[name].sessions.append(s)
            # used 字段含义为毫秒级耗时
            buckets[name].total_seconds += s.used / 1000.0
            buckets[name].credits += s.credits

        return sorted(buckets.values(), key=lambda b: b.total_seconds, reverse=True)

    def _find_long_sessions(
        self, sessions: list[SessionRecord], threshold_hours: float = 48.0
    ) -> list[SessionRecord]:
        """识别跨周长会话（创建到最后活跃超过阈值）."""
        threshold = timedelta(hours=threshold_hours)
        result: list[SessionRecord] = []
        for s in sessions:
            if not (s.created_at and s.last_activity_at):
                continue
            if s.last_activity_at - s.created_at > threshold:
                result.append(s)
        return sorted(result, key=lambda s: s.last_activity_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    def _find_overnight_idle(
        self, sessions: list[SessionRecord]
    ) -> list[SessionRecord]:
        """识别跨夜 idle：会话最后活跃时间在次日 06:00 之后."""
        result: list[SessionRecord] = []
        for s in sessions:
            if not s.last_activity_at:
                continue
            # 创建日期与最后活跃日期不同，且最后活跃时间 >= 06:00
            if s.created_at and s.created_at.date() != s.last_activity_at.date():
                if s.last_activity_at.hour >= 6:
                    result.append(s)
        return sorted(result, key=lambda s: s.last_activity_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    def _compute_wall_clock(self, sessions: list[SessionRecord]) -> float:
        """粗略 wall-clock：从最早创建到最晚活跃的跨度."""
        times = [
            t for s in sessions for t in (s.created_at, s.last_activity_at) if t
        ]
        if len(times) < 2:
            return 0.0
        return (max(times) - min(times)).total_seconds()

    def _estimate_real_active(self, sessions: list[SessionRecord]) -> float:
        """估算真实活跃时长：对 used 字段求和（假设 used 为毫秒耗时）."""
        return sum(s.used for s in sessions) / 1000.0

    def _top_models(
        self, sessions: list[SessionRecord], top_k: int = 5
    ) -> list[tuple[str, int]]:
        """按模型统计会话数."""
        counts: dict[str, int] = {}
        for s in sessions:
            model = s.model or "unknown"
            counts[model] = counts.get(model, 0) + 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_k]

    def _fetch_automations(self) -> list[dict[str, Any]]:
        """拉取自动化任务定义."""
        rows = self.conn.execute(
            """
            SELECT id, name, status, schedule_type, rrule, scheduled_at,
                   valid_from, valid_until, next_run_at, last_run_at, cwds
            FROM automations
            WHERE deleted_at IS NULL
            ORDER BY updated_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]

    def _fetch_automation_runs(
        self, start_ts: int, end_ts: int
    ) -> list[dict[str, Any]]:
        """拉取周期内的自动化运行记录."""
        rows = self.conn.execute(
            """
            SELECT thread_id, automation_id, status, result_success,
                   created_at, updated_at, thread_title, source_cwd
            FROM automation_runs
            WHERE created_at BETWEEN ? AND ?
            ORDER BY created_at DESC
            """,
            (start_ts, end_ts),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self) -> None:
        self.conn.close()
