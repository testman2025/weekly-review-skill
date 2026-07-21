"""报告渲染器测试：对齐定稿六章模板。"""

from __future__ import annotations

import json
from pathlib import Path

from report import ReportBuilder

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "skills" / "weekly-review" / "schema" / "review-input.example.json"


def test_render_matches_template_shape() -> None:
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    # 模拟已生成的图表路径
    data.setdefault("dashboard", {})["charts"] = [
        "chart-时间分布-2026-07-19.svg",
        "chart-归因Token-2026-07-19.svg",
    ]
    md = ReportBuilder(data).build()
    assert "周度复盘（weekly-review skill · 六章结构）" in md
    assert "## 一、一页看板" in md
    assert "| 指标 | 数值 | 口径说明 |" in md
    assert "**一句话结论**" in md
    assert "### 辅助图表" in md
    assert "![chart-时间分布-2026-07-19](chart-时间分布-2026-07-19.svg)" in md
    assert "## 二、分项目分析" in md
    assert "### 2.1" in md
    assert "| 维度 | 内容 |" in md
    assert "## 三、问题清单 + 根因三类归因" in md
    assert "**做得好的（正面范本）**" in md
    assert "## 四、本周动作台账 ★" in md
    assert "## 五、待对齐开放会话" in md
    assert "## 六、自动化概览" in md
    assert "## 七、事实更正" in md
    assert "```mermaid" not in md


def test_write_charts(tmp_path=None) -> None:
    from tempfile import TemporaryDirectory

    from charts import write_charts

    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    with TemporaryDirectory() as tmp:
        names = write_charts(data, tmp)
        assert len(names) == 2
        assert any("时间分布" in n for n in names)
        assert any("归因Token" in n for n in names)
        for n in names:
            content = (Path(tmp) / n).read_text(encoding="utf-8")
            assert content.strip().startswith("<svg")
            assert "</svg>" in content

