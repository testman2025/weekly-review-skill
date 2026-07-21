# Weekly Review Skill

Host Agent collects facts; this skill locks the **six-chapter Markdown template** used in production retrospectives.

## Output shape (locked)

1. Dashboard table (`指标 | 数值 | 口径说明`) + one-liner + optional PNG chart paths  
2. Theme project sections with dimension tables (incl. disk verification)  
3. Problems + three-class root cause + positives  
4. Action ledger  
5. Open sessions  
6. Automations overview  
7. Fact corrections (optional)

Charts = PNG paths under 辅助图表 — not Mermaid as the primary layout.

## Install / render

```bash
python -m cli --input schema/review-input.example.json -o weekly-report.md
```

See `SKILL.md` and `schema/`.
