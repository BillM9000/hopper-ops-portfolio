"""LLM Module: API release notes — scrapes docs.anthropic.com and summarizes"""

import httpx
import re
from server.modules.base import BaseModule
from server.models import ModuleResult
from server.config import ANTHROPIC_API_KEY, LLM_MODEL

URL = "https://docs.anthropic.com/en/release-notes/overview"


class ApiReleaseNotesModule(BaseModule):
    name = "api_release_notes"
    module_type = "llm"

    async def run(self) -> ModuleResult:
        if not ANTHROPIC_API_KEY:
            return self._result(
                success=False, data={},
                error_message="ANTHROPIC_API_KEY not configured",
            )

        # Fetch the page
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(URL)
            resp.raise_for_status()
            html = resp.text

        # Strip HTML to text (rough)
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = text[:8000]  # Limit for Haiku

        # Call Claude
        import anthropic
        aclient = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        message = await aclient.messages.create(
            model=LLM_MODEL,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Summarize the most recent API/platform changes from these Anthropic release notes.
Focus on: breaking changes, new features, deprecations, and anything that affects developers.
Return a JSON object with this exact structure:
{{"changes": [{{"date": "YYYY-MM-DD", "title": "short title", "impact": "low|medium|high", "summary": "1-2 sentences"}}], "breaking_changes": ["list any breaking changes"], "brief": "one paragraph summary"}}

Release notes content:
{text}"""
            }],
        )

        response_text = message.content[0].text
        import json
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = {"changes": [], "brief": response_text[:500]}

        brief = data.get("brief", "No API changes summarized.")
        feed_items = []
        for change in data.get("changes", [])[:3]:
            feed_items.append({
                "entry_type": "release",
                "title": f"API: {change.get('title', 'Update')}",
                "body": change.get("summary", ""),
                "source_url": URL,
            })

        return self._result(
            success=True,
            data=data,
            brief_text=brief,
            action_items=feed_items,
        )
