"""Hopper Ops — Pydantic models"""

from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel


class ModuleResult(BaseModel):
    module_name: str
    module_type: str  # deterministic, llm
    ran_at: datetime
    success: bool
    data: dict[str, Any]
    html: str = ""
    brief_text: str = ""
    action_items: list[dict[str, Any]] = []
    error_message: str | None = None
    duration_ms: int = 0


class ComponentOut(BaseModel):
    id: int
    name: str
    category: str
    current_version: str | None
    eol_date: date | None
    eol_source: str | None
    risk_level: str
    project: str | None
    notes: str | None
    last_checked_at: datetime | None
    days_remaining: int | None = None


class RiskItemOut(BaseModel):
    id: int
    component_id: int | None
    title: str
    description: str | None
    risk_level: str
    category: str
    deadline: date | None
    status: str
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    days_remaining: int | None = None


class RiskUpdate(BaseModel):
    status: Optional[str] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None


class ActionItemOut(BaseModel):
    id: int
    risk_item_id: int | None
    title: str
    description: str | None
    priority: str
    status: str
    source_module: str | None
    due_date: date | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ActionUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None


class FeedEntryOut(BaseModel):
    id: int
    module_name: str
    entry_type: str
    title: str
    body: str | None
    source_url: str | None
    published_at: datetime | None
    created_at: datetime


class ModuleRunOut(BaseModel):
    id: int
    module_name: str
    module_type: str
    ran_at: datetime
    success: bool
    duration_ms: int | None
    error_message: str | None


class HealthResponse(BaseModel):
    status: str
    database: str
    db_latency_ms: int
    uptime_seconds: float
    version: str = "0.1.0"


class StatusResponse(BaseModel):
    anthropic_status: dict[str, Any] = {}
    risk_summary: dict[str, int] = {}
    action_summary: dict[str, int] = {}
    last_refresh: datetime | None = None
    modules: list[dict[str, Any]] = []
