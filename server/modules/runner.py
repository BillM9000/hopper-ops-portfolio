"""Module orchestrator — runs all or specific modules and stores results."""

import logging
from datetime import datetime, timezone

from server.modules.base import BaseModule, timed_run
from server.modules.system_status import SystemStatusModule
from server.modules.incidents_recent import IncidentsRecentModule
from server.modules.claude_code_releases import ClaudeCodeReleasesModule
from server.modules.model_deprecations import ModelDeprecationsModule
from server.modules.stack_eol_check import StackEolCheckModule
from server.modules.sbom_diff import SbomDiffModule
from server.modules.risk_scorer import RiskScorerModule
from server.modules.api_release_notes import ApiReleaseNotesModule
from server.modules.app_release_notes import AppReleaseNotesModule
from server.modules.news_digest import NewsDigestModule
from server.modules.interesting_finds import InterestingFindsModule
from server.modules.action_items_synthesis import ActionItemsSynthesisModule
from server.models import ModuleResult
from server import database as db

logger = logging.getLogger("hopper-ops.runner")

# Registry of all deterministic modules (order matters — risk_scorer runs last)
DETERMINISTIC_MODULES: list[type[BaseModule]] = [
    SystemStatusModule,
    IncidentsRecentModule,
    ClaudeCodeReleasesModule,
    ModelDeprecationsModule,
    StackEolCheckModule,
    SbomDiffModule,
    RiskScorerModule,
]

# LLM modules (run after deterministic)
LLM_MODULES: list[type[BaseModule]] = [
    ApiReleaseNotesModule,
    AppReleaseNotesModule,
    NewsDigestModule,
    InterestingFindsModule,
    ActionItemsSynthesisModule,
]

ALL_MODULES = DETERMINISTIC_MODULES + LLM_MODULES


def get_module_by_name(name: str) -> type[BaseModule] | None:
    for mod_cls in ALL_MODULES:
        if mod_cls.name == name:
            return mod_cls
    return None


async def store_result(result: ModuleResult):
    """Store module run result in database."""
    import json
    await db.execute(
        """INSERT INTO module_runs (module_name, module_type, ran_at, success, duration_ms, result_data, brief_text, error_message)
           VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)""",
        result.module_name,
        result.module_type,
        result.ran_at,
        result.success,
        result.duration_ms,
        json.dumps(result.data, default=str),
        result.brief_text,
        result.error_message,
    )

    # Store feed entries from action items
    for item in result.action_items:
        published = item.get("published_at")
        if isinstance(published, str):
            try:
                from datetime import datetime as dt
                published = dt.fromisoformat(published.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                published = result.ran_at
        elif published is None:
            published = result.ran_at

        await db.execute(
            """INSERT INTO feed_entries (module_name, entry_type, title, body, source_url, published_at)
               VALUES ($1, $2, $3, $4, $5, $6)
               ON CONFLICT DO NOTHING""",
            result.module_name,
            item.get("entry_type", "status"),
            item.get("title", ""),
            item.get("body", ""),
            item.get("source_url"),
            published,
        )


async def run_all(module_types: str = "all") -> list[ModuleResult]:
    """Run all modules (or filtered by type) and store results."""
    results = []

    if module_types in ("all", "deterministic"):
        for mod_cls in DETERMINISTIC_MODULES:
            logger.info(f"Running module: {mod_cls.name}")
            mod = mod_cls()
            result = await timed_run(mod)
            await store_result(result)
            results.append(result)
            if result.success:
                logger.info(f"  {mod_cls.name}: OK ({result.duration_ms}ms)")
            else:
                logger.warning(f"  {mod_cls.name}: FAILED — {result.error_message}")

    if module_types in ("all", "llm"):
        for mod_cls in LLM_MODULES:
            logger.info(f"Running LLM module: {mod_cls.name}")
            mod = mod_cls()
            result = await timed_run(mod)
            await store_result(result)
            results.append(result)

    return results


async def run_single(name: str) -> ModuleResult | None:
    """Run a specific module by name."""
    mod_cls = get_module_by_name(name)
    if not mod_cls:
        return None
    mod = mod_cls()
    result = await timed_run(mod)
    await store_result(result)
    return result
