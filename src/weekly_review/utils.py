"""通用工具函数."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any


def ts_to_dt(ts: int | float | None) -> datetime.datetime | None:
    """将 SQLite 毫秒/秒级时间戳转换为 datetime，自动判断."""
    if ts is None:
        return None
    # workbuddy.db 使用毫秒时间戳
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
    """发现 workbuddy.db 路径."""
    if hint:
        p = Path(hint).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"指定的数据库不存在: {p}")

    # 常见路径探测
    candidates = [
        Path.home() / ".workbuddy" / "workbuddy.db",
        Path.home() / "workbuddy.db",
        Path.cwd() / "workbuddy.db",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("未找到 workbuddy.db，请通过 --db-path 指定")


def truncate(s: str, max_len: int = 30) -> str:
    """截断字符串."""
    return s if len(s) <= max_len else s[:max_len] + "…"
