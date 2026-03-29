import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, string> = {
  requested: "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30",
  reserved: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30",
  executing: "bg-violet-500/15 text-violet-600 dark:text-violet-400 border-violet-500/30",
  completed: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
  failed: "bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30",
  rejected: "bg-zinc-500/15 text-zinc-600 dark:text-zinc-400 border-zinc-500/30",
  insufficient_funds:
    "bg-orange-500/15 text-orange-600 dark:text-orange-400 border-orange-500/30",
  needs_manual_review:
    "bg-fuchsia-500/15 text-fuchsia-600 dark:text-fuchsia-400 border-fuchsia-500/30",
  pending: "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30",
  queued: "bg-sky-500/15 text-sky-600 dark:text-sky-400 border-sky-500/30",
  active: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
  inactive: "bg-zinc-500/15 text-zinc-500 dark:text-zinc-400 border-zinc-500/30",
};

export function StatusBadge({ status }: { status: string }) {
  const key = status.toLowerCase();
  const cls = STATUS_STYLES[key] ?? "bg-muted text-muted-foreground border-border";
  return (
    <Badge
      variant="outline"
      className={cn("font-medium capitalize", cls)}
    >
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
