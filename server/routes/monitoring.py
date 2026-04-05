"""Monitoring endpoints — Sentry, UptimeRobot, VPS health"""

from fastapi import APIRouter
from server.monitoring import sentry_client, uptimerobot_client, vps_scripts

router = APIRouter()


@router.get("/monitoring")
async def get_monitoring():
    """Aggregated monitoring data from all sources."""
    uptimerobot = await uptimerobot_client.get_monitors()
    sentry_issues = await sentry_client.get_issue_count()
    monitor_log = vps_scripts.parse_monitor_log()
    daily_report = vps_scripts.parse_daily_report()

    # Determine overall status
    ur_status = "green"
    for mon in uptimerobot:
        if mon["status"] == "down":
            ur_status = "red"
            break
        elif mon["status"] in ("seems_down", "paused"):
            ur_status = "yellow"

    sentry_status = "green"
    unresolved = sentry_issues.get("unresolved", 0)
    if unresolved > 10:
        sentry_status = "red"
    elif unresolved > 0:
        sentry_status = "yellow"

    vps_status = "green"
    if monitor_log.get("recent_alerts"):
        vps_status = "yellow"

    return {
        "overall": {
            "uptimerobot": ur_status,
            "sentry": sentry_status,
            "vps": vps_status,
        },
        "uptimerobot": {
            "monitors": uptimerobot,
            "status": ur_status,
        },
        "sentry": {
            **sentry_issues,
            "status": sentry_status,
            "dashboard_url": "https://gracezero-ai.sentry.io",
        },
        "vps": {
            "monitor": monitor_log,
            "daily_report": daily_report,
            "status": vps_status,
        },
    }


@router.get("/monitoring/uptimerobot")
async def get_uptimerobot():
    monitors = await uptimerobot_client.get_monitors()
    account = await uptimerobot_client.get_account_details()
    return {"monitors": monitors, "account": account}


@router.get("/monitoring/sentry")
async def get_sentry():
    projects = await sentry_client.get_projects()
    issues = await sentry_client.get_issue_count()
    return {"projects": projects, "issues": issues}


@router.get("/monitoring/vps")
async def get_vps():
    return {
        "monitor": vps_scripts.parse_monitor_log(),
        "daily_report": vps_scripts.parse_daily_report(),
    }
