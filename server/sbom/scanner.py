"""SBOM Scanner — collects software inventory from the local system"""

import json
import subprocess
import re
from datetime import datetime, timezone
from server import database as db


# Seed data from the VPS audit (2026-04-04)
SEED_COMPONENTS = [
    # Infrastructure
    {"name": "ubuntu", "category": "infrastructure", "current_version": "24.04.4", "eol_date": "2029-04-01", "eol_source": "manual", "risk_level": "green", "project": None},
    {"name": "postgresql", "category": "infrastructure", "current_version": "16.13", "eol_date": "2028-11-01", "eol_source": "manual", "risk_level": "green", "project": None},
    {"name": "python", "category": "infrastructure", "current_version": "3.12.3", "eol_date": "2028-10-01", "eol_source": "manual", "risk_level": "green", "project": None},
    {"name": "nodejs", "category": "infrastructure", "current_version": "22.22.2", "eol_date": "2027-04-30", "eol_source": "endoflife.date", "risk_level": "green", "project": None, "notes": "Upgraded from Node 20 on 2026-04-05"},
    {"name": "docker-engine", "category": "infrastructure", "current_version": "29.3.0", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": None},
    {"name": "docker-compose", "category": "infrastructure", "current_version": "5.1.0", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": None},

    # Web / Proxy
    {"name": "traefik", "category": "infrastructure", "current_version": "3.6.9", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": None},
    {"name": "nginx", "category": "infrastructure", "current_version": "1.24.0", "eol_date": None, "eol_source": "manual", "risk_level": "yellow", "project": None, "notes": "Legacy — only serves one domain"},
    {"name": "certbot", "category": "infrastructure", "current_version": "2.9.0", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": None},

    # Anthropic SDKs
    {"name": "@anthropic-ai/sdk", "category": "sdk", "current_version": "0.78.0", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": "traillog"},
    {"name": "anthropic-python", "category": "sdk", "current_version": "0.79.0", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": "escapevelocity"},

    # Services / Apps
    {"name": "n8n", "category": "service", "current_version": "2.10.3", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": "n8n"},
    {"name": "traillog", "category": "service", "current_version": "0.2.1", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": "traillog"},

    # Model strings
    {"name": "claude-sonnet-4-6", "category": "anthropic", "current_version": "current", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": "traillog"},
    {"name": "claude-haiku-4-5-20251001", "category": "anthropic", "current_version": "current", "eol_date": None, "eol_source": "manual", "risk_level": "green", "project": "traillog"},
    {"name": "claude-sonnet-4-20250514", "category": "anthropic", "current_version": "pinned", "eol_date": None, "eol_source": "manual", "risk_level": "yellow", "project": "traillog", "notes": "Older pinned version in gear routes — update to current"},
]

# Known risk items from the VPS audit
SEED_RISKS = [
    {
        "title": "Nginx legacy — only serves one domain",
        "description": "Nginx on host only serves one domain. Certbot only manages that one cert. Consolidate into Traefik or document exception.",
        "risk_level": "yellow",
        "category": "other",
        "status": "open",
    },
    {
        "title": "Old pinned model string: claude-sonnet-4-20250514",
        "description": "Older pinned version in traillog gear routes. Update to claude-sonnet-4-6.",
        "risk_level": "yellow",
        "category": "deprecation",
        "status": "open",
    },
    {
        "title": "EscapeVelocity model strings not fully audited",
        "description": "Python agent model strings not fully audited. Scan all .py files for model string usage.",
        "risk_level": "yellow",
        "category": "drift",
        "status": "open",
    },
    {
        "title": "MPF Dashboard — no git remote",
        "description": "Single copy on server with no backup repo. Push to GitHub or set up a remote.",
        "risk_level": "yellow",
        "category": "other",
        "status": "open",
    },
]

SEED_ACTIONS = [
    {
        "title": "Update claude-sonnet-4-20250514 to current model string",
        "description": "In traillog gear routes, replace pinned version with claude-sonnet-4-6",
        "priority": "medium",
        "source_module": "model_deprecations",
    },
    {
        "title": "Audit EscapeVelocity model strings",
        "description": "Scan all .py files in EscapeVelocity for hardcoded model names",
        "priority": "medium",
        "source_module": "model_deprecations",
    },
    {
        "title": "Push MPF Dashboard to GitHub",
        "description": "Currently has no remote — single copy on server",
        "priority": "low",
        "source_module": "risk_scorer",
    },
    {
        "title": "Consolidate Nginx into Traefik",
        "description": "Move remaining domain from Nginx to Traefik, or document the exception",
        "priority": "low",
        "source_module": "risk_scorer",
    },
]


async def seed_sbom():
    """Seed the database with initial SBOM data from the VPS audit."""
    from datetime import date as date_type

    for comp in SEED_COMPONENTS:
        eol = None
        if comp.get("eol_date"):
            eol = date_type.fromisoformat(comp["eol_date"])

        await db.execute(
            """INSERT INTO components (name, category, current_version, eol_date, eol_source, risk_level, project, notes, last_checked_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
               ON CONFLICT (name, project) DO UPDATE SET
                 current_version = EXCLUDED.current_version,
                 eol_date = EXCLUDED.eol_date,
                 risk_level = EXCLUDED.risk_level,
                 notes = EXCLUDED.notes,
                 last_checked_at = NOW()""",
            comp["name"], comp["category"], comp["current_version"],
            eol, comp.get("eol_source"), comp["risk_level"],
            comp.get("project"), comp.get("notes"),
        )

    # Seed risk items
    for risk in SEED_RISKS:
        await db.execute(
            """INSERT INTO risk_items (title, description, risk_level, category, status)
               VALUES ($1, $2, $3, $4, $5)
               ON CONFLICT DO NOTHING""",
            risk["title"], risk["description"], risk["risk_level"],
            risk["category"], risk["status"],
        )

    # Seed action items
    for action in SEED_ACTIONS:
        await db.execute(
            """INSERT INTO action_items (title, description, priority, source_module, status)
               VALUES ($1, $2, $3, $4, 'open')
               ON CONFLICT DO NOTHING""",
            action["title"], action["description"], action["priority"],
            action["source_module"],
        )

    # Create initial SBOM snapshot
    snapshot_data = {
        "components": [
            {"name": c["name"], "version": c["current_version"], "category": c["category"]}
            for c in SEED_COMPONENTS
        ],
        "scan_date": str(datetime.now(timezone.utc)),
    }

    await db.execute(
        """INSERT INTO sbom_snapshots (snapshot_date, data)
           VALUES (CURRENT_DATE, $1::jsonb)
           ON CONFLICT DO NOTHING""",
        json.dumps(snapshot_data),
    )
