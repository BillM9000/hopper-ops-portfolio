"""Module: SBOM diff — compare today's snapshot to the previous one"""

import json
from datetime import date
from server.modules.base import BaseModule
from server.models import ModuleResult
from server import database as db


class SbomDiffModule(BaseModule):
    name = "sbom_diff"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        # Get the two most recent snapshots
        snapshots = await db.fetch(
            "SELECT id, snapshot_date, data FROM sbom_snapshots ORDER BY snapshot_date DESC LIMIT 2"
        )

        if len(snapshots) < 2:
            return self._result(
                success=True,
                data={"diff": None, "message": "Not enough snapshots for comparison"},
                brief_text="SBOM diff: Only one snapshot available, no comparison possible.",
            )

        current = snapshots[0]["data"]
        previous = snapshots[1]["data"]

        if isinstance(current, str):
            current = json.loads(current)
        if isinstance(previous, str):
            previous = json.loads(previous)

        # Compare components
        current_map = {c["name"]: c for c in current.get("components", [])}
        previous_map = {c["name"]: c for c in previous.get("components", [])}

        added = []
        removed = []
        changed = []

        for name, comp in current_map.items():
            if name not in previous_map:
                added.append(comp)
            elif comp.get("version") != previous_map[name].get("version"):
                changed.append({
                    "name": name,
                    "old_version": previous_map[name].get("version"),
                    "new_version": comp.get("version"),
                })

        for name in previous_map:
            if name not in current_map:
                removed.append(previous_map[name])

        diff = {
            "added": added,
            "removed": removed,
            "changed": changed,
            "from_date": str(snapshots[1]["snapshot_date"]),
            "to_date": str(snapshots[0]["snapshot_date"]),
        }

        # Store diff in latest snapshot
        await db.execute(
            "UPDATE sbom_snapshots SET diff_from_previous = $1::jsonb WHERE id = $2",
            json.dumps(diff, default=str),
            snapshots[0]["id"],
        )

        changes_total = len(added) + len(removed) + len(changed)
        feed_items = []
        if changes_total > 0:
            feed_items.append({
                "entry_type": "status",
                "title": f"SBOM changed: {changes_total} difference(s)",
                "body": f"Added: {len(added)}, Removed: {len(removed)}, Version changes: {len(changed)}",
            })

        brief = f"SBOM diff: {changes_total} change(s) since {diff['from_date']}."
        if changed:
            brief += " Version changes: " + ", ".join(
                f"{c['name']} {c['old_version']}→{c['new_version']}" for c in changed[:3]
            )

        return self._result(
            success=True,
            data=diff,
            brief_text=brief,
            action_items=feed_items,
        )
