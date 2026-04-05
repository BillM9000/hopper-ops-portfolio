"""Module management endpoints"""

from fastapi import APIRouter, HTTPException
from server import database as db
from server.modules import runner

router = APIRouter()


@router.get("/modules")
async def list_modules():
    """List all modules with last run status."""
    rows = await db.fetch(
        """SELECT DISTINCT ON (module_name) module_name, module_type, ran_at, success, duration_ms, error_message
           FROM module_runs
           ORDER BY module_name, ran_at DESC"""
    )

    # Include modules that haven't run yet
    all_names = {cls.name for cls in runner.ALL_MODULES}
    run_map = {r["module_name"]: dict(r) for r in rows}

    modules = []
    for name in sorted(all_names):
        if name in run_map:
            modules.append(run_map[name])
        else:
            mod_cls = runner.get_module_by_name(name)
            modules.append({
                "module_name": name,
                "module_type": mod_cls.module_type if mod_cls else "unknown",
                "ran_at": None,
                "success": None,
                "duration_ms": None,
                "error_message": None,
            })

    return {"modules": modules}


@router.get("/modules/{name}/history")
async def module_history(name: str, limit: int = 20):
    rows = await db.fetch(
        """SELECT id, module_name, module_type, ran_at, success, duration_ms, error_message
           FROM module_runs WHERE module_name = $1
           ORDER BY ran_at DESC LIMIT $2""",
        name, limit,
    )
    return {"history": [dict(r) for r in rows]}


@router.post("/refresh")
async def refresh_all():
    """Trigger all modules to run now."""
    results = await runner.run_all()
    return {
        "ran": len(results),
        "success": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [
            {"module": r.module_name, "success": r.success, "duration_ms": r.duration_ms, "error": r.error_message}
            for r in results
        ],
    }


@router.post("/refresh/{module_name}")
async def refresh_module(module_name: str):
    """Trigger a specific module."""
    result = await runner.run_single(module_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")
    return {
        "module": result.module_name,
        "success": result.success,
        "duration_ms": result.duration_ms,
        "error": result.error_message,
    }
