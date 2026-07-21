# Weekly Review Skill

An **agent-agnostic** skill that turns a **local AI session history** (compatible SQLite) into a structured weekly retrospective: one-page dashboard, per-project breakdown, three-class root-cause attribution (approach / memory / process), an action ledger, and open cross-week / overnight sessions to reconcile.

It works with **any agent runtime** that can host Skills or MCP (OpenClaw, Cursor, Claude Code, etc.). It is **not WorkBuddy-only** — WorkBuddy’s DB path is merely one auto-discovery candidate.

It **vendors the retrospective "base"** and leaves weekly specifics (project names, manual notes) to the caller.

## What it does

- Reads a local AI session DB (SQLite) **read-only**.
- Produces: one-page dashboard, per-project analysis, problem list with root-cause triage, action ledger, open sessions to align, automation run overview (if tables exist).
- Exposes three forms: **CLI**, **MCP server** (stdio JSON-RPC), and **Agent SKILL**.

## Safety notes (for moderators / reviewers)

- **No third-party dependencies.** Python standard library only.
- **No network calls.** Opens a local SQLite file you point at, then prints Markdown/JSON.
- **Read-only.** Never mutates the source database.
- **No secrets / env credentials** required (optional `WEEKLY_REVIEW_DB` is only a path).
- **Agent-agnostic.** Not locked to WorkBuddy or any single vendor.

## Install

```bash
openclaw skills install weekly-review
# or
clawhub install weekly-review
```

Requires Python ≥ 3.10. Point any agent at the installed skill directory.

## Data source (not product-specific)

| Priority | How |
|----------|-----|
| 1 | `--db-path /path/to/sessions.db` |
| 2 | Env `WEEKLY_REVIEW_DB` (or `AI_SESSION_DB`) |
| 3 | Auto-discover common paths (WorkBuddy / OpenClaw / Cursor / `sessions.db`, etc.) |

**Required table:** `sessions` (see `SKILL.md` 「数据源约定」).  
**Optional:** `session_usage`, `automations`, `automation_runs` — skipped if missing.

## Usage

### CLI

```bash
cd <skill-dir>
python -m cli --db-path /path/to/your-sessions.db --start 2026-07-13 --end 2026-07-19 -o weekly-report.md
```

Options: `--db-path`, `--start`, `--end`, `--output / -o`, `--notes`, `--json`.

### MCP server

```json
{
  "mcpServers": {
    "weekly-review": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PYTHONPATH": "<skill-dir>",
        "WEEKLY_REVIEW_DB": "/path/to/your-sessions.db"
      }
    }
  }
}
```

Tool: `run_weekly_review`.

### As an Agent Skill

Copy this directory into your agent’s skills folder (any agent that reads `SKILL.md`).

## License

- Source in this repository: MIT (see repo root).
- Skills published on ClawHub are distributed under the registry's MIT-0 terms.
