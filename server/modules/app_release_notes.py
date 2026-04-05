"""LLM Module: Claude app release notes — scrapes support.claude.com"""

import httpx
import re
from server.modules.base import BaseModule
from server.models import ModuleResult
from server.config import ANTHROPIC_API_KEY, LLM_MODEL

URL = "https://support.claude.com/en/articles/12138966-release-notes"


class AppReleaseNotesModule(BaseModule):
    name = "app_release_notes"
    module_type = "llm"

    async def run(self) -> ModuleResult:
        if not ANTHROPIC_API_KEY:
            return self._result(
                success=False, data={},
                error_message="ANTHROPIC_API_KEY not configured",
            )

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(URL)
            resp.raise_for_status()
            html = resp.text

        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = text[:8000]

        import anthropic
        aclient = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        message = await aclient.messages.create(
            model=LLM_MODEL,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Summarize the most recent Claude app updates from these release notes.
Focus on: new features, UI changes, and notable improvements.
Return a JSON object: {{"updates": [{{"date": "YYYY-MM-DD", "title": "short title", "summary": "1-2 sentences"}}], "brief": "one paragraph summary"}}

Content:
{text}"""
            }],
        )

        response_text = message.content[0].text
        import json
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            data = json.loads(match.group()) if match else {"updates": [], "brief": response_text[:500]}

        feed_items = []
        for update in data.get("updates", [])[:3]:
            feed_items.append({
                "entry_type": "release",
                "title": f"Claude App: {update.get('title', 'Update')}",
                "body": update.get("summary", ""),
                "source_url": URL,
            })

        return self._result(
            success=True,
            data=data,
            brief_text=data.get("brief", "No app updates summarized."),
            action_items=feed_items,
        )
