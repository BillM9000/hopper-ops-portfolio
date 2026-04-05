"""Hopper Ops — FastAPI main application"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from server.config import SESSION_SECRET, STATIC_DIR, APP_PORT
from server.database import init_db, close_db
from server.routes.status import router as status_router
from server.routes.sbom import router as sbom_router
from server.routes.risks import router as risks_router
from server.routes.actions import router as actions_router
from server.routes.feed import router as feed_router
from server.routes.brief import router as brief_router
from server.routes.modules import router as modules_router
from server.routes.history import router as history_router
from server.routes.monitoring import router as monitoring_router
from server.routes.health import router as health_router
from server.routes.auth import router as auth_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("hopper-ops")

START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hopper Ops...")
    await init_db()
    logger.info("Database initialized")

    # Seed SBOM if components table is empty
    from server.database import fetchval
    count = await fetchval("SELECT COUNT(*) FROM components")
    if count == 0:
        logger.info("Seeding SBOM data...")
        from server.sbom.scanner import seed_sbom
        await seed_sbom()
        logger.info("SBOM seeded")

    yield
    await close_db()
    logger.info("Hopper Ops shutdown")


app = FastAPI(
    title="Hopper Ops",
    description="Operational Intelligence Dashboard — GraceZero AI",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://hopperops.gracezero.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(status_router, prefix="/api", tags=["status"])
app.include_router(sbom_router, prefix="/api", tags=["sbom"])
app.include_router(risks_router, prefix="/api", tags=["risks"])
app.include_router(actions_router, prefix="/api", tags=["actions"])
app.include_router(feed_router, prefix="/api", tags=["feed"])
app.include_router(brief_router, prefix="/api", tags=["brief"])
app.include_router(modules_router, prefix="/api", tags=["modules"])
app.include_router(history_router, prefix="/api", tags=["history"])
app.include_router(monitoring_router, prefix="/api", tags=["monitoring"])

# Expose start time for health endpoint
app.state.start_time = START_TIME

# Serve React static files in production
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA — all non-API routes fall through to index.html."""
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))
