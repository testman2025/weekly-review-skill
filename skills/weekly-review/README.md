# Weekly Review Skill

**Agent collects facts; this skill defines the retrospective structure** (and optionally renders Markdown).

Install on any Agent that supports Skills / MCP. The host Agent reads its own platform’s session history; this skill does **not** ship per-vendor DB adapters.

## What it does

- Defines a fixed weekly review: dashboard, per-project, root-cause triage (approach / memory / process), action ledger, open sessions, automations.
- Accepts a standard `review-input` JSON (see `schema/`).
- Optional CLI / MCP renderer (Python stdlib only).

## Safety

- No network calls in the renderer.
- No reading of local session databases by default.
- No secrets required.

## Install

```bash
openclaw skills install weekly-review
# or
clawhub install weekly-review
```

## Usage

1. Agent gathers this week’s session facts from **its own platform**.
2. Fill `review-input` (see `schema/review-input.example.json`).
3. Output the six sections in chat, or render:

```bash
cd <skill-dir>
python -m cli --input schema/review-input.example.json -o weekly-report.md
```

### MCP

Tool `run_weekly_review` requires `review_input` object (not `db_path`).

## License

- Repo source: MIT.
- ClawHub distribution: MIT-0.
