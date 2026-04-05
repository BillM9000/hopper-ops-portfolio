"""LLM Module: Anthropic news digest — scrapes anthropic.com/news"""

import httpx
import re
from server.modules.base import BaseModule
from server.models import ModuleResult
from server.config import ANTHROPIC_API_KEY, LLM_MODEL

URL = "https://www.anthropic.com/news"


class NewsDigestModule(BaseModule):
    name = "news_digest"
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
                "content": f"""Summarize the most recent news from Anthropic.
Focus on: product announcements, research, partnerships, and policy updates.
Return JSON: {{"articles": [{{"title": "...", "summary": "1-2 sentences", "date": "YYYY-MM-DD or null"}}], "brief": "one paragraph summary of top stories"}}

Content:
{text}"""
            }],
        )

        response_text = message.content[0].text
        from server.modules.llm_utils import parse_llm_json, extract_brief
        data = parse_llm_json(response_text, "brief")

        feed_items = []
        for article in data.get("articles", [])[:3]:
            feed_items.append({
                "entry_type": "news",
                "title": article.get("title", "Anthropic News"),
                "body": article.get("summary", ""),
                "source_url": URL,
            })

        return self._result(
            success=True,
            data=data,
            brief_text=extract_brief(data, "No news summarized."),
            action_items=feed_items,
        )
