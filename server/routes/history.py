"""History endpoints — audit trail"""

from fastapi import APIRouter, Query
from server import database as db

router = APIRouter()


@router.get("/history")
async def get_history(limit: int = Query(50, le=200), offset: int = Query(0)):
    """Unified history view — module runs + component changes + risk updates."""

    # Module runs
    module_runs = await db.fetch(
        """SELECT id, module_name, module_type, ran_at, success, duration_ms, error_message,
                  'module_run' AS event_type
           FROM module_runs
           ORDER BY ran_at DESC LIMIT $1 OFFSET $2""",
        limit, offset,
    )

    # Scan history
    scans = await db.fetch(
        """SELECT id, scan_type, ran_at, changes_detected,
                  'scan' AS event_type
           FROM scan_history
           ORDER BY ran_at DESC LIMIT $1""",
        limit,
    )

    # Combine and sort
    events = [dict(r) for r in module_runs] + [dict(s) for s in scans]
    events.sort(key=lambda e: e.get("ran_at", ""), reverse=True)

    return {"events": events[:limit], "total": len(events)}
