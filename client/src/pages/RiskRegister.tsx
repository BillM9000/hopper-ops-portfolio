import { useState, useEffect } from "react";
import RiskRow from "../components/RiskRow";
import { getRisks, updateRisk } from "../api";
import type { RiskItem } from "../types";

export default function RiskRegister() {
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [filter, setFilter] = useState("");

  const load = async () => {
    const params = filter ? `risk_level=${filter}` : "";
    const data = await getRisks(params);
    setRisks(data.risks);
  };

  useEffect(() => { load(); }, [filter]);

  const handleStatusChange = async (id: number, status: string) => {
    await updateRisk(id, { status });
    await load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Risk Register</h1>
        <div className="flex gap-2">
          {["", "red", "yellow", "green"].map((level) => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`ho-btn-ghost text-xs ${filter === level ? "bg-ho-card text-ho-text" : ""}`}
            >
              {level || "All"}
            </button>
          ))}
        </div>
      </div>

      <div className="ho-card overflow-hidden p-0">
        <table className="w-full">
          <thead>
            <tr className="border-b border-ho-border text-[10px] text-ho-muted uppercase tracking-wider">
              <th className="px-4 py-3 text-left font-semibold">Risk</th>
              <th className="px-4 py-3 text-left font-semibold">Details</th>
              <th className="px-4 py-3 text-left font-semibold">Category</th>
              <th className="px-4 py-3 text-left font-semibold">Days Left</th>
              <th className="px-4 py-3 text-left font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {risks.map((r) => (
              <RiskRow key={r.id} risk={r} onStatusChange={handleStatusChange} />
            ))}
          </tbody>
        </table>
        {risks.length === 0 && (
          <div className="text-xs text-ho-muted py-8 text-center">No risk items found</div>
        )}
      </div>
    </div>
  );
}
