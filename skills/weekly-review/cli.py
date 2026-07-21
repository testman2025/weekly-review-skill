"""命令行入口：将 Agent 整理的 review-input JSON 渲染为 Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from report import ReportBuilder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="周度复盘渲染器：输入 Agent 采集的 review-input JSON，输出 Markdown"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="review-input JSON 路径（见 schema/review-input.example.json）",
    )
    parser.add_argument("--output", "-o", help="输出 markdown 文件路径")
    parser.add_argument(
        "--json",
        action="store_true",
        help="原样输出校验后的 JSON（不做 Markdown 渲染）",
    )
    args = parser.parse_args(argv)

    path = Path(args.input).expanduser()
    if not path.exists():
        print(f"输入文件不存在: {path}", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("review-input 必须是 JSON 对象", file=sys.stderr)
        return 1
    if not (data.get("period") or {}).get("start"):
        print("缺少 period.start", file=sys.stderr)
        return 1

    if args.json:
        text = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        text = ReportBuilder(data).build()

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        try:
            print(f"报告已保存：{args.output}")
        except UnicodeEncodeError:
            print(f"Saved: {args.output}")
    else:
        try:
            print(text)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(text.encode("utf-8"))
            sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
