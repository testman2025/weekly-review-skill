"""通用工具函数."""

from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Any


def ts_to_dt(ts: int | float | None) -> datetime.datetime | None:
    """将 SQLite 毫秒/秒级时间戳转换为 datetime，自动判断."""
    if ts is None:
        return None
    # 常见会话库使用毫秒时间戳；秒级时间戳则直接使用
    if ts > 1e12:
        ts = ts / 1000
    try:
        return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    except (OSError, ValueError, OverflowError):
        return None


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    """安全除法."""
    return a / b if b else default


def fmt_hours(seconds: float) -> str:
    """格式化为小时，保留一位小数."""
    return f"{seconds / 3600:.1f}h"


def discover_db_path(hint: str | Path | None = None) -> Path:
    """发现本地 AI 会话库（SQLite）路径.

    优先级：
    1. 显式传入的 ``hint`` / ``--db-path``
    2. 环境变量 ``WEEKLY_REVIEW_DB``
    3. 常见路径自动探测（含多种 agent 产物路径；WorkBuddy 只是其中一种）
    """
    if hint:
        p = Path(hint).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"指定的数据库不存在: {p}")

    env = os.environ.get("WEEKLY_REVIEW_DB") or os.environ.get("AI_SESSION_DB")
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"环境变量指向的数据库不存在: {p}")

    # 常见路径探测：不绑定单一产品；命中任一即可
    home = Path.home()
    cwd = Path.cwd()
    candidates = [
        home / ".workbuddy" / "workbuddy.db",
        home / "workbuddy.db",
        home / ".openclaw" / "sessions.db",
        home / ".agents" / "sessions.db",
        home / ".cursor" / "sessions.db",
        cwd / "sessions.db",
        cwd / "workbuddy.db",
        cwd / "agent-sessions.db",
    ]
    for c in candidates:
        if c.exists():
            return c

    raise FileNotFoundError(
        "未找到本地 AI 会话库（SQLite）。"
        "请用 --db-path 指定，或设置环境变量 WEEKLY_REVIEW_DB。"
        "库需包含 sessions 表（见 skill 文档「数据源约定」）。"
    )


def truncate(s: str, max_len: int = 30) -> str:
    """截断字符串."""
    return s if len(s) <= max_len else s[:max_len] + "…"


def table_exists(conn: Any, name: str) -> bool:
    """检查 SQLite 表是否存在."""
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None
