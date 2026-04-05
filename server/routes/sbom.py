"""SBOM endpoints"""

from fastapi import APIRouter, Query
from server import database as db

router = APIRouter()


@router.get("/sbom")
async def get_sbom(
    category: str = Query(None),
    risk_level: str = Query(None),
    sort: str = Query("eol_date"),
):
    where_clauses = []
    params = []
    idx = 1

    if category:
        where_clauses.append(f"category = ${idx}")
        params.append(category)
        idx += 1

    if risk_level:
        where_clauses.append(f"risk_level = ${idx}")
        params.append(risk_level)
        idx += 1

    where = ""
    if where_clauses:
        where = "WHERE " + " AND ".join(where_clauses)

    # Validate sort column
    valid_sorts = {"eol_date", "name", "risk_level", "category", "updated_at"}
    if sort not in valid_sorts:
        sort = "eol_date"

    rows = await db.fetch(
        f"""SELECT id, name, category, current_version, eol_date, eol_source,
                   risk_level, project, notes, last_checked_at, created_at, updated_at
            FROM components {where}
            ORDER BY {sort} ASC NULLS LAST, name ASC""",
        *params,
    )

    # Add days_remaining calculation
    from datetime import date
    today = date.today()
    for row in rows:
        if row.get("eol_date"):
            row["days_remaining"] = (row["eol_date"] - today).days
        else:
            row["days_remaining"] = None

    return {"components": rows, "total": len(rows)}


@router.get("/sbom/diff")
async def get_sbom_diff():
    latest = await db.fetchrow(
        "SELECT diff_from_previous, snapshot_date FROM sbom_snapshots ORDER BY snapshot_date DESC LIMIT 1"
    )
    if not latest or not latest["diff_from_previous"]:
        return {"diff": None, "message": "No diff available"}
    return {"diff": latest["diff_from_previous"], "snapshot_date": latest["snapshot_date"]}
