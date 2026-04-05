"""Action items endpoints"""

from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException
from server import database as db
from server.models import ActionUpdate

router = APIRouter()


@router.get("/actions")
async def get_actions(
    status: str = Query(None),
    priority: str = Query(None),
):
    where_clauses = []
    params = []
    idx = 1

    if status:
        where_clauses.append(f"status = ${idx}")
        params.append(status)
        idx += 1

    if priority:
        where_clauses.append(f"priority = ${idx}")
        params.append(priority)
        idx += 1

    where = ""
    if where_clauses:
        where = "WHERE " + " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""SELECT * FROM action_items {where}
            ORDER BY
              CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END,
              created_at DESC""",
        *params,
    )

    return {"actions": rows, "total": len(rows)}


@router.patch("/actions/{action_id}")
async def update_action(action_id: int, update: ActionUpdate):
    existing = await db.fetchrow("SELECT id FROM action_items WHERE id = $1", action_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Action item not found")

    sets = []
    params = []
    idx = 1

    if update.status:
        sets.append(f"status = ${idx}")
        params.append(update.status)
        idx += 1
        if update.status == "done":
            sets.append(f"completed_at = ${idx}")
            params.append(datetime.now(timezone.utc))
            idx += 1

    if update.priority:
        sets.append(f"priority = ${idx}")
        params.append(update.priority)
        idx += 1

    if not sets:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(action_id)
    await db.execute(
        f"UPDATE action_items SET {', '.join(sets)} WHERE id = ${idx}",
        *params,
    )

    row = await db.fetchrow("SELECT * FROM action_items WHERE id = $1", action_id)
    return row
