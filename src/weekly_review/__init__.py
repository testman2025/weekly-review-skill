"""Weekly Review Skill - 通用周度复盘分析引擎.

固化底座：
- 读取 workbuddy.db / 兼容 SQLite 会话数据库
- 生成一页看板、项目分布、根因三类归因、动作台账、待对齐开放会话
- 通过 CLI / MCP / WorkBuddy SKILL 三种形态暴露

不固化成品：
- 每周具体项目名、自定义改进项由使用者/运行时输入决定
"""

__version__ = "0.1.0"

from .analyzer import WeeklyReviewAnalyzer
from .report import ReportBuilder

__all__ = ["WeeklyReviewAnalyzer", "ReportBuilder"]
