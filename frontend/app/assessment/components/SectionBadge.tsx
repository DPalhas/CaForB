import type { ReactNode } from "react";

interface SectionBadgeProps {
  children: ReactNode;
}

export default function SectionBadge({ children }: SectionBadgeProps) {
  return (
    <div className="inline-flex items-center px-3 py-1 rounded-full bg-amber-950/40 text-amber-300 text-xs font-bold uppercase tracking-wider mb-2 border border-amber-800/40">
      {children}
    </div>
  );
}
