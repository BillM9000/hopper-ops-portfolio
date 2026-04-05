"""LLM Module: Action items synthesis — cross-module analysis"""

import json
from server.modules.base import BaseModule
from server.models import ModuleResult
from server.config import ANTHROPIC_API_KEY, LLM_MODEL
from server import database as db


class ActionItemsSynthesisModule(BaseModule):
    name = "action_items_synthesis"
    module_type = "llm"

    async def run(self) -> ModuleResult:
        if not ANTHROPIC_API_KEY:
            return self._result(
                success=False, data={},
                error_message="ANTHROPIC_API_KEY not configured",
            )

        # Gather latest module results
        modules = await db.fetch(
            """SELECT DISTINCT ON (module_name) module_name, brief_text, result_data
               FROM module_runs WHERE success = TRUE
               ORDER BY module_name, ran_at DESC"""
        )

        # Gather current risk items and action items
        risks = await db.fetch(
            "SELECT title, risk_level, category, status FROM risk_items WHERE status != 'resolved' ORDER BY risk_level"
        )
        actions = await db.fetch(
            "SELECT title, priority, status FROM action_items WHERE status IN ('open', 'in_progress') ORDER BY priority"
        )

        context = {
            "module_summaries": {m["module_name"]: m["brief_text"] for m in modules},
            "open_risks": [dict(r) for r in risks],
            "open_actions": [dict(a) for a in actions],
        }

        import anthropic
        aclient = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        message = await aclient.messages.create(
            model=LLM_MODEL,
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": f"""You are an operational intelligence system for a small engineering org running AI-powered web apps on a single VPS.

Given the current state below, synthesize the most important action items. Prioritize by urgency and impact. Identify any patterns or connections between risks.

Return JSON: {{"synthesized_actions": [{{"title": "action title", "priority": "critical|high|medium|low", "reason": "why this matters now"}}], "patterns": ["any cross-cutting observations"], "brief": "2-3 sentence executive summary"}}

Current state:
{json.dumps(context, indent=2, default=str)}"""
            }],
        )

        response_text = message.content[0].text
        from server.modules.llm_utils import parse_llm_json, extract_brief
        data = parse_llm_json(response_text, "brief")

        # Upsert synthesized action items
        for action in data.get("synthesized_actions", []):
            await db.execute(
                """INSERT INTO action_items (title, description, priority, source_module, status)
                   VALUES ($1, $2, $3, 'action_items_synthesis', 'open')
                   ON CONFLICT DO NOTHING""",
                action.get("title", ""),
                action.get("reason", ""),
                action.get("priority", "medium"),
            )

        return self._result(
            success=True,
            data=data,
            brief_text=extract_brief(data, "No synthesis available."),
        )
