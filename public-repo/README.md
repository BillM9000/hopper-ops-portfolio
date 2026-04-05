# Hopper Ops — Operational Intelligence Platform

**Technology Risk Register | SBOM Management | Infrastructure Monitoring**

Hopper Ops is a purpose-built operational intelligence dashboard that serves as the single source of truth for GraceZero AI's infrastructure state, technology lifecycle management, and risk posture. It replaces scattered manual checks with a unified, automated system that runs 12 data collection modules, surfaces risks, and delivers a daily operational brief.

Named for **Grace Hopper** — Navy rear admiral, computer science pioneer — and the concept of a hopper: a funnel that processes raw operational signals into refined, actionable intelligence.

---

## Architecture

```
                        ┌──────────────────────────────────────┐
                        │          Hopper Ops                   │
                        │    hopperops.gracezero.ai             │
                        │                                       │
   ┌──────────┐         │  ┌────────────┐   ┌──────────────┐  │
   │ n8n Cron │────────▶│  │  Module    │──▶│  PostgreSQL  │  │
   │ (6 AM)   │         │  │  Runner    │   │  (8 tables)  │  │
   └──────────┘         │  │  (12 mods) │   └──────┬───────┘  │
                        │  └────────────┘          │           │
                        │         │                │           │
                        │  ┌──────▼────────────────▼────────┐ │
                        │  │   FastAPI API Layer             │ │
                        │  │   /api/status, /risks, /sbom    │ │
                        │  │   /monitoring, /brief, /feed    │ │
                        │  └──────────────┬─────────────────┘ │
                        │                 │                    │
                        │  ┌──────────────▼─────────────────┐ │
                        │  │   React Dashboard               │ │
                        │  │   7 pages, dark theme            │ │
                        │  └────────────────────────────────┘ │
                        │                                       │
                        │  ┌────────────────────────────────┐  │
                        │  │   Outputs                       │  │
                        │  │   → Daily email brief (6 AM)    │  │
                        │  │   → CLAUDE.md webhook           │  │
                        │  │   → PDF risk register export    │  │
                        │  └────────────────────────────────┘  │
                        └──────────────────────────────────────┘

  External Data Sources:
  ├── Anthropic Status API (status.claude.com)
  ├── GitHub Releases (claude-code atom feed)
  ├── endoflife.date API (stack EOL tracking)
  ├── UptimeRobot API (uptime + response times)
  ├── Sentry API (error tracking + issue counts)
  └── Claude API (Haiku 4.5 for editorial modules)
```

### Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12), asyncpg |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Database | PostgreSQL 16 |
| Auth | Google OAuth 2.0 (single-admin) |
| LLM | Anthropic Claude Haiku 4.5 (editorial modules) |
| Infrastructure | Docker, Traefik (TLS), Ubuntu 24.04 LTS |
| Monitoring | UptimeRobot, Sentry, custom health scripts |

---

## How We Operate — IT Service Management

GraceZero AI follows industry-standard IT service management practices adapted for a lean engineering organization. This section documents our operational framework, tooling, and processes.

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
  Requirements       Issue created        PR created            Automated
  & design docs      with RFC,            with tests,           Docker build,
  in Notion           priority,            type checks,          Traefik TLS,
  workspace           labels,              lint, visual QA       health check
                      project link                               verification
```

### 1. Planning & Requirements (Notion)

- Product requirements documented in Notion workspace
- Architecture Decision Records (ADRs) for significant technical choices
- Runbooks for operational procedures
- Design specs with mockups before implementation begins

### 2. Issue Tracking & RFCs (Linear)

- All work tracked in **Linear** (GraceZero team, project-based)
- **RFC process** for non-trivial changes — document the what, why, alternatives considered, and implementation plan before writing code
- Issue types: Feature, Bug, RFC, Chore, Security
- Priority levels: Urgent, High, Normal, Low
- Every commit references a Linear issue ID (e.g., `TOP-69`)

### 3. Development & Review (GitHub)

- **Git flow**: Feature branches from master, PR-based review
- **Automated checks**: TypeScript type checking, ESLint, Prettier
- **Testing**: Playwright E2E (215+ tests), Vitest unit tests, visual QA
- **Commit conventions**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- **Changelog**: Every code change logged in CHANGELOG.md in the same commit

### 4. Deployment (Docker + Traefik)

- **Containerized**: All applications run in Docker containers
- **Reverse proxy**: Traefik handles TLS termination, routing, and Let's Encrypt certificates
- **Zero-downtime**: Container recreation with `docker compose up -d`
- **Environment isolation**: Separate containers for production and QA
- **Golden backups**: Database snapshots taken before every major change

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

### Layer 3 — Infrastructure Health (Custom Scripts)

10-check infrastructure monitor running every 15 minutes:

| Check | Threshold | Alert Condition |
|-------|-----------|-----------------|
| Disk usage | 85% | Approaching capacity |
| Database size | 500MB | Abnormal growth |
| Backup freshness | 25 hours | Missed backup window |
| Backup size anomaly | 50% variance | Data corruption indicator |
| Container status | Any down | Service outage |
| Container restarts | Any restart | Stability issue |
| Memory usage | 256MB per container | Memory leak |
| Session count | 10,000 | Session store bloat |
| Error rate | 10/hour | Application health |
| Auth failures | 50/hour | Brute force attempt |

### Layer 4 — Hopper Ops (Operational Intelligence)

The dashboard itself — aggregating all monitoring data into a single view:

- **Anthropic platform status** — real-time from status.claude.com
- **Dependency lifecycle tracking** — EOL dates for every component in the stack
- **Risk register** — categorized, prioritized, with status tracking
- **SBOM (Software Bill of Materials)** — complete inventory of all dependencies
- **Daily brief** — automated summary emailed at 6 AM

---

## Security Posture

### Authentication & Authorization

| Control | Implementation |
|---------|---------------|
| Authentication | Google OAuth 2.0 with PKCE |
| Session management | Server-side sessions, 7-day expiry, secure cookies |
| CSRF protection | Double-submit cookie pattern (XSRF-TOKEN) |
| Rate limiting | Auth: 20 req/15 min, API: 100 req/min |
| Input validation | Zod schemas (TypeScript), Pydantic models (Python) |
| SQL injection | Parameterized queries only (`$1, $2, $3`) |
| XSS prevention | CSP headers, output escaping |
| Secrets management | Environment variables, never in code or git |

### Infrastructure Security

| Control | Status |
|---------|--------|
| TLS/SSL | Let's Encrypt via Traefik, auto-renewal |
| SSH | Key-only authentication, no password auth |
| Firewall | UFW active, allow 22/80/443 only |
| Container isolation | Non-root users, read-only mounts where possible |
| Dependency scanning | SBOM tracked in Hopper Ops, EOL alerts automated |
| Backup encryption | Daily automated backups, rolling 10-day retention |
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
| **EOL** | Component approaching end-of-life | Node.js 20 → 22 upgrade (completed) |
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

Each component is tracked with:
- Current version
- EOL date (from endoflife.date or manual entry)
- Days remaining until EOL
- Risk level (red/yellow/green)
- Which project uses it
- Last verified date

---

## Daily Operations Brief

Every morning at 6:00 AM CST, an automated workflow:

1. **Triggers** all 12 data collection modules
2. **Aggregates** results into a compiled brief
3. **Emails** the summary to the operations team
4. **Surfaces** critical items that need immediate attention

Brief sections:
- Anthropic platform status
- Recent incidents (last 7 days)
- Claude Code releases
- Model deprecation alerts
- Stack health (EOL countdown)
- API and app release notes (AI-summarized)
- Industry news digest (AI-curated)
- Prioritized action items

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
3. RFC created in Linear (TOP-61) with upgrade plan
4. Dockerfiles updated, tested on QA environment
5. Full Playwright suite (217 tests) passed on QA
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
Single pane of glass: UptimeRobot uptime/response times, Sentry error tracking, and VPS health checks — all in one view.

### Risk Register
Sortable, filterable risk table with inline status management. Color-coded by severity.

---

## Contact

**GraceZero AI** — Engineering operations powered by Claude

Built with FastAPI, React, PostgreSQL, and Claude Haiku 4.5.
