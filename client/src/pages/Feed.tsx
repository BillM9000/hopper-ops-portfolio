import { useState, useEffect } from "react";
import FeedEntryComponent from "../components/FeedEntry";
import { getFeed } from "../api";
import type { FeedEntry } from "../types";

const TYPES = ["", "status", "incident", "release", "deprecation", "news", "eol"];

export default function Feed() {
  const [entries, setEntries] = useState<FeedEntry[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const params = filter ? `entry_type=${filter}` : "";
    getFeed(params).then((d) => setEntries(d.entries));
  }, [filter]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Feed</h1>
        <div className="flex gap-2 flex-wrap">
          {TYPES.map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`ho-btn-ghost text-xs ${filter === t ? "bg-ho-card text-ho-text" : ""}`}
            >
              {t || "All"}
            </button>
          ))}
        </div>
      </div>

      <div className="ho-card">
        {entries.map((e) => (
          <FeedEntryComponent key={e.id} entry={e} />
        ))}
        {entries.length === 0 && (
          <div className="text-xs text-ho-muted text-center py-8">
            No feed entries — run a refresh to populate
          </div>
        )}
      </div>
    </div>
  );
}
