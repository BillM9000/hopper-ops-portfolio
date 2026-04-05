"""LLM Module: Interesting finds — curated industry news from RSS"""

import httpx
import xml.etree.ElementTree as ET
from server.modules.base import BaseModule
from server.models import ModuleResult
from server.config import ANTHROPIC_API_KEY, LLM_MODEL

# Configurable RSS feeds
RSS_FEEDS = [
    "https://simonwillison.net/atom/everything/",
    "https://blog.pragmaticengineer.com/rss/",
]

ATOM_NS = "{http://www.w3.org/2005/Atom}"


class InterestingFindsModule(BaseModule):
    name = "interesting_finds"
    module_type = "llm"

    async def run(self) -> ModuleResult:
        if not ANTHROPIC_API_KEY:
            return self._result(
                success=False, data={},
                error_message="ANTHROPIC_API_KEY not configured",
            )

        entries = []
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            for feed_url in RSS_FEEDS:
                try:
                    resp = await client.get(feed_url)
                    if resp.status_code != 200:
                        continue
                    root = ET.fromstring(resp.text)

                    # Try Atom format
                    items = root.findall(f"{ATOM_NS}entry")
                    if items:
                        for item in items[:5]:
                            title = item.findtext(f"{ATOM_NS}title", "")
                            link_el = item.find(f"{ATOM_NS}link")
                            link = link_el.get("href", "") if link_el is not None else ""
                            summary = item.findtext(f"{ATOM_NS}summary", "")[:300]
                            entries.append({"title": title, "url": link, "summary": summary, "source": feed_url})
                    else:
                        # Try RSS 2.0
                        for item in root.findall(".//item")[:5]:
                            title = item.findtext("title", "")
                            link = item.findtext("link", "")
                            desc = item.findtext("description", "")[:300]
                            entries.append({"title": title, "url": link, "summary": desc, "source": feed_url})
                except Exception:
                    continue

        if not entries:
            return self._result(
                success=True,
                data={"finds": [], "brief": "No RSS content available."},
                brief_text="No interesting finds this cycle.",
            )

        # Use Claude to curate
        import anthropic
        aclient = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        import json

        entries_text = json.dumps(entries[:15], indent=2)
        message = await aclient.messages.create(
            model=LLM_MODEL,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""From these RSS entries, pick the 3-5 most relevant to an engineering leader running AI-powered web apps on a single VPS. Focus on: AI/LLM tooling, DevOps, infrastructure, and practical engineering.
Return JSON: {{"finds": [{{"title": "...", "summary": "1 sentence why it's interesting", "url": "..."}}], "brief": "one sentence summary"}}

Entries:
{entries_text}"""
            }],
        )

        response_text = message.content[0].text
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            data = json.loads(match.group()) if match else {"finds": [], "brief": "Could not parse."}

        feed_items = []
        for find in data.get("finds", [])[:5]:
            feed_items.append({
                "entry_type": "interesting",
                "title": find.get("title", ""),
                "body": find.get("summary", ""),
                "source_url": find.get("url", ""),
            })

        return self._result(
            success=True,
            data=data,
            brief_text=data.get("brief", "See interesting finds."),
            action_items=feed_items,
        )
