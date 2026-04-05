"""Feed endpoints — news and updates stream"""

from fastapi import APIRouter, Query
from server import database as db

router = APIRouter()


@router.get("/feed")
async def get_feed(
    entry_type: str = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    where = ""
    params = []
    idx = 1

    if entry_type:
        where = f"WHERE entry_type = ${idx}"
        params.append(entry_type)
        idx += 1

    params.extend([limit, offset])
    rows = await db.fetch(
        f"""SELECT * FROM feed_entries {where}
            ORDER BY created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}""",
        *params,
    )

    total = await db.fetchval(
        f"SELECT COUNT(*) FROM feed_entries {where}",
        *(params[:-2]),  # Remove limit/offset
    )

    return {"entries": rows, "total": total}


@router.get("/feed/{entry_type}")
async def get_feed_by_type(entry_type: str, limit: int = Query(50)):
    rows = await db.fetch(
        """SELECT * FROM feed_entries WHERE entry_type = $1
           ORDER BY created_at DESC LIMIT $2""",
        entry_type, limit,
    )
    return {"entries": rows, "total": len(rows)}
