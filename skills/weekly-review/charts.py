"""用标准库生成周度复盘辅助图表（SVG，无第三方依赖）。

定稿约定两张图：
- chart-时间分布-YYYY-MM-DD.svg
- chart-归因Token-YYYY-MM-DD.svg
"""

from __future__ import annotations

import html
import math
import re
from pathlib import Path
from typing import Any


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _parse_hours(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = re.search(r"([\d.]+)", str(value).replace(",", "").replace("万", "0000"))
    if not m:
        return None
    return float(m.group(1))


def _bar_chart(
    title: str,
    items: list[tuple[str, float]],
    *,
    ylabel: str = "",
    width: int = 720,
    height: int = 420,
) -> str:
    """水平可读的竖直柱状图 SVG."""
    if not items:
        items = [("无数据", 0.0)]
    labels = [lab for lab, _ in items]
    values = [max(0.0, v) for _, v in items]
    vmax = max(values) if any(values) else 1.0
    vmax *= 1.15

    margin_l, margin_r, margin_t, margin_b = 70, 30, 56, 90
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    n = len(items)
    gap = 16
    bar_w = max(24.0, (plot_w - gap * (n + 1)) / n)
    colors = ["#3D5A80", "#EE6C4D", "#98C1D9", "#293241", "#E0FBFC", "#F2CC8F"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#F7F5F2"/>',
        f'<text x="{width/2}" y="32" text-anchor="middle" '
        f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="18" '
        f'font-weight="600" fill="#1B1B1B">{_esc(title)}</text>',
    ]

    # grid + axis
    parts.append(
        f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" '
        f'y2="{margin_t + plot_h}" stroke="#999" stroke-width="1.5"/>'
    )
    parts.append(
        f'<line x1="{margin_l}" y1="{margin_t + plot_h}" x2="{margin_l + plot_w}" '
        f'y2="{margin_t + plot_h}" stroke="#999" stroke-width="1.5"/>'
    )
    for i in range(5):
        y = margin_t + plot_h - (plot_h * i / 4)
        val = vmax * i / 4
        parts.append(
            f'<line x1="{margin_l}" y1="{y:.1f}" x2="{margin_l + plot_w}" '
            f'y2="{y:.1f}" stroke="#DDD" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{margin_l - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="11" '
            f'fill="#666">{val:.1f}</text>'
        )
    if ylabel:
        parts.append(
            f'<text x="18" y="{margin_t + plot_h/2}" text-anchor="middle" '
            f'transform="rotate(-90 18 {margin_t + plot_h/2})" '
            f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="12" '
            f'fill="#555">{_esc(ylabel)}</text>'
        )

    for i, (lab, val) in enumerate(zip(labels, values)):
        x = margin_l + gap + i * (bar_w + gap)
        h = 0 if vmax <= 0 else (val / vmax) * plot_h
        y = margin_t + plot_h - h
        color = colors[i % len(colors)]
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
            f'fill="{color}" rx="4"/>'
        )
        parts.append(
            f'<text x="{x + bar_w/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" '
            f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="12" '
            f'font-weight="600" fill="#222">{val:.1f}</text>'
        )
        # wrap label
        short = lab if len(lab) <= 10 else lab[:9] + "…"
        parts.append(
            f'<text x="{x + bar_w/2:.1f}" y="{margin_t + plot_h + 22}" '
            f'text-anchor="middle" font-family="Segoe UI, Microsoft YaHei, sans-serif" '
            f'font-size="12" fill="#333">{_esc(short)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _pie_chart(
    title: str,
    items: list[tuple[str, float]],
    *,
    width: int = 720,
    height: int = 420,
) -> str:
    total = sum(max(0.0, v) for _, v in items) or 1.0
    cx, cy, r = width * 0.38, height * 0.55, min(width, height) * 0.28
    colors = ["#3D5A80", "#EE6C4D", "#98C1D9", "#293241", "#E0FBFC", "#F2CC8F", "#81B29A"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#F7F5F2"/>',
        f'<text x="{width/2}" y="32" text-anchor="middle" '
        f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="18" '
        f'font-weight="600" fill="#1B1B1B">{_esc(title)}</text>',
    ]
    angle = -math.pi / 2
    for i, (lab, val) in enumerate(items):
        val = max(0.0, val)
        sweep = 2 * math.pi * (val / total)
        x1 = cx + r * math.cos(angle)
        y1 = cy + r * math.sin(angle)
        angle2 = angle + sweep
        x2 = cx + r * math.cos(angle2)
        y2 = cy + r * math.sin(angle2)
        large = 1 if sweep > math.pi else 0
        color = colors[i % len(colors)]
        parts.append(
            f'<path d="M {cx:.1f} {cy:.1f} L {x1:.1f} {y1:.1f} '
            f'A {r:.1f} {r:.1f} 0 {large} 1 {x2:.1f} {y2:.1f} Z" fill="{color}"/>'
        )
        angle = angle2

    # legend
    lx, ly = width * 0.68, 80
    for i, (lab, val) in enumerate(items):
        color = colors[i % len(colors)]
        pct = 100.0 * max(0.0, val) / total
        y = ly + i * 28
        parts.append(f'<rect x="{lx}" y="{y}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(
            f'<text x="{lx + 22}" y="{y + 12}" '
            f'font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="13" '
            f'fill="#222">{_esc(lab)} ({pct:.0f}%)</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def build_chart_payloads(data: dict[str, Any]) -> dict[str, str]:
    """根据 review-input 生成两张 SVG 字符串."""
    period = data.get("period") or {}
    end = period.get("end") or "week"
    d = data.get("dashboard") or {}

    # 时间分布：真实活跃 + 各主题时长
    time_items: list[tuple[str, float]] = []
    active = d.get("active_hours")
    if active is None and d.get("metrics"):
        for m in d["metrics"]:
            name = str(m.get("name") or "")
            if "真实活跃" in name:
                active = _parse_hours(m.get("value"))
                break
    if active is not None:
        time_items.append(("真实活跃", float(active)))

    for p in data.get("projects") or []:
        title = str(p.get("title") or p.get("name") or "主题")
        # 标题里常带 ≈15.4h
        h = _parse_hours(title)
        if h is None:
            h = _parse_hours(p.get("hours"))
        if h is None:
            continue
        short = title.split("（")[0].split("(")[0].strip()
        if len(short) > 12:
            short = short[:11] + "…"
        time_items.append((short, h))

    if len(time_items) < 2:
        # fallback flat hours
        for p in data.get("projects") or []:
            h = _parse_hours(p.get("hours"))
            if h is not None:
                time_items.append((str(p.get("name") or "项目")[:12], h))

    # 归因 / Token：问题类别计数，或 credits/hours by project
    attr_items: list[tuple[str, float]] = []
    cat_counts: dict[str, float] = {}
    for p in data.get("problems") or []:
        cat = str(p.get("category") or "未分类")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    if cat_counts:
        attr_items = list(cat_counts.items())
    else:
        for p in data.get("projects") or []:
            c = p.get("credits")
            h = _parse_hours(p.get("hours")) or _parse_hours(p.get("title"))
            name = str(p.get("name") or p.get("title") or "项目")
            name = name.split("（")[0].split("(")[0].strip()[:12]
            if c is not None:
                attr_items.append((name, float(c)))
            elif h is not None:
                attr_items.append((name, float(h)))

    if not attr_items:
        tokens = d.get("tokens") or d.get("credits") or 1
        attr_items = [("本周用量", float(_parse_hours(tokens) or 1))]

    return {
        f"chart-时间分布-{end}.svg": _bar_chart(
            f"时间分布（{end}）", time_items or [("真实活跃", 1.0)], ylabel="小时"
        ),
        f"chart-归因Token-{end}.svg": _pie_chart(
            f"归因 / 用量结构（{end}）", attr_items
        ),
    }


def write_charts(
    data: dict[str, Any], charts_dir: str | Path
) -> list[str]:
    """写出 SVG，返回相对文件名列表（供 dashboard.charts / 报告嵌入）."""
    out_dir = Path(charts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for name, svg in build_chart_payloads(data).items():
        path = out_dir / name
        path.write_text(svg, encoding="utf-8")
        names.append(name)
    return names
