"""Module: Recent Anthropic incidents (last 7 days)"""

import httpx
from datetime import datetime, timezone, timedelta
from server.modules.base import BaseModule
from server.models import ModuleResult

INCIDENTS_URL = "https://status.anthropic.com/api/v2/incidents.json"


class IncidentsRecentModule(BaseModule):
    name = "incidents_recent"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(INCIDENTS_URL)
            resp.raise_for_status()
            data = resp.json()

        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent = []

        for inc in data.get("incidents", []):
            created = inc.get("created_at", "")
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                continue

            if created_dt >= cutoff:
                recent.append({
                    "name": inc.get("name"),
                    "status": inc.get("status"),
                    "impact": inc.get("impact"),
                    "created_at": created,
                    "resolved_at": inc.get("resolved_at"),
                    "shortlink": inc.get("shortlink"),
                })

        feed_items = []
        for inc in recent:
            feed_items.append({
                "entry_type": "incident",
                "title": f"Incident: {inc['name']}",
                "body": f"Status: {inc['status']}, Impact: {inc['impact']}",
                "source_url": inc.get("shortlink"),
                "published_at": inc.get("created_at"),
            })

        brief = f"{len(recent)} incident(s) in the last 7 days."
        if recent:
            brief += " Latest: " + recent[0]["name"]

        return self._result(
            success=True,
            data={"incidents": recent, "count": len(recent)},
            brief_text=brief,
            action_items=feed_items,
        )
