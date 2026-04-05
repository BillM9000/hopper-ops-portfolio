"""Module: Claude Code releases from GitHub atom feed"""

import httpx
import xml.etree.ElementTree as ET
from server.modules.base import BaseModule
from server.models import ModuleResult

RELEASES_URL = "https://github.com/anthropics/claude-code/releases.atom"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


class ClaudeCodeReleasesModule(BaseModule):
    name = "claude_code_releases"
    module_type = "deterministic"

    async def run(self) -> ModuleResult:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(RELEASES_URL)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        entries = root.findall(f"{ATOM_NS}entry")

        releases = []
        for entry in entries[:5]:
            title = entry.findtext(f"{ATOM_NS}title", "")
            link_el = entry.find(f"{ATOM_NS}link")
            link = link_el.get("href", "") if link_el is not None else ""
            updated = entry.findtext(f"{ATOM_NS}updated", "")
            content = entry.findtext(f"{ATOM_NS}content", "")

            # Truncate content for storage
            if len(content) > 500:
                content = content[:500] + "..."

            releases.append({
                "title": title,
                "url": link,
                "published_at": updated,
                "summary": content,
            })

        feed_items = []
        for rel in releases[:3]:
            feed_items.append({
                "entry_type": "release",
                "title": f"Claude Code {rel['title']}",
                "body": rel.get("summary", "")[:200],
                "source_url": rel.get("url"),
                "published_at": rel.get("published_at"),
            })

        brief = f"{len(releases)} recent Claude Code releases."
        if releases:
            brief += f" Latest: {releases[0]['title']}"

        return self._result(
            success=True,
            data={"releases": releases, "count": len(releases)},
            brief_text=brief,
            action_items=feed_items,
        )
