import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "primary";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold",
        variant === "primary"
          ? "bg-amber-400 text-stone-950"
          : "bg-stone-900/60 text-stone-300 border border-stone-800",
        className
      )}
      {...props}
    />
  );
}
