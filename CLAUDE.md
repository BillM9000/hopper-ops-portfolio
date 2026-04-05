# Hopper Ops — CLAUDE.md

## Quick Reference

| Item | Value |
|------|-------|
| **Stack** | FastAPI (Python 3.12) + React 18 + TypeScript + Vite + Tailwind CSS + PostgreSQL 16 |
| **Server** | `uvicorn server.main:app --port 3616` |
| **Client dev** | `cd client && npm run dev` → port 5173, proxies /api to :3616 |
| **Build** | `npm run build --prefix client` (Vite, outputs to client/dist/) |
| **Typecheck** | `cd client && npm run typecheck` |
| **Docker** | `docker compose build --no-cache && docker compose up -d` |
| **Port** | 3616 (localhost only, reverse proxy in front) |
| **Database** | PostgreSQL 16 |
| **Version** | v0.1.0 |

---

## Architecture

### Backend (FastAPI)
- **12 modules**: 7 deterministic + 5 LLM (editorial, requires ANTHROPIC_API_KEY)
- **Deterministic**: system_status, incidents_recent, claude_code_releases, model_deprecations, stack_eol_check, sbom_diff, risk_scorer
- **LLM**: api_release_notes, app_release_notes, news_digest, interesting_finds, action_items_synthesis
- **Monitoring integrations**: UptimeRobot API, Sentry API, VPS script log parsing
- **Auth**: Google OAuth, single admin user
- **Database**: asyncpg connection pool, 8 tables

### Frontend (React 18 + TypeScript)
- **7 pages**: Dashboard, Risk Register, SBOM, Action Items, Feed, Monitoring, History
- **6 components**: Layout, StatusBadge, RiskRow, ActionCard, FeedEntry, ModuleStatus, RefreshButton
- **Styling**: Tailwind CSS with `ho-*` color theme (dark mode only)

### Data Flow
- `POST /api/refresh` → runs all modules → stores results in DB → populates feed
- Frontend fetches from `/api/status`, `/api/risks`, `/api/actions`, `/api/feed`, `/api/monitoring`
- `GET /api/brief/text` → plain text brief for consumption

---

## Database (8 tables)

| Table | Purpose |
|-------|---------|
| components | SBOM — software inventory with versions + EOL dates |
| risk_items | Risk register — categorized risks with status tracking |
| action_items | Task list — prioritized actions from modules |
| module_runs | Audit trail — every module execution with results |
| feed_entries | News stream — aggregated updates from all modules |
| sbom_snapshots | SBOM history — daily snapshots with diffs |
| scan_history | Scan audit — version check and EOL scan results |
| sessions | Auth sessions |

---

## .env Keys

DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SESSION_SECRET, ADMIN_EMAIL, ANTHROPIC_API_KEY, UPTIMEROBOT_API_KEY, SENTRY_API_TOKEN, SENTRY_ORG, SENTRY_DSN

---

## Named For

Grace Hopper — Navy rear admiral, computer science pioneer. "Hopper" also describes a funnel that processes raw input into refined output — which is exactly what this app does with operational signals.
