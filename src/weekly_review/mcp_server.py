"""轻量 MCP server，任何支持 MCP 的 agent 都能调用.

不依赖 `mcp` 官方包，使用 stdio JSON-RPC 2.0 实现。
暴露工具：
- `run_weekly_review`: 运行周度复盘并返回 markdown 报告或原始指标 JSON。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

from .analyzer import WeeklyReviewAnalyzer
from .report import ReportBuilder


TOOLS_SCHEMA = {
    "tools": [
        {
            "name": "run_weekly_review",
            "description": "基于 workbuddy.db 生成指定周期的周度复盘报告。",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "workbuddy.db 绝对路径。不传则自动发现。",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "开始日期，如 2026-07-13。不传默认上周一。",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期，如 2026-07-19。不传默认上周日。",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["markdown", "json"],
                        "description": "输出格式，默认 markdown。",
                    },
                    "notes": {
                        "type": "object",
                        "description": "人工标注：problems/actions 等，会写入报告对应章节。",
                    },
                },
            },
        }
    ]
}


def _default_week_range() -> tuple[datetime, datetime]:
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday() + 7)
    sunday = monday + timedelta(days=6)
    start = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
    end = datetime(
        sunday.year, sunday.month, sunday.day, 23, 59, 59, tzinfo=timezone.utc
    )
    return start, end


def _parse_date(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _run_review(params: dict[str, Any]) -> dict[str, Any]:
    start, end = _default_week_range()
    if params.get("start_date"):
        start = _parse_date(params["start_date"])
    if params.get("end_date"):
        end = _parse_date(params["end_date"])

    notes = params.get("notes") or {}
    fmt = params.get("output_format", "markdown")

    with WeeklyReviewAnalyzer(params.get("db_path")) as analyzer:
        result = analyzer.query(start, end)

    if fmt == "json":
        content = json.dumps(
            {
                "period": {
                    "start": result.period_start.isoformat(),
                    "end": result.period_end.isoformat(),
                },
                "sessions_count": len(result.sessions),
                "real_active_hours": round(result.real_active_seconds / 3600, 2),
                "total_credits": result.total_credits,
                "projects": [
                    {
                        "name": b.name,
                        "sessions": len(b.sessions),
                        "hours": round(b.total_seconds / 3600, 2),
                        "credits": round(b.credits, 2),
                    }
                    for b in result.project_buckets
                ],
                "long_sessions": [
                    {"id": s.id, "title": s.title, "cwd": s.cwd}
                    for s in result.long_sessions
                ],
                "overnight_sessions": [
                    {"id": s.id, "title": s.title, "cwd": s.cwd}
                    for s in result.overnight_sessions
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        content = ReportBuilder(result).build(notes)

    return {
        "content": [
            {
                "type": "text",
                "text": content,
            }
        ]
    }


def _send_response(id_: Any, result: Any) -> None:
    msg = {"jsonrpc": "2.0", "id": id_, "result": result}
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _send_error(id_: Any, code: int, message: str) -> None:
    msg = {"jsonrpc": "2.0", "id": id_, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _handle_request(req: dict[str, Any]) -> None:
    method = req.get("method")
    id_ = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        _send_response(
            id_,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "weekly-review-skill-mcp",
                    "version": "0.1.0",
                },
                "capabilities": {"tools": {}},
            },
        )
    elif method == "notifications/initialized":
        pass
    elif method == "tools/list":
        _send_response(id_, TOOLS_SCHEMA)
    elif method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name != "run_weekly_review":
            _send_error(id_, -32601, f"未知工具: {name}")
            return
        try:
            result = _run_review(arguments)
            _send_response(id_, result)
        except Exception as e:
            _send_error(id_, -32603, f"运行复盘失败: {e}")
    else:
        _send_error(id_, -32601, f"未知方法: {method}")


def serve() -> None:
    """启动 stdio MCP server."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            _send_error(None, -32700, "非法 JSON")
            continue
        _handle_request(req)


if __name__ == "__main__":
    serve()
