import { useState, useEffect } from "react";
import { CheckCircle, XCircle, Clock } from "lucide-react";
import { getHistory } from "../api";

interface HistoryEvent {
  id: number;
  module_name?: string;
  scan_type?: string;
  ran_at: string;
  success?: boolean;
  changes_detected?: boolean;
  duration_ms?: number;
  error_message?: string;
  event_type: string;
}

export default function History() {
  const [events, setEvents] = useState<HistoryEvent[]>([]);

  useEffect(() => {
    getHistory().then((d) => setEvents(d.events as HistoryEvent[]));
  }, []);

  return (
    <div>
      <h1 className="text-xl font-bold mb-6">History</h1>

      <div className="ho-card p-0">
        <div className="divide-y divide-ho-border/50">
          {events.map((ev, i) => (
            <div key={i} className="flex items-center gap-3 px-4 py-3 hover:bg-ho-accent/5 transition-colors">
              {ev.success === true && <CheckCircle size={14} className="text-green-400 flex-shrink-0" />}
              {ev.success === false && <XCircle size={14} className="text-red-400 flex-shrink-0" />}
              {ev.success === undefined && <Clock size={14} className="text-ho-muted flex-shrink-0" />}

              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium">
                  {ev.event_type === "module_run" && `Module: ${ev.module_name}`}
                  {ev.event_type === "scan" && `Scan: ${ev.scan_type}`}
                </div>
                {ev.error_message && (
                  <div className="text-xs text-red-400 mt-0.5 truncate">{ev.error_message}</div>
                )}
              </div>

              <div className="text-right flex-shrink-0">
                <div className="text-[10px] text-ho-muted">
                  {new Date(ev.ran_at).toLocaleString("en-US", {
                    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
                  })}
                </div>
                {ev.duration_ms !== undefined && (
                  <div className="text-[10px] text-ho-muted">{ev.duration_ms}ms</div>
                )}
              </div>
            </div>
          ))}
          {events.length === 0 && (
            <div className="text-xs text-ho-muted text-center py-8">No history yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
