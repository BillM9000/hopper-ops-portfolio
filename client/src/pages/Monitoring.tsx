import { useState, useEffect } from "react";
import { ExternalLink, Wifi, Bug, Server } from "lucide-react";
import StatusBadge from "../components/StatusBadge";
import RefreshButton from "../components/RefreshButton";
import { getMonitoring } from "../api";
import type { MonitoringData } from "../types";

export default function Monitoring() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const d = await getMonitoring();
      setData(d);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <h1 className="text-xl font-bold">Monitoring</h1>
        <RefreshButton onClick={load} loading={loading} />
      </div>

      {/* Status summary cards */}
      {data && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4 mb-6">
          <div className="ho-card flex items-center gap-3">
            <Wifi size={20} className="text-ho-accent-light" />
            <div>
              <div className="text-[10px] text-ho-muted uppercase font-semibold">UptimeRobot</div>
              <StatusBadge level={data.overall.uptimerobot} size="md" />
            </div>
          </div>
          <div className="ho-card flex items-center gap-3">
            <Bug size={20} className="text-ho-accent-light" />
            <div>
              <div className="text-[10px] text-ho-muted uppercase font-semibold">Sentry</div>
              <div className="flex items-center gap-2">
                <StatusBadge level={data.overall.sentry} size="md" />
                <span className="text-sm text-ho-muted">{data.sentry.unresolved} issues</span>
              </div>
            </div>
          </div>
          <div className="ho-card flex items-center gap-3">
            <Server size={20} className="text-ho-accent-light" />
            <div>
              <div className="text-[10px] text-ho-muted uppercase font-semibold">VPS Health</div>
              <StatusBadge level={data.overall.vps} size="md" />
            </div>
          </div>
        </div>
      )}

      {/* UptimeRobot */}
      {data?.uptimerobot.monitors.length ? (
        <div className="ho-card mb-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold">UptimeRobot</h2>
            <a
              href="https://dashboard.uptimerobot.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-ho-muted hover:text-ho-accent-light text-xs flex items-center gap-1"
            >
              Dashboard <ExternalLink size={10} />
            </a>
          </div>
          <div className="space-y-2">
            {data.uptimerobot.monitors.map((m) => (
              <div key={m.id} className="flex items-center gap-3 py-2 px-3 rounded-md bg-ho-bg/50">
                <StatusBadge level={m.status === "up" ? "green" : m.status === "down" ? "red" : "yellow"} />
                <span className="text-sm font-medium flex-1">{m.friendly_name}</span>
                <span className="text-xs text-ho-muted">{m.uptime_30d}%</span>
                <span className="text-xs font-mono text-ho-muted">{m.avg_response_ms}ms</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* Sentry */}
      {data?.sentry && (
        <div className="ho-card mb-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold">Sentry (last 24h)</h2>
            <a
              href={data.sentry.dashboard_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-ho-muted hover:text-ho-accent-light text-xs flex items-center gap-1"
            >
              Dashboard <ExternalLink size={10} />
            </a>
          </div>
          {data.sentry.issues?.length ? (
            <div className="space-y-1">
              {data.sentry.issues.map((issue, i) => (
                <div key={i} className="flex items-center gap-3 py-2 px-3 rounded-md bg-ho-bg/50 text-sm">
                  <span className="text-red-400 font-mono text-xs">{issue.level}</span>
                  <span className="flex-1 truncate">{issue.title}</span>
                  <span className="text-xs text-ho-muted">{issue.count}x</span>
                  {issue.permalink && (
                    <a href={issue.permalink} target="_blank" rel="noopener noreferrer" className="text-ho-muted hover:text-ho-accent-light">
                      <ExternalLink size={12} />
                    </a>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-ho-muted text-center py-4">No unresolved issues</div>
          )}
        </div>
      )}

      {/* VPS Health */}
      {data?.vps.monitor.available && (
        <div className="ho-card">
          <h2 className="text-sm font-semibold mb-3">VPS Health (monitor.sh)</h2>
          {data.vps.monitor.recent_alerts?.length ? (
            <div className="space-y-1">
              {data.vps.monitor.recent_alerts.map((alert, i) => (
                <div key={i} className="text-xs font-mono text-yellow-400 bg-yellow-500/10 px-3 py-1.5 rounded">
                  {alert}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-green-400 text-center py-4">No recent alerts</div>
          )}
        </div>
      )}
    </div>
  );
}
