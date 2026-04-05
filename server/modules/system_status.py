"""Module: Anthropic system status — checks status.anthropic.com"""

import httpx
from server.modules.base import BaseModule
from server.models import ModuleResult

STATUS_URL = "https://status.claude.com/api/v2/summary.json"


class SystemStatusModule(BaseModule):
    name = "system_status"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(STATUS_URL)
            resp.raise_for_status()
            data = resp.json()

        status = data.get("status", {})
        indicator = status.get("indicator", "unknown")
        description = status.get("description", "")

        components = []
        for comp in data.get("components", []):
            components.append({
                "name": comp.get("name"),
                "status": comp.get("status"),
                "description": comp.get("description", ""),
            })

        # Active incidents
        incidents = []
        for inc in data.get("incidents", []):
            incidents.append({
                "name": inc.get("name"),
                "status": inc.get("status"),
                "impact": inc.get("impact"),
                "created_at": inc.get("created_at"),
            })

        risk_level = "green"
        if indicator == "major":
            risk_level = "red"
        elif indicator in ("minor", "degraded"):
            risk_level = "yellow"

        brief = f"Anthropic Platform: {description}"
        if incidents:
            brief += f" ({len(incidents)} active incident(s))"

        feed_items = []
        if indicator != "none":
            feed_items.append({
                "entry_type": "status",
                "title": f"Anthropic Status: {description}",
                "body": f"Indicator: {indicator}. {len(components)} components checked.",
                "source_url": "https://status.anthropic.com",
            })

        return self._result(
            success=True,
            data={
                "indicator": indicator,
                "description": description,
                "components": components,
                "active_incidents": incidents,
                "risk_level": risk_level,
            },
            brief_text=brief,
            action_items=feed_items,
        )
