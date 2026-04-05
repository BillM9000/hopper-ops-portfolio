"""UptimeRobot API client — read-only access to monitors"""

import httpx
from server.config import UPTIMEROBOT_API_KEY

UPTIMEROBOT_API = "https://api.uptimerobot.com/v2"


async def get_monitors() -> list[dict]:
    """Get all monitors with status and response times."""
    if not UPTIMEROBOT_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{UPTIMEROBOT_API}/getMonitors",
            json={
                "api_key": UPTIMEROBOT_API_KEY,
                "format": "json",
                "response_times": 1,
                "response_times_limit": 24,
                "logs": 1,
                "logs_limit": 10,
                "custom_uptime_ratios": "1-7-30",
            },
        )
        if resp.status_code != 200:
            return []

        data = resp.json()
        monitors = data.get("monitors", [])

        result = []
        for mon in monitors:
            # Status codes: 0=paused, 1=not checked, 2=up, 8=seems down, 9=down
            status_map = {0: "paused", 1: "pending", 2: "up", 8: "seems_down", 9: "down"}
            status = status_map.get(mon.get("status"), "unknown")

            # Parse custom uptime ratios (1d-7d-30d)
            ratios = (mon.get("custom_uptime_ratio", "0-0-0") or "0-0-0").split("-")

            # Average response time from recent samples
            response_times = mon.get("response_times", [])
            avg_response = 0
            if response_times:
                avg_response = sum(rt.get("value", 0) for rt in response_times) // len(response_times)

            result.append({
                "id": mon.get("id"),
                "friendly_name": mon.get("friendly_name"),
                "url": mon.get("url"),
                "status": status,
                "uptime_1d": float(ratios[0]) if len(ratios) > 0 else 0,
                "uptime_7d": float(ratios[1]) if len(ratios) > 1 else 0,
                "uptime_30d": float(ratios[2]) if len(ratios) > 2 else 0,
                "avg_response_ms": avg_response,
                "response_times": [
                    {"value": rt.get("value", 0), "datetime": rt.get("datetime", 0)}
                    for rt in response_times[:24]
                ],
            })

        return result


async def get_account_details() -> dict:
    """Get account details including monitor limits."""
    if not UPTIMEROBOT_API_KEY:
        return {}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{UPTIMEROBOT_API}/getAccountDetails",
            json={"api_key": UPTIMEROBOT_API_KEY, "format": "json"},
        )
        if resp.status_code != 200:
            return {}
        data = resp.json()
        account = data.get("account", {})
        return {
            "monitor_limit": account.get("monitor_limit"),
            "up_monitors": account.get("up_monitors"),
            "down_monitors": account.get("down_monitors"),
            "paused_monitors": account.get("paused_monitors"),
        }
