import { RefreshCw } from "lucide-react";
import clsx from "clsx";

interface Props {
  onClick: () => void;
  loading: boolean;
  label?: string;
}

export default function RefreshButton({ onClick, loading, label = "Refresh" }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="ho-btn-primary flex items-center gap-1.5"
    >
      <RefreshCw size={14} className={clsx(loading && "animate-spin")} />
      {loading ? "Running..." : label}
    </button>
  );
}
