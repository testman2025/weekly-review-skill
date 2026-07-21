"""CLI 冒烟测试."""

from __future__ import annotations

from pathlib import Path

from cli import main

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "skills" / "weekly-review" / "schema" / "review-input.example.json"


def test_cli_renders_to_file(tmp_path: Path | None = None) -> None:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.md"
        code = main(["--input", str(EXAMPLE), "-o", str(out)])
        assert code == 0
        text = out.read_text(encoding="utf-8")
        assert "周度复盘" in text
