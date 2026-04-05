"""Module: Stack EOL check — compares SBOM components against endoflife.date"""

import httpx
from datetime import datetime, timezone, date
from server.modules.base import BaseModule
from server.models import ModuleResult
from server import database as db

# Map our component names to endoflife.date product slugs
PRODUCT_MAP = {
    "postgresql": "postgresql",
    "nodejs": "nodejs",
    "python": "python",
    "ubuntu": "ubuntu",
    "nginx": "nginx",
    "docker-engine": "docker-engine",
    "traefik": "traefik",
}

EOL_API = "https://endoflife.date/api"


class StackEolCheckModule(BaseModule):
    name = "stack_eol_check"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        components = await db.fetch(
            "SELECT id, name, current_version, eol_date, risk_level FROM components WHERE category = 'infrastructure'"
        )

        results = []
        action_items = []
        today = date.today()

        async with httpx.AsyncClient(timeout=15) as client:
            for comp in components:
                name = comp["name"].lower()
                product_slug = PRODUCT_MAP.get(name)
                if not product_slug:
                    results.append({
                        "name": comp["name"],
                        "version": comp["current_version"],
                        "eol_date": str(comp["eol_date"]) if comp["eol_date"] else None,
                        "risk_level": comp["risk_level"],
                        "source": "manual",
                        "days_remaining": None,
                    })
                    continue

                try:
                    resp = await client.get(f"{EOL_API}/{product_slug}.json")
                    if resp.status_code != 200:
                        continue

                    cycles = resp.json()
                    version = comp["current_version"] or ""

                    # Find matching cycle
                    matched_cycle = None
                    for cycle in cycles:
                        cycle_ver = str(cycle.get("cycle", ""))
                        # Match major version or major.minor
                        if version.startswith(cycle_ver):
                            matched_cycle = cycle
                            break

                    if matched_cycle:
                        eol = matched_cycle.get("eol")
                        eol_date = None
                        days_remaining = None
                        risk_level = "green"

                        if isinstance(eol, str):
                            try:
                                eol_date = date.fromisoformat(eol)
                                days_remaining = (eol_date - today).days
                                if days_remaining < 0:
                                    risk_level = "red"
                                elif days_remaining < 90:
                                    risk_level = "red"
                                elif days_remaining < 365:
                                    risk_level = "yellow"
                            except ValueError:
                                pass
                        elif eol is False:
                            risk_level = "green"
                            days_remaining = None  # Not EOL

                        # Update component in DB
                        await db.execute(
                            """UPDATE components SET eol_date = $1, eol_source = 'endoflife.date',
                               risk_level = $2, last_checked_at = NOW() WHERE id = $3""",
                            eol_date, risk_level, comp["id"]
                        )

                        results.append({
                            "name": comp["name"],
                            "version": comp["current_version"],
                            "eol_date": str(eol_date) if eol_date else None,
                            "risk_level": risk_level,
                            "days_remaining": days_remaining,
                            "source": "endoflife.date",
                            "lts": matched_cycle.get("lts"),
                        })

                        if risk_level in ("red", "yellow") and days_remaining is not None:
                            action_items.append({
                                "entry_type": "eol",
                                "title": f"{comp['name']} {comp['current_version']} — {days_remaining} days to EOL",
                                "body": f"EOL: {eol_date}. Plan upgrade.",
                            })

                except httpx.HTTPError:
                    results.append({
                        "name": comp["name"],
                        "version": comp["current_version"],
                        "error": "Failed to check endoflife.date",
                    })

        red_count = sum(1 for r in results if r.get("risk_level") == "red")
        yellow_count = sum(1 for r in results if r.get("risk_level") == "yellow")
        brief = f"Stack EOL check: {len(results)} components. {red_count} critical, {yellow_count} warning."

        return self._result(
            success=True,
            data={"components": results, "red": red_count, "yellow": yellow_count},
            brief_text=brief,
            action_items=action_items,
        )
