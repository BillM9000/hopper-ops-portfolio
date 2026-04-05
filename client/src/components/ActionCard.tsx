import clsx from "clsx";
import type { ActionItem } from "../types";

interface Props {
  action: ActionItem;
  onStatusChange?: (id: number, status: string) => void;
}

const PRIORITY_COLORS = {
  critical: "border-l-red-500 bg-red-500/5",
  high: "border-l-yellow-500 bg-yellow-500/5",
  medium: "border-l-ho-accent bg-ho-accent/5",
  low: "border-l-ho-border bg-ho-card",
};

export default function ActionCard({ action, onStatusChange }: Props) {
  return (
    <div className={clsx("border-l-2 rounded-r-lg p-3", PRIORITY_COLORS[action.priority])}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium">{action.title}</div>
          {action.description && (
            <div className="text-xs text-ho-muted mt-1 line-clamp-2">{action.description}</div>
          )}
          <div className="flex items-center gap-3 mt-2 text-[10px] text-ho-muted">
            <span className="uppercase font-semibold">{action.priority}</span>
            {action.source_module && <span>via {action.source_module}</span>}
          </div>
        </div>
        {onStatusChange && action.status !== "done" && (
          <div className="flex gap-1">
            <button
              onClick={() => onStatusChange(action.id, "done")}
              className="ho-btn-ghost text-xs text-green-400 hover:bg-green-500/10"
            >
              Done
            </button>
            <button
              onClick={() => onStatusChange(action.id, "dismissed")}
              className="ho-btn-ghost text-xs"
            >
              Dismiss
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
