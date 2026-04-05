"""Risk register endpoints"""

from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException
from server import database as db
from server.models import RiskUpdate

router = APIRouter()


@router.get("/risks")
async def get_risks(
    risk_level: str = Query(None),
    category: str = Query(None),
    status: str = Query(None),
):
    where_clauses = []
    params = []
    idx = 1

    if risk_level:
        where_clauses.append(f"risk_level = ${idx}")
        params.append(risk_level)
        idx += 1

    if category:
        where_clauses.append(f"category = ${idx}")
        params.append(category)
        idx += 1

    if status:
        where_clauses.append(f"status = ${idx}")
        params.append(status)
        idx += 1

    where = ""
    if where_clauses:
        where = "WHERE " + " AND ".join(where_clauses)

    rows = await db.fetch(
        f"""SELECT r.*, c.name as component_name, c.current_version
            FROM risk_items r
            LEFT JOIN components c ON r.component_id = c.id
            {where}
            ORDER BY
              CASE risk_level WHEN 'red' THEN 1 WHEN 'yellow' THEN 2 ELSE 3 END,
              deadline ASC NULLS LAST""",
        *params,
    )

    from datetime import date
    today = date.today()
    for row in rows:
        if row.get("deadline"):
            row["days_remaining"] = (row["deadline"] - today).days
        else:
            row["days_remaining"] = None

    return {"risks": rows, "total": len(rows)}


@router.get("/risks/{risk_id}")
async def get_risk(risk_id: int):
    row = await db.fetchrow(
        """SELECT r.*, c.name as component_name, c.current_version
           FROM risk_items r
           LEFT JOIN components c ON r.component_id = c.id
           WHERE r.id = $1""",
        risk_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Risk item not found")
    return row


@router.patch("/risks/{risk_id}")
async def update_risk(risk_id: int, update: RiskUpdate):
    existing = await db.fetchrow("SELECT id FROM risk_items WHERE id = $1", risk_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Risk item not found")

    sets = []
    params = []
    idx = 1

    if update.status:
        sets.append(f"status = ${idx}")
        params.append(update.status)
        idx += 1
        if update.status == "resolved":
            sets.append(f"resolved_at = ${idx}")
            params.append(datetime.now(timezone.utc))
            idx += 1

    if update.risk_level:
        sets.append(f"risk_level = ${idx}")
        params.append(update.risk_level)
        idx += 1

    if not sets:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(risk_id)
    await db.execute(
        f"UPDATE risk_items SET {', '.join(sets)} WHERE id = ${idx}",
        *params,
    )

    return await get_risk(risk_id)
