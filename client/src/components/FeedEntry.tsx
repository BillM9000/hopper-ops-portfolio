import { ExternalLink } from "lucide-react";
import clsx from "clsx";
import type { FeedEntry as FeedEntryType } from "../types";

interface Props {
  entry: FeedEntryType;
}

const TYPE_COLORS: Record<string, string> = {
  status: "text-green-400",
  incident: "text-red-400",
  release: "text-blue-400",
  deprecation: "text-yellow-400",
  news: "text-ho-teal",
  interesting: "text-ho-gold",
  eol: "text-red-400",
};

export default function FeedEntryComponent({ entry }: Props) {
  const timeAgo = entry.created_at
    ? new Date(entry.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div className="flex gap-3 py-3 border-b border-ho-border/50 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={clsx("text-[10px] font-semibold uppercase", TYPE_COLORS[entry.entry_type] || "text-ho-muted")}>
            {entry.entry_type}
          </span>
          <span className="text-[10px] text-ho-muted">{timeAgo}</span>
        </div>
        <div className="text-sm font-medium mt-0.5">{entry.title}</div>
        {entry.body && (
          <div className="text-xs text-ho-muted mt-0.5 line-clamp-2">{entry.body}</div>
        )}
      </div>
      {entry.source_url && (
        <a
          href={entry.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-ho-muted hover:text-ho-accent-light transition-colors flex-shrink-0"
        >
          <ExternalLink size={14} />
        </a>
      )}
    </div>
  );
}
