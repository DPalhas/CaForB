import { CheckSquare, User, Clock } from "lucide-react";

interface NextStep {
  action: string;
  owner: string;
  timeframe: string;
}

interface NextStepsListProps {
  steps: NextStep[];
}

export default function NextStepsList({ steps }: NextStepsListProps) {
  if (!steps.length) return null;

  return (
    <div className="bg-gradient-to-br from-purple-950/80 via-slate-900 to-slate-950 rounded-3xl p-7 text-white shadow-xl shadow-purple-950/20 border border-purple-800/40">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-400">
          <CheckSquare className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Immediate Executive Next Steps
          </h2>
          <p className="text-xs text-slate-400">Prioritized implementation roadmap for leadership alignment</p>
        </div>
      </div>

      <ol className="space-y-4">
        {steps.map((step, index) => (
          <li key={index} className="bg-slate-900/80 rounded-2xl p-5 border border-slate-800/80 hover:border-purple-500/40 transition flex items-start gap-4">
            <span className="w-7 h-7 rounded-xl bg-gradient-to-r from-purple-400 to-indigo-400 text-slate-950 font-extrabold text-xs flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md">
              {index + 1}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-100 leading-relaxed">{step.action}</p>
              <div className="flex flex-wrap gap-2.5 mt-3">
                <span className="text-xs font-semibold text-purple-300 bg-purple-950/80 px-3 py-1 rounded-lg border border-purple-800/60 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-purple-400" />
                  <span>{step.owner}</span>
                </span>
                <span className="text-xs font-semibold text-slate-300 bg-slate-800/80 px-3 py-1 rounded-lg border border-slate-700/60 flex items-center gap-1.5 font-mono">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  <span>{step.timeframe}</span>
                </span>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
