import { CheckCircle, XCircle, Clock } from "lucide-react";
import type { ModuleRun } from "../types";

interface Props {
  module: ModuleRun;
}

export default function ModuleStatus({ module: mod }: Props) {
  const timeAgo = mod.ran_at
    ? new Date(mod.ran_at).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "Never";

  return (
    <div className="flex items-center gap-3 py-2 px-3 rounded-md hover:bg-ho-card/50 transition-colors">
      {mod.success === true && <CheckCircle size={14} className="text-green-400 flex-shrink-0" />}
      {mod.success === false && <XCircle size={14} className="text-red-400 flex-shrink-0" />}
      {mod.success === null && <Clock size={14} className="text-ho-muted flex-shrink-0" />}
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium font-mono">{mod.module_name}</div>
        <div className="text-[10px] text-ho-muted">{mod.module_type}</div>
      </div>
      <div className="text-right flex-shrink-0">
        <div className="text-[10px] text-ho-muted">{timeAgo}</div>
        {mod.duration_ms !== null && (
          <div className="text-[10px] text-ho-muted">{mod.duration_ms}ms</div>
        )}
      </div>
    </div>
  );
}
