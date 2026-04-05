"""Status endpoint — at-a-glance system overview"""

from fastapi import APIRouter
from server import database as db

router = APIRouter()


@router.get("/status")
async def get_status():
    # Get latest system_status module run
    latest_status = await db.fetchrow(
        """SELECT result_data, ran_at FROM module_runs
           WHERE module_name = 'system_status' AND success = TRUE
           ORDER BY ran_at DESC LIMIT 1"""
    )

    # Risk summary
    risk_summary = await db.fetch(
        """SELECT risk_level, COUNT(*) as count FROM risk_items
           WHERE status != 'resolved'
           GROUP BY risk_level"""
    )

    # Action summary
    action_summary = await db.fetch(
        """SELECT status, COUNT(*) as count FROM action_items
           GROUP BY status"""
    )

    # Last refresh time
    last_refresh = await db.fetchval(
        "SELECT MAX(ran_at) FROM module_runs"
    )

    # Module run statuses
    modules = await db.fetch(
        """SELECT DISTINCT ON (module_name) module_name, success, ran_at, duration_ms, error_message
           FROM module_runs ORDER BY module_name, ran_at DESC"""
    )

    import json
    anthropic_data = latest_status["result_data"] if latest_status else {}
    if isinstance(anthropic_data, str):
        try:
            anthropic_data = json.loads(anthropic_data)
        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "anthropic_status": anthropic_data,
        "risk_summary": {r["risk_level"]: r["count"] for r in risk_summary},
        "action_summary": {a["status"]: a["count"] for a in action_summary},
        "last_refresh": last_refresh,
        "modules": [dict(m) for m in modules],
    }
