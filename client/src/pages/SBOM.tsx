import { useState, useEffect } from "react";
import StatusBadge from "../components/StatusBadge";
import { getSbom } from "../api";
import type { Component } from "../types";

export default function SBOM() {
  const [components, setComponents] = useState<Component[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const params = filter ? `category=${filter}` : "";
    getSbom(params).then((d) => setComponents(d.components));
  }, [filter]);

  const categories = [...new Set(components.map((c) => c.category))];

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <h1 className="text-xl font-bold">Software Bill of Materials</h1>
          <p className="text-xs text-ho-muted mt-0.5">{components.length} components tracked</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilter("")}
            className={`ho-btn-ghost text-xs ${filter === "" ? "bg-ho-card text-ho-text" : ""}`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`ho-btn-ghost text-xs ${filter === cat ? "bg-ho-card text-ho-text" : ""}`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="ho-card overflow-hidden p-0 overflow-x-auto">
        <table className="w-full min-w-[700px]">
          <thead>
            <tr className="border-b border-ho-border text-[10px] text-ho-muted uppercase tracking-wider">
              <th className="px-4 py-3 text-left font-semibold">Component</th>
              <th className="px-4 py-3 text-left font-semibold">Version</th>
              <th className="px-4 py-3 text-left font-semibold">Category</th>
              <th className="px-4 py-3 text-left font-semibold">EOL Date</th>
              <th className="px-4 py-3 text-left font-semibold">Days Left</th>
              <th className="px-4 py-3 text-left font-semibold">Risk</th>
              <th className="px-4 py-3 text-left font-semibold">Project</th>
            </tr>
          </thead>
          <tbody>
            {components.map((c) => (
              <tr key={c.id} className="border-b border-ho-border/50 hover:bg-ho-accent/5 transition-colors">
                <td className="px-4 py-3">
                  <span className="text-sm font-medium font-mono">{c.name}</span>
                </td>
                <td className="px-4 py-3 text-xs font-mono text-ho-muted">{c.current_version || "—"}</td>
                <td className="px-4 py-3 text-xs text-ho-muted">{c.category}</td>
                <td className="px-4 py-3 text-xs text-ho-muted">{c.eol_date || "—"}</td>
                <td className="px-4 py-3 text-xs">
                  {c.days_remaining !== null ? (
                    <span className={c.days_remaining < 90 ? "text-red-400 font-medium" : "text-ho-muted"}>
                      {c.days_remaining}d
                    </span>
                  ) : (
                    <span className="text-ho-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3"><StatusBadge level={c.risk_level} /></td>
                <td className="px-4 py-3 text-xs text-ho-muted">{c.project || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
