"""Shared utilities for LLM modules."""

import json
import re


def parse_llm_json(text: str, fallback_key: str = "brief") -> dict:
    """Robustly parse JSON from LLM output, handling common issues."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences — may appear anywhere in the text
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)\n\s*```", text, re.DOTALL)
    if fence_match:
        inner = fence_match.group(1).strip()
        try:
            return json.loads(inner)
        except json.JSONDecodeError:
            fixed = re.sub(r",\s*([}\]])", r"\1", inner)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

    # Also try stripping fences from the whole text
    stripped = text.strip()
    if "```" in stripped:
        stripped = re.sub(r"```(?:json)?\s*\n?", "", stripped)
        stripped = re.sub(r"\n?```\s*$", "", stripped)
        stripped = stripped.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            fixed = re.sub(r",\s*([}\]])", r"\1", stripped)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

    # Try extracting the outermost {...} with greedy match
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        raw = brace_match.group()

        for attempt in range(3):
            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                err_msg = str(e)
                # Fix trailing commas before } or ]
                raw = re.sub(r",\s*([}\]])", r"\1", raw)
                # Fix unescaped newlines in string values
                raw = re.sub(r'(?<=": ")(.*?)(?="[,}\]])', lambda m: m.group(0).replace('\n', '\\n'), raw)
                # Fix single trailing comma at end
                raw = re.sub(r",\s*$", "", raw)
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    # Try truncating at the error position and closing
                    if "char" in err_msg:
                        pos_match = re.search(r"char (\d+)", err_msg)
                        if pos_match:
                            pos = int(pos_match.group(1))
                            # Truncate before the error and try to close the JSON
                            truncated = raw[:pos].rstrip(", \n\t")
                            # Count open braces/brackets and close them
                            open_braces = truncated.count("{") - truncated.count("}")
                            open_brackets = truncated.count("[") - truncated.count("]")
                            truncated += "]" * open_brackets + "}" * open_braces
                            try:
                                return json.loads(truncated)
                            except json.JSONDecodeError:
                                pass
                    break

    # Last resort: return the text as the fallback field
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = cleaned.strip().rstrip("`")
    return {fallback_key: cleaned[:500]}


def extract_brief(data: dict, fallback: str = "No summary available.") -> str:
    """Extract a clean brief string from parsed LLM data."""
    brief = data.get("brief", fallback)
    if not isinstance(brief, str):
        brief = str(brief)
    # If the brief is actually JSON or code-fenced, it means parsing hit fallback
    if brief.startswith("```") or brief.startswith("{"):
        for key in ("brief", "summary"):
            if key in data and isinstance(data[key], str) and not data[key].startswith("{"):
                return data[key][:300]
        return fallback
    return brief[:300]


def strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
