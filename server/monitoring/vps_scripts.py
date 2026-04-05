"""VPS script log parser — reads monitor.sh and daily-report.sh output"""

import os
from pathlib import Path
from server.config import MONITOR_LOG_PATH, DAILY_REPORT_LOG_PATH


def read_tail(filepath: str, lines: int = 50) -> list[str]:
    """Read the last N lines of a file."""
    path = Path(filepath)
    if not path.exists():
        return []
    try:
        with open(path) as f:
            all_lines = f.readlines()
            return [line.rstrip() for line in all_lines[-lines:]]
    except (OSError, PermissionError):
        return []


def parse_monitor_log(lines: int = 50) -> dict:
    """Parse monitor.sh output for health checks."""
    raw = read_tail(MONITOR_LOG_PATH, lines)
    if not raw:
        return {"available": False, "message": "monitor.log not found", "entries": []}

    entries = []
    current_entry = None

    for line in raw:
        if line.startswith("=== Monitor Check"):
            if current_entry:
                entries.append(current_entry)
            current_entry = {"timestamp": line, "checks": [], "alerts": []}
        elif current_entry:
            if "ALERT" in line or "WARNING" in line:
                current_entry["alerts"].append(line)
            elif line.strip():
                current_entry["checks"].append(line)

    if current_entry:
        entries.append(current_entry)

    alerts = []
    for entry in entries:
        alerts.extend(entry.get("alerts", []))

    return {
        "available": True,
        "entries": entries[-5:],  # Last 5 check runs
        "recent_alerts": alerts[-10:],
        "total_checks": len(entries),
    }


def parse_daily_report(lines: int = 100) -> dict:
    """Parse daily-report.sh output."""
    raw = read_tail(DAILY_REPORT_LOG_PATH, lines)
    if not raw:
        return {"available": False, "message": "daily-report.log not found", "entries": []}

    # The daily report is a structured text output
    return {
        "available": True,
        "raw": raw,
        "line_count": len(raw),
    }
