"""命令行入口."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from analyzer import WeeklyReviewAnalyzer
from report import ReportBuilder


def default_week_range() -> tuple[datetime, datetime]:
    """默认统计上周一 00:00 到本周日 23:59."""
    today = datetime.now(timezone.utc).date()
    # 上周一
    monday = today - timedelta(days=today.weekday() + 7)
    sunday = monday + timedelta(days=6)
    start = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
    end = datetime(
        sunday.year, sunday.month, sunday.day, 23, 59, 59, tzinfo=timezone.utc
    )
    return start, end


def parse_date(s: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期: {s}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="周度复盘分析器")
    parser.add_argument("--db-path", help="workbuddy.db 路径，默认自动发现")
    parser.add_argument(
        "--start", help="开始日期（如 2026-07-13），默认上周一"
    )
    parser.add_argument(
        "--end", help="结束日期（如 2026-07-19），默认上周日"
    )
    parser.add_argument("--output", "-o", help="输出 markdown 文件路径")
    parser.add_argument(
        "--notes", help="JSON 文件：人工标注的问题/动作台账"
    )
    parser.add_argument(
        "--json", action="store_true", help="输出原始 JSON 而非 markdown"
    )
    args = parser.parse_args(argv)

    start, end = default_week_range()
    if args.start:
        start = parse_date(args.start)
    if args.end:
        end = parse_date(args.end)

    notes: dict = {}
    if args.notes:
        notes = json.loads(Path(args.notes).read_text(encoding="utf-8"))

    with WeeklyReviewAnalyzer(args.db_path) as analyzer:
        result = analyzer.query(start, end)

    if args.json:
        # 简单序列化
        data = {
            "period": {
                "start": result.period_start.isoformat(),
                "end": result.period_end.isoformat(),
            },
            "sessions_count": len(result.sessions),
            "real_active_hours": result.real_active_seconds / 3600,
            "total_token": result.total_token,
            "projects": [
                {"name": b.name, "sessions": len(b.sessions), "hours": b.total_seconds / 3600}
                for b in result.project_buckets
            ],
            "long_sessions": [
                {"id": s.id, "title": s.title, "cwd": s.cwd}
                for s in result.long_sessions
            ],
        }
        text = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        text = ReportBuilder(result).build(notes)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"报告已保存：{args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
