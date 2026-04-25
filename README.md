# Hopper Ops — Operational Intelligence Platform

**Technology Risk Register | SBOM Management | Infrastructure Monitoring | Market Intelligence**

Hopper Ops is a purpose-built operational intelligence dashboard that serves as the single source of truth for GraceZero AI's infrastructure state, technology lifecycle management, and risk posture. It replaces scattered manual checks with a unified, automated system that runs **26 data collection modules across two pipelines** — a 14-module core operations pipeline and a 12-module AI-powered market intelligence pipeline — surfaces risks, and delivers a daily operational brief.

Named for **Grace Hopper** — Navy rear admiral, computer science pioneer — and the concept of a hopper: a funnel that processes raw operational signals into refined, actionable intelligence.

**Live:** [hopperops.gracezero.ai](https://hopperops.gracezero.ai) | **Public Repo:** [github.com/BillM9000/hopper-ops-portfolio](https://github.com/BillM9000/hopper-ops-portfolio)

---

## What It Does

- **Technology risk register** — auto-scored risks across every app in the stack (EOL, security, deprecation, drift)
- **SBOM (Software Bill of Materials)** — full component inventory with EOL countdown, daily diff, and a cross-project scanner that walks every codebase looking for pinned AI model strings
- **Infrastructure monitoring** — single pane of glass: UptimeRobot uptime, Sentry errors with environment-aware filtering, Docker container health, slow-query tracking via `pg_stat_statements`
- **Daily brief** — automated email every morning compiling status, incidents, Claude Code releases, model deprecations, and AI-summarized news; archives last 3 briefs with inline viewer and one-click forward
- **Market intelligence pipeline (Intelligence Lab)** — multi-source signal collection across 10 sources, deterministic scoring, two-pass LLM trend detection, and adversarial cross-stream opportunity synthesis

---

## What's Not in the Average Operations Dashboard

Most ops dashboards are uptime monitors, log aggregators, or APM tools. Hopper Ops is none of them. Six things make it unusual:

### 1. AI model deprecations tracked as supply-chain components

Most teams hardcode `claude-3-5-sonnet-20241022` somewhere in a config and find out it's deprecated when production breaks. In Hopper Ops, model strings are first-class SBOM components with countdown timers. A **cross-project scanner** walks every codebase under `~/GraceZero.ai.local/` looking for pinned model IDs and flags them in the risk register before the deprecation deadline.

### 2. Adversarial AI synthesis — the LLM has to argue against itself

Every opportunity the Intelligence Lab generates has a forced `why_this_might_not_work` field. The synthesizer cannot publish a recommendation without first articulating the case against it. This cuts AI optimism bias substantially — opportunities that survive the falsification step are the ones worth pursuing.

### 3. ICP disqualifications baked into the synthesis prompt

The opportunity synthesizer runs against an explicit "WHAT WE WILL NOT PURSUE" block in the prompt. It cannot propose pitching anything HubSpot, Zapier, GoHighLevel, Make.com, or Salesforce already ships at <$200/mo. It cannot propose ideas requiring sales channels we don't have. The discipline that's normally a human gate is encoded into the model's instructions.

### 4. Two pipelines, one platform

Operational monitoring AND market intelligence on the same dashboard, same database, same auth. Either is a product on its own. Together they're a posture: monitor what's running, watch what the market wants next, surface both in a single morning brief.

### 5. 80-phrase pain classifier across all 10 collectors

Most "social listening" tools detect complaints on Reddit only. The Hopper Ops pain classifier scans every collected signal — HN comments, X complaint queries, blog posts, GitHub issues, RSS, news — against an **80-phrase taxonomy** organized into 8 categories (time/cost quantifiers, frustration language, workaround patterns, reliability failures, pricing complaints, capacity pain, switching language, gap-naming). Two distinct matches promote the signal to `pain_point`. One-off mentions are ignored.

### 6. Persistence-aware trend detection (not churn-aware)

Trends carry a `title_key` (normalized hash) and a `(first_seen, last_seen, observation_count)` window. Re-detecting a trend the next day adds **+3 momentum** (capped at +12) — sustained signals get heavier. Archived trends don't block re-detection because the unique constraint is partial: `WHERE status='active'`. Most "trending" systems just refresh and lose continuity. This one accumulates evidence over time.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Hopper Ops                                │
│                    hopperops.gracezero.ai                           │
│                                                                     │
│   CORE PIPELINE                    INTELLIGENCE PIPELINE            │
│   ─────────────                    ─────────────────────            │
│   ┌──────────────┐                 ┌──────────────────┐             │
│   │ Module Runner│                 │ 10 Collectors    │             │
│   │ (14 modules) │                 │ HN, RSS, Reddit  │             │
│   │ 9 determ.    │                 │ X, X Voices      │             │
│   │ 5 LLM        │                 │ GitHub, Blogs    │             │
│   └──────┬───────┘                 │ YouTube, Anth.   │             │
│          │                         │ News             │             │
│          │                         └──────┬───────────┘             │
│          │                                │                         │
│          │               ┌────────────────▼──────────────┐          │
│          │               │ 2 Analyzers                   │          │
│          │               │ - Trend detector (Sonnet 4.6) │          │
│          │               │ - Opportunity synth (Opus 4.7)│          │
│          │               └────────────────┬──────────────┘          │
│          │                                │                         │
│   ┌──────▼────────────────────────────────▼────────────────────┐    │
│   │                   PostgreSQL (15 tables)                   │    │
│   └───────────────────────────┬────────────────────────────────┘    │
│                               │                                     │
│   ┌───────────────────────────▼────────────────────────────────┐    │
│   │                 FastAPI API Layer (35+ endpoints)          │    │
│   └───────────────────────────┬────────────────────────────────┘    │
│                               │                                     │
│   ┌───────────────────────────▼────────────────────────────────┐    │
│   │              React Dashboard (9 pages)                     │    │
│   │   Dashboard · Risk · SBOM · Actions · Feed · Monitoring    │    │
│   │   History · Intelligence Lab · Login                       │    │
│   └────────────────────────────────────────────────────────────┘    │
│                                                                     │
│   Outputs:  Daily email brief · Plain-text brief endpoint           │
└─────────────────────────────────────────────────────────────────────┘

External Sources:
├── Anthropic Status API (status.claude.com)
├── GitHub Releases (claude-code atom feed)
├── endoflife.date API (stack EOL tracking)
├── n8n GitHub releases (version drift tracking)
├── UptimeRobot API (uptime + response times)
├── Sentry API (error tracking + issue counts, environment-filtered)
├── Hacker News (top + Show HN + Ask HN + comment sweeping)
├── Reddit, X, GitHub Trending, AI Lab Blogs, RSS
├── YouTube (channel RSS), Google News RSS
└── Claude API (Haiku 4.5 — editorial; Sonnet 4.6 — Intel trends; Opus 4.7 — Intel synthesis)
```

### Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12), asyncpg |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL 16 (15 tables) |
| Auth | Google OAuth 2.0 (single-admin) |
| LLM | Claude Haiku 4.5 (editorial) · Claude Sonnet 4.6 (Intel trend detector) · **Claude Opus 4.7 (Intel synthesis — reasoning premium justified for high-stakes cross-stream output)** |
| Infrastructure | Docker, Traefik (TLS + Let's Encrypt), Ubuntu 24.04 LTS |
| Monitoring | UptimeRobot, Sentry, custom health scripts, pg_stat_statements |

---

## Core Operations Pipeline (14 Modules)

The core pipeline runs on schedule and on-demand, collecting and synthesizing operational data.

### Deterministic Modules (9)

| Module | Source | Output |
|--------|--------|--------|
| `system_status` | Anthropic Status API | Current platform health |
| `incidents_recent` | Anthropic Status API | Incidents in last 7 days |
| `claude_code_releases` | GitHub atom feed | Latest Claude Code versions |
| `model_deprecations` | Anthropic changelog | Deprecation alerts with countdown |
| `stack_eol_check` | endoflife.date API | EOL countdown per component |
| `n8n_version_check` | n8n GitHub releases | n8n version drift + risk reasoning |
| `sbom_diff` | DB snapshot comparison | Component changes since last run |
| `sentry_issues` | Sentry API (env-filtered) | Unresolved issues, dismissal-aware |
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
│             │     │  (Claude Sonnet)  │     │  (Claude Opus)   │
│  pain_point │     │                   │     │                  │
│  ai_signal  │     │  Pass 1: cluster  │     │  Cross pain pts  │
│  (labeled   │     │  pain points      │     │  with AI signals │
│  at ingest  │     │                   │     │                  │
│  by 80-phr. │     │  Pass 2: cluster  │     │  Output: pitch   │
│  classifier)│     │  AI signals       │     │  angle, market,  │
│             │     │                   │     │  gap, evidence   │
│             │     │  Persistence-     │     │  quotes, "why    │
│             │     │  aware: re-detect │     │  this might not  │
│             │     │  bonus +3 (cap 12)│     │  work" field     │
└─────────────┘     └───────────────────┘     └──────────────────┘
```

### Signal Collectors (10)

| Collector | Source | Auto-Category Logic |
|-----------|--------|---------------------|
| `intel_hn` | Hacker News top + Show HN + Ask HN + comment sweeping on Ask-HN and pain-flagged stories | pain_point (Ask-HN parentage or 80-phrase classifier match) |
| `intel_rss` | 10 curated AI/tech RSS feeds | pain_point (classifier) / ai_signal (default) |
| `intel_reddit` | **11 subreddits** — SaaS, n8n, automation, smallbusiness, devops, Entrepreneur, microsaas, nocode, SideProject, sweatystartup, EntrepreneurRideAlong | pain_point (buyer subs + classifier) |
| `intel_x` | X keyword search — **5 product-category terms + 6 complaint queries** ("sick of Zapier", "Make.com is broken", etc.) | pain_point (complaint queries pre-tagged + classifier on body) |
| `intel_x_voices` | X accounts from voice registry | by voice tier |
| `intel_github` | GitHub daily trending repos | pain_point (classifier) / ai_signal (default) |
| `intel_blogs` | AI lab blogs (Anthropic, OpenAI, Google, Meta, Mistral) | pain_point (classifier) / ai_signal (default) |
| `intel_youtube` | YouTube channel RSS from voice registry | pain_point (classifier) / ai_signal (default) |
| `intel_anthropic` | Platform notes + Claude app notes + anthropic.com/news | pain_point (classifier) / ai_signal (default) |
| `intel_news` | Google News RSS — mainstream AI headlines (last 24h) | pain_point (classifier) / ai_signal (default) |

### Pain Classifier (80 phrases, 8 categories, all 10 sources)

A shared classifier — `pain_classifier.py` — scans every collected signal's title and body against an 80-phrase taxonomy. **Two distinct matches** promote the signal to `pain_point`. Categories:

| Category | Sample phrases |
|----------|----------------|
| Help-seeking | "need help with", "looking for someone", "anyone built" |
| Time/cost quantifiers | "wasting hours", "hours per week", "full day lost" |
| Frustration / emotional | "sick of", "fed up with", "drives me crazy" |
| Workaround language | "manual process", "spreadsheet hell", "stuck doing" |
| Reliability failures | "flaky", "keeps breaking", "silently fails" |
| Pricing complaints | "too expensive", "ripoff", "killing my margin" |
| Capacity / scale | "can't scale", "rate limited", "doesn't handle" |
| Switching / gap-naming | "moving off", "wish there was", "the problem with" |

The two-match threshold prevents single stray mentions in AI-focused content from triggering false positives.

### Trend Scoring (Deterministic, Stream-Aware)

All trend scoring uses a deterministic algorithm — no LLM guessing.

**Momentum (0–100)** — Is this trend real?

```
momentum = source_breadth(30) + engagement(30) + volume(20) + recency(20)
```

| Factor | Max | Formula |
|--------|-----|---------|
| Source breadth | 30 | `unique_sources × 5` (capped at 30) — pain_point stream counts distinct subreddits as distinct channels |
| Engagement | 30 | `sum(capped_scores) / 10` × 1.5 multiplier on pain_point stream (complaints under-engage) |
| Volume | 20 | `signal_count × 2` (capped at 20) |
| Recency | 20 | `20 - (avg_age_hours / 3.0)` — softer decay over 48h window |

**Noise (0–100)** — Is it hype or substance?

```
noise = low_engagement(35) + source_concentration(35) + title_similarity(30)
```

| Factor | Max | Formula |
|--------|-----|---------|
| Low engagement ratio | 35 | `(signals with <5 pts / total) × 35` |
| Source concentration | 35 | `(max_from_one_source / total) × 35` |
| Title similarity | 30 | `(duplicate_titles / total) × 30` — trigram matching |

**Persistence bonus:** trends re-detected on subsequent runs accumulate `+3` momentum per re-detection, capped at `+12`. Sustained signals beat one-day spikes.

**Threshold:** `momentum ≥ 60 AND noise ≤ 50` → promoted to dashboard.

### Opportunity Synthesizer (Claude Opus 4.7)

The synthesizer takes the day's pain trends + AI-signal trends and produces opportunities — actionable pitches with structured fields:

- **Pitch angle** — what to sell, in one sentence
- **Target market** — who would buy this
- **Gap** — why this isn't already solved by an incumbent
- **Effort estimate** — buildable in days/weeks/months under GraceZero's ICP rules
- **Build-vs-wait** — ship now or wait for more signal
- **Evidence quotes (JSONB)** — grounded source quotes with URLs the LLM had to cite
- **Why this might not work** — adversarial falsification field; the synthesizer must argue against the recommendation before publishing it

The synthesis prompt has an explicit ICP disqualification block — opportunities are auto-rejected if a competitor already ships the same feature at <$200/mo, if it requires sales channels GraceZero doesn't have, if it needs capabilities GraceZero hasn't shipped before, or if the buyer can solve it with a $20 ChatGPT subscription plus 30 minutes of setup.

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
- **Memory drift guard**: pre-commit hook blocks commits when in-repo memory and Claude-Code-managed memory disagree
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
- **Per-environment filtering** (`SENTRY_ALLOWED_ENVIRONMENTS`) — dev/local noise excluded from ops dashboard at query time, never mutated in Sentry
- **Dismissal system**: individual issues can be hidden from Hopper Ops display without touching Sentry history

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
- **AI model deprecation tracking** — pinned model strings as supply-chain components with countdown timers
- **Risk register** — categorized, prioritized, with status tracking
- **SBOM** — complete inventory with daily diffs and cross-project model-string scanner
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
- **AI model strings**: model identifiers tracked as supply-chain components with deprecation deadlines
- **Data sources**: endoflife.date API for automated EOL checking; n8n GitHub releases for n8n version drift

Each component is tracked with current version, target version (when an upgrade is needed), risk reasoning, EOL date, days remaining, risk level, which project uses it, and last-verified date.

**Cross-project Claude model scanner** — walks every codebase under `~/GraceZero.ai.local/` looking for pinned model IDs (`claude-3-5-sonnet-20241022`, `claude-haiku-4-5-20251001`, etc.) and surfaces drift between code and SBOM. Catches the model string a developer pinned 6 months ago and forgot about.

---

## Daily Operations Brief

Every morning, an automated workflow:

1. Triggers all 14 core data collection modules
2. Aggregates results into a compiled brief
3. Emails the summary to the operations team
4. Stores a snapshot in the brief archive (rolling last 3)

Brief sections:
- Anthropic platform status + recent incidents
- Claude Code releases + model deprecation alerts
- Stack health (EOL countdown per component)
- API and app release notes (AI-summarized)
- Industry news digest (AI-curated)
- Prioritized action items (synthesized from all module data)

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
Complete software inventory with versions, target versions, risk reasoning, EOL dates, days remaining, risk badges, and project assignments.

### Monitoring
Single pane of glass: UptimeRobot uptime/response times, Sentry error tracking with environment filtering, Docker container metrics, and slow query stats.

### Risk Register
Sortable, filterable risk table with inline status management. Color-coded by severity.

### Intelligence Lab
Multi-tab market intelligence view: Pain Points with momentum/noise scores, AI Signals, Opportunity pipeline (with adversarial falsification + evidence quotes), Voice registry, and Digest.

---

## Contact

**GraceZero AI** — Engineering operations powered by Claude

Built with FastAPI, React, PostgreSQL, and Claude (Haiku 4.5 + Sonnet 4.6 + Opus 4.7).
