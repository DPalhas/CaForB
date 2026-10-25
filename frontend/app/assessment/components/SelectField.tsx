import type { ReactNode, ChangeEvent } from "react";
import { ChevronDown } from "lucide-react";

interface SelectFieldProps {
  id: string;
  value: string;
  onChange: (e: ChangeEvent<HTMLSelectElement>) => void;
  children: ReactNode;
}

export default function SelectField({
  id,
  value,
  onChange,
  children,
}: SelectFieldProps) {
  return (
    <div className="relative">
      <select
        id={id}
        value={value}
        onChange={onChange}
        className="w-full border border-stone-800 rounded-lg px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-stone-900/60 appearance-none cursor-pointer"
      >
        {children}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-stone-500">
        <ChevronDown className="w-4 h-4" />
      </div>
    </div>
  );
}
