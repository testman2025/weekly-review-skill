# Weekly Review Skill

A self-contained, platform-agnostic skill that turns your **local AI session history** (a SQLite database) into a structured weekly retrospective: a one-page dashboard, per-project breakdown, three-class root-cause attribution (approach / memory / process), an action ledger, and a list of open cross-week / overnight sessions to reconcile.

It **vendors the retrospective "base"** (what to look at, how to attribute causes, how to log actions) and leaves weekly specifics (project names, manual notes) to the caller.

## What it does

- Reads a local AI session DB (SQLite) **read-only**.
- Produces: one-page dashboard (wall-clock, real active time, credit usage, session count, long/overnight sessions), per-project analysis, problem list with root-cause triage, action ledger (done / observing / pending), open sessions to align, automation run overview.
- Exposes three forms: **CLI**, **MCP server** (stdio JSON-RPC), and **Agent SKILL**.

## Safety notes (for moderators / reviewers)

- **No third-party dependencies.** Uses only the Python standard library (`sqlite3`, `json`, `argparse`, `datetime`, `pathlib`, `typing`). There is no `pip install` step and nothing is downloaded at runtime.
- **No network calls.** The skill only opens a local SQLite file you point it at (default `~/.workbuddy/workbuddy.db`), reads it, and prints a Markdown/JSON report to stdout or a local file.
- **Read-only.** It never writes to or mutates the source database.
- **No hidden execution.** The only "code" that runs is the bundled Python scripts, executed locally on your own machine, on data you explicitly provide.

## Install

```bash
clawhub install weekly-review
```

Then point your agent at the installed skill directory.

## Usage

### CLI

```bash
cd <skill-dir>
python -m cli --start 2026-07-13 --end 2026-07-19 -o weekly-report.md
```

Options: `--db-path`, `--start`, `--end`, `--output / -o`, `--notes` (JSON of manual problems/actions), `--json`.

### MCP server

```json
{
  "mcpServers": {
    "weekly-review": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": { "PYTHONPATH": "<skill-dir>" }
    }
  }
}
```

Tool: `run_weekly_review` (params: `db_path`, `start_date`, `end_date`, `output_format`, `notes`).

### As an Agent Skill

Copy this directory's `SKILL.md` into your agent's skills folder (e.g. `~/.agents/skills/weekly-review/SKILL.md`).

## Output sections

1. One-page dashboard
2. Per-project analysis (auto-aggregated by working-directory leaf)
3. Problem list + three-class root-cause attribution (approach / memory / process)
4. Action ledger (done / observing / pending)
5. Open sessions to reconcile (>48h cross-week, overnight idle)
6. Automation run overview

## Notes

- Default period: last Monday 00:00 ~ last Sunday 23:59 (UTC), overridable via `--start` / `--end`.
- Cross-week threshold: 48h. Overnight idle threshold: last active after 06:00 next day.
- Long sessions must be reconciled by reading their content/title, not by duration alone.
- Root-cause attribution must distinguish approach / memory / process — never a one-size "collapse everything into one workspace" verdict.

## License

MIT
