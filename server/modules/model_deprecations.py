"""Module: Model deprecation tracking"""

import httpx
from datetime import datetime, timezone, timedelta
from server.modules.base import BaseModule
from server.models import ModuleResult

DEPRECATIONS_URL = "https://deprecations.info/api/v1/deprecations.json"


class ModelDeprecationsModule(BaseModule):
    name = "model_deprecations"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        deprecations = []
        action_items = []

        # Try deprecations.info
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(DEPRECATIONS_URL)
                if resp.status_code == 200:
                    data = resp.json()
                    # Filter for Anthropic/Claude-related entries
                    for dep in data if isinstance(data, list) else data.get("deprecations", []):
                        name = dep.get("name", "").lower()
                        vendor = dep.get("vendor", "").lower()
                        if "anthropic" in vendor or "claude" in name:
                            shutdown = dep.get("shutdown_date") or dep.get("eol_date")
                            days_left = None
                            if shutdown:
                                try:
                                    shutdown_dt = datetime.fromisoformat(shutdown.replace("Z", "+00:00"))
                                    if shutdown_dt.tzinfo is None:
                                        shutdown_dt = shutdown_dt.replace(tzinfo=timezone.utc)
                                    days_left = (shutdown_dt - datetime.now(timezone.utc)).days
                                except (ValueError, TypeError):
                                    pass

                            deprecations.append({
                                "name": dep.get("name"),
                                "vendor": dep.get("vendor"),
                                "shutdown_date": shutdown,
                                "days_remaining": days_left,
                                "replacement": dep.get("replacement"),
                                "notes": dep.get("notes", ""),
                            })
        except httpx.HTTPError:
            pass  # Non-critical — this source may not have Anthropic data

        # Known deprecations from our SBOM (hardcoded awareness)
        known = [
            {
                "name": "claude-sonnet-4-20250514",
                "vendor": "Anthropic",
                "shutdown_date": None,
                "days_remaining": None,
                "replacement": "claude-sonnet-4-6",
                "notes": "Older pinned version in traillog gear routes. Update to current.",
            },
        ]

        # Merge known with discovered
        known_names = {d["name"] for d in deprecations}
        for k in known:
            if k["name"] not in known_names:
                deprecations.append(k)

        # Generate action items for things approaching shutdown
        for dep in deprecations:
            days = dep.get("days_remaining")
            if days is not None and days < 90:
                priority = "critical" if days < 30 else "high"
                action_items.append({
                    "entry_type": "deprecation",
                    "title": f"Model {dep['name']} — {days} days until shutdown",
                    "body": f"Replace with {dep.get('replacement', 'latest')}. {dep.get('notes', '')}",
                })

        brief = f"{len(deprecations)} model deprecation(s) tracked."
        approaching = [d for d in deprecations if d.get("days_remaining") is not None and d["days_remaining"] < 90]
        if approaching:
            brief += f" {len(approaching)} approaching shutdown."

        return self._result(
            success=True,
            data={"deprecations": deprecations, "count": len(deprecations)},
            brief_text=brief,
            action_items=action_items,
        )
