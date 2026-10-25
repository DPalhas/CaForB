import type { ReactNode } from "react";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
      {icon && (
        <div className="w-12 h-12 rounded-xl bg-stone-900 border border-stone-800 flex items-center justify-center">
          {icon}
        </div>
      )}
      <h2 className="text-xl font-semibold text-white">{title}</h2>
      {description && (
        <p className="text-sm text-stone-400 max-w-sm">{description}</p>
      )}
      {action}
    </div>
  );
}
