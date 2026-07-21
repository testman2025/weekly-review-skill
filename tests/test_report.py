"""报告渲染器测试."""

from __future__ import annotations

import json
from pathlib import Path

from report import ReportBuilder


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "skills" / "weekly-review" / "schema" / "review-input.example.json"


def test_render_example() -> None:
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    md = ReportBuilder(data).build()
    assert "一页看板" in md
    assert "分项目分析" in md
    assert "weekly-review-skill" in md
    assert "待对齐开放会话" in md


def test_empty_optional_sections() -> None:
    md = ReportBuilder(
        {
            "period": {"start": "2026-07-13", "end": "2026-07-19"},
            "dashboard": {"session_count": 0, "active_hours": 0},
        }
    ).build()
    assert "2026-07-13" in md
    assert "暂无人工标注问题" in md or "问题清单" in md
