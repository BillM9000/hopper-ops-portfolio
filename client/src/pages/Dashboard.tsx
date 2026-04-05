import { useState, useEffect } from "react";
import { AlertTriangle, CheckSquare, Activity, Clock, Shield } from "lucide-react";
import ActionCard from "../components/ActionCard";
import FeedEntryComponent from "../components/FeedEntry";
import ModuleStatus from "../components/ModuleStatus";
import RefreshButton from "../components/RefreshButton";
import { getStatus, getActions, getFeed, refreshAll, updateAction } from "../api";
import type { StatusData, ActionItem, FeedEntry } from "../types";

export default function Dashboard() {
  const [status, setStatus] = useState<StatusData | null>(null);
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [feed, setFeed] = useState<FeedEntry[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    const [s, a, f] = await Promise.all([
      getStatus(),
      getActions("status=open"),
      getFeed("limit=10"),
    ]);
    setStatus(s);
    setActions(a.actions);
    setFeed(f.entries);
  };

  useEffect(() => { load(); }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await refreshAll();
      await load();
    } finally {
      setRefreshing(false);
    }
  };

  const handleActionStatus = async (id: number, newStatus: string) => {
    await updateAction(id, { status: newStatus });
    await load();
  };

  const anthropic = status?.anthropic_status as Record<string, unknown> | undefined;
  const indicator = (anthropic?.indicator as string) || "unknown";

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">Dashboard</h1>
          {status?.last_refresh && (
            <p className="text-xs text-ho-muted mt-0.5">
              Last refresh: {new Date(status.last_refresh).toLocaleString()}
            </p>
          )}
        </div>
        <RefreshButton onClick={handleRefresh} loading={refreshing} />
      </div>

      {/* Status cards */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="ho-card flex items-center gap-3 hover:border-ho-accent transition-colors">
          <div className="p-2 rounded-lg bg-ho-accent/10">
            <Shield size={20} className="text-ho-accent-light" />
          </div>
          <div>
            <div className="text-[10px] text-ho-muted uppercase font-semibold">Anthropic</div>
            <div className="text-lg font-bold capitalize">{indicator === "none" ? "Operational" : indicator}</div>
          </div>
        </div>

        <div className="ho-card flex items-center gap-3 hover:border-ho-accent transition-colors">
          <div className="p-2 rounded-lg bg-red-500/10">
            <AlertTriangle size={20} className="text-red-400" />
          </div>
          <div>
            <div className="text-[10px] text-ho-muted uppercase font-semibold">Risks</div>
            <div className="flex items-center gap-2 mt-0.5">
              {status?.risk_summary?.red ? (
                <span className="text-lg font-bold text-red-400">{status.risk_summary.red}</span>
              ) : null}
              {status?.risk_summary?.yellow ? (
                <span className="text-lg font-bold text-yellow-400">{status.risk_summary.yellow}</span>
              ) : null}
              {status?.risk_summary?.green ? (
                <span className="text-lg font-bold text-green-400">{status.risk_summary.green}</span>
              ) : null}
            </div>
          </div>
        </div>

        <div className="ho-card flex items-center gap-3 hover:border-ho-accent transition-colors">
          <div className="p-2 rounded-lg bg-ho-accent/10">
            <CheckSquare size={20} className="text-ho-accent-light" />
          </div>
          <div>
            <div className="text-[10px] text-ho-muted uppercase font-semibold">Actions</div>
            <div className="text-lg font-bold">{status?.action_summary?.open || 0} open</div>
          </div>
        </div>

        <div className="ho-card flex items-center gap-3 hover:border-ho-accent transition-colors">
          <div className="p-2 rounded-lg bg-ho-accent/10">
            <Activity size={20} className="text-ho-accent-light" />
          </div>
          <div>
            <div className="text-[10px] text-ho-muted uppercase font-semibold">Modules</div>
            <div className="text-lg font-bold">
              {status?.modules?.filter((m) => m.success).length || 0}/{status?.modules?.length || 0}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Action Items */}
        <div className="col-span-1 ho-card">
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <CheckSquare size={14} />
            Top Actions
          </h2>
          <div className="space-y-2">
            {actions.slice(0, 5).map((a) => (
              <ActionCard key={a.id} action={a} onStatusChange={handleActionStatus} />
            ))}
            {actions.length === 0 && (
              <div className="text-xs text-ho-muted py-4 text-center">No open actions</div>
            )}
          </div>
        </div>

        {/* Feed */}
        <div className="col-span-1 ho-card">
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Clock size={14} />
            Recent Updates
          </h2>
          <div>
            {feed.slice(0, 8).map((e) => (
              <FeedEntryComponent key={e.id} entry={e} />
            ))}
            {feed.length === 0 && (
              <div className="text-xs text-ho-muted py-4 text-center">No recent updates — run a refresh</div>
            )}
          </div>
        </div>

        {/* Module Status */}
        <div className="col-span-1 ho-card">
          <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Activity size={14} />
            Modules
          </h2>
          <div>
            {status?.modules?.map((m) => (
              <ModuleStatus key={m.module_name} module={m} />
            ))}
            {(!status?.modules || status.modules.length === 0) && (
              <div className="text-xs text-ho-muted py-4 text-center">No module runs yet</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
