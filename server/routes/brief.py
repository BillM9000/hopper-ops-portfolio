"""Daily brief endpoints"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from server import database as db

router = APIRouter()


@router.get("/brief")
async def get_brief():
    """Compiled daily brief (JSON) from latest module runs."""
    modules = await db.fetch(
        """SELECT DISTINCT ON (module_name) module_name, result_data, brief_text, ran_at, success
           FROM module_runs
           ORDER BY module_name, ran_at DESC"""
    )

    sections = {}
    for mod in modules:
        sections[mod["module_name"]] = {
            "brief_text": mod["brief_text"],
            "ran_at": mod["ran_at"],
            "success": mod["success"],
            "data": mod["result_data"],
        }

    # Recent actions
    actions = await db.fetch(
        """SELECT title, priority, status FROM action_items
           WHERE status IN ('open', 'in_progress')
           ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
           LIMIT 10"""
    )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": sections,
        "action_items": [dict(a) for a in actions],
    }


@router.get("/brief/text")
async def get_brief_text():
    """Plain text brief for CLAUDE.md consumption."""
    modules = await db.fetch(
        """SELECT DISTINCT ON (module_name) module_name, brief_text, ran_at, success
           FROM module_runs
           ORDER BY module_name, ran_at DESC"""
    )

    lines = [
        f"## HOPPER OPS BRIEF — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    section_order = [
        ("system_status", "SYSTEM STATUS"),
        ("incidents_recent", "RECENT INCIDENTS"),
        ("claude_code_releases", "CLAUDE CODE RELEASES"),
        ("model_deprecations", "MODEL DEPRECATIONS"),
        ("stack_eol_check", "STACK HEALTH"),
        ("sbom_diff", "SBOM CHANGES"),
        ("risk_scorer", "RISK SUMMARY"),
        ("api_release_notes", "API CHANGES"),
        ("app_release_notes", "APP UPDATES"),
        ("news_digest", "NEWS"),
        ("interesting_finds", "INTERESTING FINDS"),
        ("action_items_synthesis", "SYNTHESIZED ACTIONS"),
    ]

    module_map = {m["module_name"]: m for m in modules}

    for mod_name, heading in section_order:
        mod = module_map.get(mod_name)
        if mod and mod["success"] and mod["brief_text"]:
            lines.append(f"**{heading}:** {mod['brief_text']}")
            lines.append("")

    # Action items
    actions = await db.fetch(
        """SELECT title, priority FROM action_items
           WHERE status IN ('open', 'in_progress')
           ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END
           LIMIT 10"""
    )

    if actions:
        lines.append("**ACTION ITEMS:**")
        for a in actions:
            marker = "!!!" if a["priority"] == "critical" else "!" if a["priority"] == "high" else "-"
            lines.append(f"  {marker} [{a['priority'].upper()}] {a['title']}")
        lines.append("")

    return PlainTextResponse("\n".join(lines))
