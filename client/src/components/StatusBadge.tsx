import clsx from "clsx";

interface Props {
  level: "red" | "yellow" | "green" | string;
  label?: string;
  size?: "sm" | "md";
}

export default function StatusBadge({ level, label, size = "sm" }: Props) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full font-semibold",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
        level === "red" && "bg-red-500/20 text-red-400",
        level === "yellow" && "bg-yellow-500/20 text-yellow-400",
        level === "green" && "bg-green-500/20 text-green-400",
      )}
    >
      <span
        className={clsx(
          "w-1.5 h-1.5 rounded-full",
          level === "red" && "bg-red-400",
          level === "yellow" && "bg-yellow-400",
          level === "green" && "bg-green-400",
        )}
      />
      {label || level}
    </span>
  );
}
