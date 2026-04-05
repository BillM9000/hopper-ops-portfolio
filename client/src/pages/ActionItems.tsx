import { useState, useEffect } from "react";
import ActionCard from "../components/ActionCard";
import { getActions, updateAction } from "../api";
import type { ActionItem } from "../types";

export default function ActionItems() {
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [filter, setFilter] = useState("open");

  const load = async () => {
    const params = filter ? `status=${filter}` : "";
    const data = await getActions(params);
    setActions(data.actions);
  };

  useEffect(() => { load(); }, [filter]);

  const handleStatusChange = async (id: number, status: string) => {
    await updateAction(id, { status });
    await load();
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <h1 className="text-xl font-bold">Action Items</h1>
        <div className="flex gap-2 flex-wrap">
          {["open", "in_progress", "done", "dismissed", ""].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`ho-btn-ghost text-xs ${filter === s ? "bg-ho-card text-ho-text" : ""}`}
            >
              {s || "All"}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        {actions.map((a) => (
          <ActionCard key={a.id} action={a} onStatusChange={handleStatusChange} />
        ))}
        {actions.length === 0 && (
          <div className="ho-card text-xs text-ho-muted text-center py-8">
            No action items found
          </div>
        )}
      </div>
    </div>
  );
}
