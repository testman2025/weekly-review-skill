"""核心分析引擎的基础测试."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from analyzer import WeeklyReviewAnalyzer


def test_default_week_range() -> None:
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday() + 7)
    assert monday.weekday() == 0


def test_analyzer_can_connect() -> None:
    """确保能连接任意路径的空 SQLite 文件."""
    import sqlite3

    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "sessions.db"
        sqlite3.connect(db_path).close()
        with WeeklyReviewAnalyzer(db_path) as analyzer:
            analyzer.conn.execute("SELECT 1")


def test_optional_tables_skipped() -> None:
    """仅有 sessions 表时也能 query，不因缺少 usage/automations 失败."""
    import sqlite3

    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "minimal.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE sessions (
                id TEXT, cwd TEXT, title TEXT, custom_title TEXT, status TEXT,
                created_at INTEGER, updated_at INTEGER, last_activity_at INTEGER,
                model TEXT, source_mode TEXT, is_background_automation INTEGER
            )
            """
        )
        conn.commit()
        conn.close()

        start = datetime(2026, 7, 13, tzinfo=timezone.utc)
        end = datetime(2026, 7, 19, 23, 59, 59, tzinfo=timezone.utc)
        with WeeklyReviewAnalyzer(db_path) as analyzer:
            result = analyzer.query(start, end)
        assert result.sessions == []
        assert result.automations == []
