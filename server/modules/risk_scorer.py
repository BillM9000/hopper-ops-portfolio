"""Module: Risk scorer — aggregates all risk signals into a scored register"""

from datetime import date
from server.modules.base import BaseModule
from server.models import ModuleResult
from server import database as db


class RiskScorerModule(BaseModule):
    name = "risk_scorer"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        # Gather all components with their risk levels
        components = await db.fetch(
            "SELECT id, name, risk_level, eol_date, current_version, project FROM components"
        )

        # Gather existing risk items
        existing_risks = await db.fetch(
            "SELECT id, component_id, title, risk_level, status FROM risk_items WHERE status != 'resolved'"
        )
        existing_component_ids = {r["component_id"] for r in existing_risks if r["component_id"]}

        today = date.today()
        new_risks = []
        summary = {"red": 0, "yellow": 0, "green": 0}

        for comp in components:
            level = comp["risk_level"]
            summary[level] = summary.get(level, 0) + 1

            # Auto-create risk items for red/yellow components if not already tracked
            if level in ("red", "yellow") and comp["id"] not in existing_component_ids:
                days_left = None
                if comp["eol_date"]:
                    days_left = (comp["eol_date"] - today).days

                category = "eol" if comp["eol_date"] else "other"
                description = f"{comp['name']} {comp['current_version'] or ''}"
                if days_left is not None:
                    description += f" — {days_left} days to EOL ({comp['eol_date']})"

                await db.execute(
                    """INSERT INTO risk_items (component_id, title, description, risk_level, category, deadline, status)
                       VALUES ($1, $2, $3, $4, $5, $6, 'open')
                       ON CONFLICT DO NOTHING""",
                    comp["id"],
                    f"{comp['name']} approaching EOL" if category == "eol" else f"{comp['name']} risk: {level}",
                    description,
                    level,
                    category,
                    comp["eol_date"],
                )
                new_risks.append(comp["name"])

        # Count action items
        action_counts = await db.fetchrow(
            """SELECT
                 COUNT(*) FILTER (WHERE status = 'open') AS open,
                 COUNT(*) FILTER (WHERE status = 'in_progress') AS in_progress,
                 COUNT(*) FILTER (WHERE status = 'done') AS done
               FROM action_items"""
        )

        brief = f"Risk summary: {summary['red']} critical, {summary['yellow']} warning, {summary['green']} healthy."
        if new_risks:
            brief += f" New risks created: {', '.join(new_risks)}"

        return self._result(
            success=True,
            data={
                "risk_summary": summary,
                "action_summary": dict(action_counts) if action_counts else {},
                "new_risks_created": new_risks,
                "total_components": len(components),
            },
            brief_text=brief,
        )
