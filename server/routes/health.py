"""Health endpoint"""

import time
from fastapi import APIRouter, Request
from server import database as db

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    start = time.monotonic()
    try:
        await db.fetchval("SELECT 1")
        db_latency = int((time.monotonic() - start) * 1000)
        db_status = "connected"
    except Exception as e:
        db_latency = int((time.monotonic() - start) * 1000)
        db_status = f"error: {e}"

    uptime = time.time() - request.app.state.start_time

    status = "ok" if db_status == "connected" else "degraded"
    status_code = 200 if status == "ok" else 503

    return {
        "status": status,
        "database": db_status,
        "db_latency_ms": db_latency,
        "uptime_seconds": round(uptime, 1),
        "version": "0.1.0",
    }
