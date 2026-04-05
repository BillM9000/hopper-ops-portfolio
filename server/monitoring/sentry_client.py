"""Sentry API client — read-only access to issues and events"""

import httpx
from server.config import SENTRY_API_TOKEN, SENTRY_ORG

SENTRY_API = "https://sentry.io/api/0"
HEADERS = {"Authorization": f"Bearer {SENTRY_API_TOKEN}"}


async def get_projects() -> list[dict]:
    """List all projects in the org."""
    if not SENTRY_API_TOKEN:
        return []
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{SENTRY_API}/organizations/{SENTRY_ORG}/projects/",
            headers=HEADERS,
        )
        if resp.status_code != 200:
            return []
        return resp.json()


async def get_issues(project_slug: str = "", query: str = "is:unresolved", limit: int = 25) -> list[dict]:
    """Get issues for a project or across the org."""
    if not SENTRY_API_TOKEN:
        return []
    url = f"{SENTRY_API}/organizations/{SENTRY_ORG}/issues/"
    params = {"query": query, "limit": limit, "sort": "date"}
    if project_slug:
        params["project"] = project_slug

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            return []
        return resp.json()


async def get_issue_count(project_slug: str = "") -> dict:
    """Get count of unresolved issues."""
    issues = await get_issues(project_slug, limit=100)
    return {
        "unresolved": len(issues),
        "issues": [
            {
                "title": i.get("title", ""),
                "culprit": i.get("culprit", ""),
                "count": i.get("count", 0),
                "firstSeen": i.get("firstSeen"),
                "lastSeen": i.get("lastSeen"),
                "level": i.get("level", "error"),
                "permalink": i.get("permalink", ""),
            }
            for i in issues[:10]
        ],
    }


async def get_stats(project_slug: str, stat: str = "received", resolution: str = "1h") -> list:
    """Get project stats (events received over time)."""
    if not SENTRY_API_TOKEN:
        return []
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{SENTRY_API}/projects/{SENTRY_ORG}/{project_slug}/stats/",
            headers=HEADERS,
            params={"stat": stat, "resolution": resolution},
        )
        if resp.status_code != 200:
            return []
        return resp.json()
