# Hopper Ops — Operational Intelligence Platform

**Technology Risk Register | SBOM Management | Infrastructure Monitoring | Market Intelligence**

Hopper Ops is a purpose-built operational intelligence dashboard that serves as the single source of truth for GraceZero AI's infrastructure state, technology lifecycle management, and risk posture. It replaces scattered manual checks with a unified, automated system that runs 24 data collection modules across two pipelines — a core operations pipeline and an AI-powered market intelligence pipeline — surfaces risks, and delivers a daily operational brief.

Named for **Grace Hopper** — Navy rear admiral, computer science pioneer — and the concept of a hopper: a funnel that processes raw operational signals into refined, actionable intelligence.

**Live:** [hopperops.gracezero.ai](https://hopperops.gracezero.ai) | **Public Repo:** [github.com/BillM9000/hopper-ops-portfolio](https://github.com/BillM9000/hopper-ops-portfolio)

---

## What It Does

- **Technology risk register** — auto-scored risks across every app in the stack (EOL, security, deprecation, drift)
- **SBOM (Software Bill of Materials)** — full inventory of every component with EOL countdown and daily diff
- **Infrastructure monitoring** — single pane of glass: UptimeRobot uptime, Sentry errors, Docker container health, slow query tracking via `pg_stat_statements`
- **Daily brief** — automated email every morning compiling status, incidents, Claude Code releases, model deprecations, and AI-summarized news; archives last 3 briefs with inline viewer and forward capability
- **Market intelligence pipeline (Intelligence Lab)** — multi-source signal collection, deterministic scoring, LLM trend detection, and cross-stream opportunity synthesis

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Hopper Ops                                │
│                    hopperops.gracezero.ai                           │
│                                                                     │
│   CORE PIPELINE                    INTELLIGENCE PIPELINE            │
│   ─────────────                    ─────────────────────           │
│   ┌──────────────┐                 ┌──────────────────┐            │
│   │ Module Runner│                 │ 10 Collectors    │            │
│   │ (12 modules) │                 │ HN, RSS, Reddit  │            │
│   │ 7 determ.    │                 │ X, X Voices      │            │
│   │ 5 LLM        │                 │ GitHub, Blogs    │            │
│   └──────┬───────┘                 │ YouTube, Anth.   │            │
│          │                         │ News             │            │
│          │                         └──────┬───────────┘            │
│          │                                │                         │
│          │               ┌────────────────▼──────────┐             │
│          │               │ 2 Analyzers (Claude Sonnet)│             │
│          │               │ - Trend detector (2-pass)  │             │
│          │               │ - Opportunity synthesizer  │             │
│          │               └────────────────┬──────────┘             │
│          │                                │                         │
│   ┌──────▼────────────────────────────────▼────────────────────┐   │
│   │                   PostgreSQL (15 tables)                    │   │
│   └───────────────────────────┬────────────────────────────────┘   │
│                               │                                     │
│   ┌───────────────────────────▼────────────────────────────────┐   │
│   │                 FastAPI API Layer (35+ endpoints)           │   │
│   └───────────────────────────┬────────────────────────────────┘   │
│                               │                                     │
│   ┌───────────────────────────▼────────────────────────────────┐   │
│   │              React Dashboard (9 pages)                      │   │
│   │   Dashboard · Risk · SBOM · Actions · Feed · Monitoring     │   │
│   │   History · Intelligence Lab · Login                        │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   Outputs:  Daily email brief · Plain-text brief endpoint           │
└─────────────────────────────────────────────────────────────────────┘

External Sources:
├── Anthropic Status API (status.claude.com)
├── GitHub Releases (claude-code atom feed)
├── endoflife.date API (stack EOL tracking)
├── UptimeRobot API (uptime + response times)
├── Sentry API (error tracking + issue counts)
├── Hacker News, Reddit, X, GitHub Trending, AI Lab Blogs, RSS
├── YouTube (channel RSS), Google News RSS
└── Claude API (Haiku 4.5 — editorial; Sonnet 4.6 — Intel analyzers)
```

### Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12), asyncpg |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL 16 (15 tables) |
| Auth | Google OAuth 2.0 (single-admin) |
| LLM | Claude Haiku 4.5 (editorial modules) · Claude Sonnet 4.6 (Intel analyzers) |
| Infrastructure | Docker, Traefik (TLS + Let's Encrypt), Ubuntu 24.04 LTS |
| Monitoring | UptimeRobot, Sentry, custom health scripts, pg_stat_statements |

---

## Core Operations Pipeline (12 Modules)

The core pipeline runs on schedule and on-demand, collecting and synthesizing operational data.

### Deterministic Modules (7)

| Module | Source | Output |
|--------|--------|--------|
| `system_status` | Anthropic Status API | Current platform health |
| `incidents_recent` | Anthropic Status API | Incidents in last 7 days |
| `claude_code_releases` | GitHub atom feed | Latest Claude Code versions |
| `model_deprecations` | Anthropic changelog | Deprecation alerts |
| `stack_eol_check` | endoflife.date API | EOL countdown per component |
| `sbom_diff` | DB snapshot comparison | Component changes since last run |
| `risk_scorer` | SBOM + Sentry + incidents | Auto-scored risk register |

### LLM Editorial Modules (5, Claude Haiku 4.5)

| Module | What It Generates |
|--------|------------------|
| `api_release_notes` | AI-summarized Anthropic API changes |
| `app_release_notes` | AI-summarized Claude app updates |
| `news_digest` | Curated AI/tech news digest |
| `interesting_finds` | Noteworthy items across all signals |
| `action_items_synthesis` | Prioritized action list from all module data |

---

## Intelligence Lab

The Intelligence Lab is a three-stage market intelligence pipeline that answers: *"What should GraceZero pitch this week?"*

### Pipeline: Collect → Analyze → Synthesize

```
┌─────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  10 Signal  │────▶│  Two-Pass Trend   │────▶│  Opportunity     │
│  Collectors │     │  Detector         │     │  Synthesizer     │
│             │     │  (Claude Sonnet)  │     │  (Claude Sonnet) │
│  pain_point │     │                   │     │                  │
│  ai_signal  │     │  Pass 1: cluster  │     │  Cross pain pts  │
│  (labeled   │     │  pain points      │     │  with AI signals │
│  at ingest) │     │                   │     │                  │
│             │     │  Pass 2: cluster  │     │  Output: pitch   │
│             │     │  AI signals       │     │  angle, market,  │
│             │     │                   │     │  gap, effort,    │
│             │     │                   │     │  build-vs-wait   │
└─────────────┘     └───────────────────┘     └──────────────────┘
```

### Signal Collectors (10)

| Collector | Source | Auto-Category |
|-----------|--------|---------------|
| `intel_hn` | Hacker News top + Show HN | mixed |
| `intel_rss` | 10 curated AI/tech RSS feeds | ai_signal |
| `intel_reddit` | 8 subreddits (SaaS, n8n, automation, etc.) | pain_point (keyword match) |
| `intel_x` | X keyword search (5 terms) | mixed |
| `intel_x_voices` | X accounts from voice registry | by voice tier |
| `intel_github` | GitHub daily trending repos | ai_signal |
| `intel_blogs` | AI lab blogs (Anthropic, OpenAI, Google, Meta, Mistral) | ai_signal |
| `intel_youtube` | YouTube channel RSS from voice registry | ai_signal |
| `intel_anthropic` | Platform notes + Claude app notes + anthropic.com/news | ai_signal |
| `intel_news` | Google News RSS — mainstream AI headlines (last 24h) | ai_signal |

### Scoring Algorithm (Deterministic, Not LLM)

All trend scoring uses a deterministic algorithm — no LLM guessing. Both pain-point and AI-signal streams use the same formula.

**Momentum (0–100)** — Is this trend real?

```
momentum = source_breadth(30) + engagement(30) + volume(20) + recency(20)
```

| Factor | Max | Formula |
|--------|-----|---------|
| Source breadth | 30 | `unique_sources × 5` (capped at 30) |
| Engagement | 30 | `sum(capped_scores) / 10` — per-signal cap of 50 |
| Volume | 20 | `signal_count × 2` (capped at 20) |
| Recency | 20 | `20 - (avg_age_hours / 2.4)` — decays over 48h |

**Noise (0–100)** — Is it hype or substance?

```
noise = low_engagement(35) + source_concentration(35) + title_similarity(30)
```

| Factor | Max | Formula |
|--------|-----|---------|
| Low engagement ratio | 35 | `(signals with <5 pts / total) × 35` |
| Source concentration | 35 | `(max_from_one_source / total) × 35` |
| Title similarity | 30 | `(duplicate_titles / total) × 30` — trigram matching |

**Threshold:** `momentum ≥ 60 AND noise ≤ 50` → promoted to dashboard.

### Voice Registry

Tracked people organized by tier — controls what gets collected and how signals are categorized.

| Tier | Purpose | Signal Category |
|------|---------|----------------|
| Visionary | Where AI is going | ai_signal |
| Practitioner | What's working now | ai_signal |
| Buyer | What problems exist | pain_point |

Voices are managed via the Voices tab in the Intelligence Lab UI. Platforms: X, YouTube, Newsletter, Reddit. Soft-delete preserves historical signal links.

### Reply Drafter

Pain-point posts have a **Draft Reply** button. Claude generates a technically specific, non-salesy response — no GraceZero mention, no links — consistent with a "be the most helpful person in the thread" positioning strategy.

### Intelligence Lab UI Tabs

- **Pain Points** — high-momentum pain signals with momentum/noise scores and Draft Reply
- **AI Signals** — emerging capability trends with source breadth and evidence
- **Opportunities** — synthesized leads in a pipeline (Signal → Researched → Pitched → Won → Dismissed)
- **Voices** — voice registry management
- **Digest** — summary of top trends and active opportunities

---

## How We Operate — IT Service Management

GraceZero AI follows industry-standard IT service management practices adapted for a lean engineering organization.

### Frameworks & Standards

| Standard | How We Apply It |
|----------|----------------|
| **ITIL v4** | Service lifecycle management — incident, problem, change, and release management processes |
| **NIST Cybersecurity Framework** | Identify, Protect, Detect, Respond, Recover — applied to all infrastructure decisions |
| **ISO/IEC 27001** | Information security management principles — access control, encryption, audit trails |
| **OWASP Top 10** | Application security baseline — all code reviewed against OWASP before deployment |
| **SemVer** | Semantic versioning for all releases — MAJOR.MINOR.PATCH with tagged releases |
| **12-Factor App** | Configuration in environment, stateless processes, disposable containers |

---

## Change Management Process

Every change to production follows a structured workflow. No cowboy deployments.

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Notion    │────▶│   Linear    │────▶│  Code Review │────▶│   Deploy    │
│  (Planning) │     │  (Tracking) │     │  (GitHub)    │     │  (Docker)   │
└─────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
       │                  │                    │                     │
  Requirements       Issue created        PR created            Docker build,
  & design docs      with RFC,            with type checks,     Traefik TLS,
  in Notion           priority,            lint, visual QA       health check
  workspace           labels,                                    verification,
                      project link                               image tag
                                                                 policy enforced
```

### 1. Planning & Requirements (Notion)

- Product requirements and Architecture Decision Records documented in Notion
- Runbooks for all operational procedures
- Design specs before implementation begins

### 2. Issue Tracking & RFCs (Linear)

- All work tracked in **Linear** (GraceZero team, project-based)
- **RFC process** for non-trivial changes — document the what, why, alternatives considered, and implementation plan before writing code
- Issue types: Feature, Bug, RFC, Chore, Security
- Every commit references a Linear issue ID

### 3. Development & Review (GitHub)

- **Git flow**: Feature branches from master, PR-based review
- **Automated checks**: TypeScript type checking, ESLint, Prettier
- **Testing**: Playwright E2E smoke tests, Vitest unit tests, visual QA
- **Commit conventions**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- **Changelog**: Every code change logged in `CHANGELOG.md` in the same commit

### 4. Deployment (Docker + Traefik)

- **Containerized**: All applications run in Docker containers
- **Reverse proxy**: Traefik handles TLS termination, routing, and Let's Encrypt certificates
- **Zero-downtime**: Container recreation with `docker compose up -d`
- **Image tag policy**: Every deploy produces exactly two tags — `:latest` (mutable pointer) and `:<git-sha>` (immutable rollback artifact). No slug tags. Previous sha tag retained for one cycle as the rollback target.
- **Health verification**: Deploy only considered complete after `/api/health` returns 200
- **Environment isolation**: `.env` preserved across deploys; never overwritten by build process

---

## Monitoring & Observability (4-Layer Stack)

### Layer 1 — External Uptime (UptimeRobot)

- HTTP health checks every 5 minutes
- Monitors all public endpoints (`/api/health`)
- Email alerts on downtime
- 30-day uptime tracking with response time history

### Layer 2 — Error Tracking (Sentry)

- Server-side and client-side error capture
- Source maps for stack trace resolution
- 20% trace sampling, 100% replay on error
- Error grouping, assignment, and resolution tracking
- Real-time alerting on new error types
- Per-environment filtering (`SENTRY_ALLOWED_ENVIRONMENTS`) — dev/local noise excluded from ops dashboard
- Dismissal system: individual issues can be hidden from Hopper Ops display without touching Sentry history

### Layer 3 — Infrastructure Health (Custom Scripts)

10-check infrastructure monitor running every 15 minutes via cron, emailing alerts on threshold breach:

| Check | Threshold | Alert Condition |
|-------|-----------|-----------------|
| Disk usage | 85% | Approaching capacity |
| Database size | 500MB | Abnormal growth |
| Backup freshness | 25 hours | Missed backup window |
| Backup size anomaly | 50% variance | Data corruption indicator |
| Container status | Any down | Service outage |
| Container restarts | Any restart | Stability issue |
| Memory usage | 512MB per container | Memory leak |
| Session count | 10,000 | Session store bloat |
| Error rate | 10/hour | Application health |
| Auth failures | 50/hour | Brute force attempt |

### Layer 4 — Hopper Ops (Operational Intelligence)

The dashboard itself — aggregating all monitoring data into a single view:

- **Anthropic platform status** — real-time from status.claude.com
- **Sentry integration** — unresolved issues with first/last seen, occurrence counts, direct Sentry links; dismissed issues tracked separately
- **Docker container metrics** — CPU, memory, network I/O, restart count, uptime per container
- **Slow query tracking** — top queries by execution time via `pg_stat_statements`
- **Dependency lifecycle** — EOL dates for every component in the stack
- **Risk register** — categorized, prioritized, with status tracking
- **SBOM** — complete inventory with daily diffs
- **Daily brief** — automated summary with rolling archive (last 3 briefs), inline HTML viewer, and forward capability

---

## Security Posture

### Authentication & Authorization

| Control | Implementation |
|---------|---------------|
| Authentication | Google OAuth 2.0 |
| Session management | Server-side sessions, 7-day expiry, secure cookies |
| CSRF protection | Double-submit cookie pattern (XSRF-TOKEN) |
| Rate limiting | Auth: 20 req/15 min, API: 100 req/min |
| Input validation | Pydantic models (Python), TypeScript strict mode |
| SQL injection | Parameterized queries only (`$1, $2, $3`) |
| XSS prevention | CSP headers, output escaping |
| Secrets management | Environment variables, never in code or git |

### Infrastructure Security

| Control | Status |
|---------|--------|
| TLS/SSL | Let's Encrypt via Traefik, auto-renewal |
| SSH | Key-only authentication, no password auth |
| Firewall | UFW active, allow 22/80/443 only |
| Dependency scanning | SBOM tracked in Hopper Ops, EOL alerts automated |
| Backup | Daily automated pg_dump, rolling 10-snapshot retention |
| Fail2ban | Active, banning repeated SSH failures |

### Incident Response

1. **Detection** — UptimeRobot alert + Sentry notification + monitor.sh email
2. **Triage** — Hopper Ops dashboard for at-a-glance severity assessment
3. **Response** — Runbooks in Notion for common scenarios
4. **Resolution** — Fix deployed, risk item updated in Hopper Ops
5. **Post-mortem** — Documented in Linear issue, CHANGELOG updated

---

## Risk Management

### Risk Categories

| Category | Description | Example |
|----------|-------------|---------|
| **EOL** | Component approaching end-of-life | Node.js 20 → 22 upgrade |
| **Security** | Vulnerability or exposure | Flask agents bound to 0.0.0.0 (remediated) |
| **Deprecation** | API/model being sunset | Pinned model strings needing update |
| **Drift** | Configuration divergence | Unaudited model strings in agent code |
| **Compliance** | Standard not met | Missing SBOM documentation |

### Risk Scoring

| Level | Criteria | Action |
|-------|----------|--------|
| Critical (Red) | < 30 days to EOL, active vulnerability, service down | Immediate remediation |
| Warning (Yellow) | < 365 days to EOL, non-critical finding, plan needed | Schedule this quarter |
| Healthy (Green) | Current, patched, compliant | Monitor only |

---

## Software Bill of Materials (SBOM)

Hopper Ops maintains a complete SBOM covering:

- **Infrastructure**: OS, database, runtime, proxy, container engine
- **SDKs**: Anthropic client libraries (npm + pip)
- **Services**: All deployed applications and their versions
- **Model strings**: AI model identifiers with deprecation tracking
- **Data sources**: endoflife.date API for automated EOL checking

Each component is tracked with current version, EOL date, days remaining, risk level, which project uses it, and last-verified date.

---

## Daily Operations Brief

Every morning, an automated n8n workflow:

1. Triggers all 12 core data collection modules
2. Aggregates results into a compiled brief
3. Emails the summary to the operations team
4. Stores a snapshot in the brief archive (rolling last 3)

Brief sections:
- Anthropic platform status + recent incidents
- Claude Code releases + model deprecation alerts
- Stack health (EOL countdown per component)
- API and app release notes (AI-summarized)
- Industry news digest (AI-curated)
- Prioritized action items

**Brief archives:** Last 3 briefs are retained in the database with inline HTML viewer and one-click forward to any email address.

---

## Technology Lifecycle Management

```
  Discovery          Assessment          Planning           Execution          Verification
 ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
 │ Hopper   │─────▶│ Risk     │─────▶│ RFC in   │─────▶│ Branch,  │─────▶│ Test,    │
 │ Ops      │      │ Register │      │ Linear   │      │ Code,    │      │ Deploy,  │
 │ detects  │      │ entry    │      │ with     │      │ Review   │      │ Verify   │
 │ EOL      │      │ created  │      │ plan     │      │          │      │          │
 └──────────┘      └──────────┘      └──────────┘      └──────────┘      └──────────┘
```

**Example: Node.js 20 → 22 Upgrade**

1. Hopper Ops flagged Node.js 20 EOL (April 30, 2026) — 26 days remaining
2. Risk item auto-created in risk register (red, critical)
3. RFC created in Linear with upgrade plan
4. Dockerfiles updated, tested on QA environment
5. Full Playwright suite passed on QA
6. Deployed to production, 24-hour soak period monitored
7. Risk item resolved, SBOM updated to Node.js 22

Total time from detection to resolution: **1 business day**

---

## Screenshots

### Dashboard
At-a-glance view: Anthropic platform status, risk summary, open action items, module health, and recent updates.

### SBOM
Complete software inventory with versions, EOL dates, days remaining, risk badges, and project assignments.

### Monitoring
Single pane of glass: UptimeRobot uptime/response times, Sentry error tracking, Docker container metrics, and slow query stats.

### Risk Register
Sortable, filterable risk table with inline status management. Color-coded by severity.

### Intelligence Lab
Multi-tab market intelligence view: Pain Points with momentum/noise scores, AI Signals, Opportunity pipeline, Voice registry, and Digest.

---

## Contact

**GraceZero AI** — Engineering operations powered by Claude

Built with FastAPI, React, PostgreSQL, and Claude (Haiku 4.5 + Sonnet 4.6).
