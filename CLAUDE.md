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
| **Database** | PostgreSQL 16 (15 tables) |
| **Version** | v0.1.0 |

---

## Architecture

### Backend (FastAPI)

#### Core Pipeline (12 modules)
- **Deterministic (7)**: system_status, incidents_recent, claude_code_releases, model_deprecations, stack_eol_check, sbom_diff, risk_scorer
- **LLM — Haiku 4.5 (5)**: api_release_notes, app_release_notes, news_digest, interesting_finds, action_items_synthesis
- **Monitoring integrations**: UptimeRobot API, Sentry API, VPS script log parsing, pg_stat_statements
- **Auth**: Google OAuth, single admin user
- **Database**: asyncpg connection pool, 15 tables

#### Intelligence Lab (12 modules)
- **Collectors (10, deterministic)**: intel_hn, intel_rss, intel_reddit, intel_x, intel_x_voices, intel_github, intel_blogs, intel_youtube, intel_anthropic, intel_news
- **Analyzers (2, Claude Sonnet 4.6)**: intel_trend_detector (two-pass: pain points + AI signals), intel_opportunity_brief (cross-stream synthesis)
- **Scoring**: Deterministic momentum/noise algorithm (not LLM)
- **Voice Registry**: Tracked people by tier (visionary/practitioner/buyer)
- **Reply Drafter**: Claude generates helpful, non-salesy responses for pain-point posts

### Frontend (React 18 + TypeScript)
- **9 pages**: Dashboard, Risk Register, SBOM, Action Items, Feed, Monitoring, History, Intelligence Lab, Login
- **Intelligence Lab tabs**: Pain Points, AI Signals, Opportunities, Voices, Digest
- **Styling**: Tailwind CSS with `ho-*` color theme (dark mode only)

### Data Flow
- `POST /api/refresh` → runs all core modules → stores results in DB → populates feed
- `POST /api/intelligence/collect` → runs 10 collectors → stores signals with auto-categorization
- `POST /api/intelligence/analyze` → two-pass trend detection (pain points + AI signals)
- `POST /api/intelligence/synthesize` → cross-stream opportunity generation
- `GET /api/brief/text` → plain text brief for consumption

---

## Database (15 tables)

| Table | Purpose |
|-------|---------|
| components | SBOM — software inventory with versions + EOL dates |
| risk_items | Risk register — categorized risks with status tracking |
| risk_history | Risk status change history |
| action_items | Task list — prioritized actions from modules |
| module_runs | Audit trail — every module execution with results |
| feed_entries | News stream — aggregated updates from all modules |
| sbom_snapshots | SBOM history — daily snapshots with diffs |
| scan_history | Scan audit — version check and EOL scan results |
| sessions | Auth sessions |
| intel_voices | Voice registry — people to follow, tier + platform |
| intel_signals | Raw signals — source, score, category (pain_point/ai_signal), voice link |
| intel_trends | Detected patterns — momentum/noise scores, stream (pain_point/ai_signal) |
| intel_opportunities | Synthesized opportunities — pipeline stages (signal → researched → pitched → won → dismissed) |
| sentry_dismissed_issues | Sentry issue IDs hidden from Hopper Ops display |
| brief_archives | Rolling archive of the last 3 sent daily briefs |

---

## API Endpoints

### Core
| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/health | DB connectivity + uptime |
| GET | /api/status | At-a-glance system overview |
| GET | /api/sbom | Component inventory |
| GET | /api/sbom/diff | SBOM changes since last snapshot |
| GET | /api/risks | Risk register |
| PATCH | /api/risks/:id | Update risk status |
| GET | /api/actions | Action items |
| PATCH | /api/actions/:id | Update action status |
| GET | /api/feed | News/updates stream |
| GET | /api/brief | Compiled daily brief (JSON) |
| GET | /api/brief/text | Plain text brief |
| POST | /api/brief/send | Build + email daily brief, archive snapshot |
| GET | /api/brief/archives | List last 3 archived briefs |
| GET | /api/brief/archives/:id | Fetch a single archived brief |
| GET | /api/brief/archives/:id/html | Raw HTML of a stored brief |
| POST | /api/brief/archives/:id/send | Forward a stored brief |
| GET | /api/modules | Module list with run status |
| POST | /api/refresh | Trigger all core modules |
| POST | /api/refresh/:name | Trigger specific module |
| GET | /api/monitoring | Aggregated Sentry + UptimeRobot + VPS health |
| GET | /api/history | Audit trail |
| GET | /auth/google | OAuth login |
| GET | /auth/me | Current user |

### Intelligence Lab
| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/intelligence/signals | List signals (filter: source, tag, category) |
| GET | /api/intelligence/trends | List trends (filter: status, stream) |
| GET | /api/intelligence/trends/:id | Single trend with evidence |
| PATCH | /api/intelligence/trends/:id | Update trend status |
| GET | /api/intelligence/opportunities | List opportunities (filter: stage) |
| PATCH | /api/intelligence/opportunities/:id | Update opportunity stage/notes |
| GET | /api/intelligence/voices | List voices (filter: tier, platform) |
| POST | /api/intelligence/voices | Create a voice |
| PATCH | /api/intelligence/voices/:id | Update a voice |
| DELETE | /api/intelligence/voices/:id | Soft-delete a voice |
| POST | /api/intelligence/signals/:id/draft-reply | Generate reply for pain-point post |
| POST | /api/intelligence/collect | Run all 10 collectors |
| POST | /api/intelligence/analyze | Two-pass trend analysis |
| POST | /api/intelligence/synthesize | Cross-stream opportunity synthesis |

### Sentry Dismissals
| Method | Path | Purpose |
|--------|------|---------|
| GET | /api/monitoring/sentry/dismissed | List hidden Sentry issue IDs |
| POST | /api/monitoring/sentry/dismiss | Hide a Sentry issue from Hopper Ops |
| DELETE | /api/monitoring/sentry/dismiss/:id | Restore a single hidden issue |
| DELETE | /api/monitoring/sentry/dismiss | Restore ALL hidden issues |

---

## .env Keys

DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SESSION_SECRET, ADMIN_EMAIL, ANTHROPIC_API_KEY, UPTIMEROBOT_API_KEY, SENTRY_API_TOKEN, SENTRY_ORG, SENTRY_DSN, SENTRY_ALLOWED_ENVIRONMENTS, X_BEARER_TOKEN

---

## Named For

Grace Hopper — Navy rear admiral, computer science pioneer. "Hopper" also describes a funnel that processes raw input into refined output — which is exactly what this app does with operational signals.
