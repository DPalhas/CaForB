import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoadingStateProps {
  label?: string;
  className?: string;
}

export function LoadingState({ label, className }: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-16",
        className
      )}
    >
      <Loader2 className="w-6 h-6 animate-spin text-amber-400" />
      {label && <p className="text-sm text-stone-400">{label}</p>}
    </div>
  );
}
