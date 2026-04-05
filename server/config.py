"""Hopper Ops — Configuration"""

import os
from pathlib import Path

# Database
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://hopperops:changeme@localhost:5432/hopper_ops"
)

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CALLBACK_URL = os.environ.get(
    "GOOGLE_CALLBACK_URL",
    "https://your-domain.example.com/auth/google/callback"
)

# App
APP_URL = os.environ.get("APP_URL", "https://your-domain.example.com")
APP_PORT = int(os.environ.get("APP_PORT", "3616"))
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
SESSION_SECRET = os.environ.get("SESSION_SECRET", "hopper-ops-dev-secret-change-me")

# Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-haiku-4-5-20251001"

# Monitoring
UPTIMEROBOT_API_KEY = os.environ.get("UPTIMEROBOT_API_KEY", "")
SENTRY_API_TOKEN = os.environ.get("SENTRY_API_TOKEN", "")
SENTRY_ORG = os.environ.get("SENTRY_ORG", "gracezero-ai")
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")

# Paths (VPS)
MONITOR_LOG_PATH = os.environ.get("MONITOR_LOG_PATH", "/opt/app/backups/monitor.log")
DAILY_REPORT_LOG_PATH = os.environ.get("DAILY_REPORT_LOG_PATH", "/opt/app/backups/daily-report.log")

# Static files
STATIC_DIR = Path(__file__).parent.parent / "client" / "dist"
