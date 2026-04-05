import StatusBadge from "./StatusBadge";
import type { RiskItem } from "../types";

interface Props {
  risk: RiskItem;
  onStatusChange?: (id: number, status: string) => void;
}

export default function RiskRow({ risk, onStatusChange }: Props) {
  return (
    <tr className="border-b border-ho-border/50 hover:bg-ho-accent/5 transition-colors">
      <td className="px-4 py-3">
        <StatusBadge level={risk.risk_level} />
      </td>
      <td className="px-4 py-3">
        <div className="font-medium text-sm">{risk.title}</div>
        {risk.description && (
          <div className="text-xs text-ho-muted mt-0.5 line-clamp-1">{risk.description}</div>
        )}
      </td>
      <td className="px-4 py-3 text-xs text-ho-muted">{risk.category}</td>
      <td className="px-4 py-3 text-xs">
        {risk.days_remaining !== null ? (
          <span className={risk.days_remaining < 30 ? "text-red-400 font-medium" : "text-ho-muted"}>
            {risk.days_remaining}d
          </span>
        ) : (
          <span className="text-ho-muted">—</span>
        )}
      </td>
      <td className="px-4 py-3">
        {onStatusChange ? (
          <select
            value={risk.status}
            onChange={(e) => onStatusChange(risk.id, e.target.value)}
            className="bg-ho-card border border-ho-border rounded px-2 py-1 text-xs text-ho-text"
          >
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="accepted">Accepted</option>
          </select>
        ) : (
          <span className="text-xs text-ho-muted">{risk.status}</span>
        )}
      </td>
    </tr>
  );
}
