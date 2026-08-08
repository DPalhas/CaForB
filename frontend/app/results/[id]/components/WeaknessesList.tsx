import { AlertTriangle } from "lucide-react";

interface WeaknessesListProps {
  weaknesses: string[];
}

export default function WeaknessesList({ weaknesses }: WeaknessesListProps) {
  if (!weaknesses.length) return null;

  return (
    <div className="bg-amber-950/30 rounded-3xl border border-amber-800/40 p-6 sm:p-7">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-600/40 flex items-center justify-center text-amber-400">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-amber-200">
            Key Strategic Vulnerabilities & Barriers
          </h2>
          <p className="text-xs text-amber-400/70">Risk areas identified from your operational & process inputs</p>
        </div>
      </div>

      <ul className="space-y-2.5">
        {weaknesses.map((weakness, index) => (
          <li key={index} className="flex items-start gap-3 bg-stone-950/60 p-3.5 rounded-2xl border border-amber-800/40 shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-amber-400 mt-2 flex-shrink-0" />
            <p className="text-sm font-medium text-amber-100 leading-relaxed">{weakness}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
