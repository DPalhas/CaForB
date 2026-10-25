import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-xl border border-stone-800/80 bg-stone-900/60 shadow-sm",
        className
      )}
      {...props}
    />
  );
}
