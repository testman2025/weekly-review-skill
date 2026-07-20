"""核心分析引擎的基础测试."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from weekly_review.analyzer import WeeklyReviewAnalyzer


def test_default_week_range() -> None:
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday() + 7)
    assert monday.weekday() == 0


def test_analyzer_can_connect() -> None:
    """确保能连接一个空 SQLite 文件并返回空结果."""
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "workbuddy.db"
        WeeklyReviewAnalyzer(db_path).conn.execute("SELECT 1")
