export interface Component {
  id: number;
  name: string;
  category: string;
  current_version: string | null;
  eol_date: string | null;
  eol_source: string | null;
  risk_level: "red" | "yellow" | "green";
  project: string | null;
  notes: string | null;
  last_checked_at: string | null;
  days_remaining: number | null;
}

export interface RiskItem {
  id: number;
  component_id: number | null;
  component_name?: string;
  current_version?: string;
  title: string;
  description: string | null;
  risk_level: "red" | "yellow" | "green";
  category: string;
  deadline: string | null;
  status: string;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  days_remaining: number | null;
}

export interface ActionItem {
  id: number;
  risk_item_id: number | null;
  title: string;
  description: string | null;
  priority: "critical" | "high" | "medium" | "low";
  status: string;
  source_module: string | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface FeedEntry {
  id: number;
  module_name: string;
  entry_type: string;
  title: string;
  body: string | null;
  source_url: string | null;
  published_at: string | null;
  created_at: string;
}

export interface ModuleRun {
  module_name: string;
  module_type: string;
  ran_at: string | null;
  success: boolean | null;
  duration_ms: number | null;
  error_message: string | null;
}

export interface UptimeMonitor {
  id: number;
  friendly_name: string;
  url: string;
  status: string;
  uptime_1d: number;
  uptime_7d: number;
  uptime_30d: number;
  avg_response_ms: number;
}

export interface MonitoringData {
  overall: { uptimerobot: string; sentry: string; vps: string };
  uptimerobot: { monitors: UptimeMonitor[]; status: string };
  sentry: { unresolved: number; issues: SentryIssue[]; status: string; dashboard_url: string };
  vps: { monitor: VpsMonitor; daily_report: VpsDailyReport; status: string };
}

export interface SentryIssue {
  title: string;
  culprit: string;
  count: number;
  firstSeen: string;
  lastSeen: string;
  level: string;
  permalink: string;
}

export interface VpsMonitor {
  available: boolean;
  entries: unknown[];
  recent_alerts: string[];
  total_checks: number;
}

export interface VpsDailyReport {
  available: boolean;
  raw: string[];
  line_count: number;
}

export interface StatusData {
  anthropic_status: Record<string, unknown>;
  risk_summary: Record<string, number>;
  action_summary: Record<string, number>;
  last_refresh: string | null;
  modules: ModuleRun[];
}

export interface User {
  email: string;
  name: string;
  picture: string;
}
