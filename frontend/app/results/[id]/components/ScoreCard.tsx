import { Award, TrendingUp, ShieldCheck } from "lucide-react";

interface ScoreCardProps {
  score: number;
}

const getScoreLabel = (score: number) => {
  if (score <= 3) return { label: "Early Stage", color: "text-rose-300", bg: "bg-rose-950/40 border-rose-800/40", fill: "#e11d48", bar: "#e11d48" };
  if (score <= 5) return { label: "Developing", color: "text-amber-300", bg: "bg-amber-950/40 border-amber-800/40", fill: "#fb923c", bar: "#fb923c" };
  if (score <= 7) return { label: "Established", color: "text-emerald-300", bg: "bg-emerald-950/40 border-emerald-800/40", fill: "#10b981", bar: "#10b981" };
  return { label: "Advanced Leader", color: "text-yellow-300", bg: "bg-yellow-950/40 border-yellow-800/40", fill: "#fbbf24", bar: "#fbbf24" };
};

export default function ScoreCard({ score }: ScoreCardProps) {
  const { label, color, bg, fill } = getScoreLabel(score);
  const percentage = Math.min(100, Math.max(0, (score / 10) * 100));

  return (
    <div className="glass-card rounded-3xl border border-stone-800/80 p-6 sm:p-8">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        
        {/* Score Circular Metric */}
        <div className="flex items-center gap-6">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-stone-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                strokeWidth="3.5"
                strokeDasharray={`${percentage}, 100`}
                strokeLinecap="round"
                stroke={fill}
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className={`text-3xl font-extrabold tracking-tight ${color}`}>
                {score.toFixed(1)}
              </span>
              <span className="text-[10px] font-mono font-semibold text-stone-500">OUT OF 10</span>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-400">Innovation Index</span>
              <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${bg} ${color}`}>
                {label}
              </span>
            </div>
            <h3 className="text-xl font-bold text-white">Maturity Score</h3>
            <p className="text-xs text-stone-400 max-w-xs mt-1">
              Calculated based on governance structure, digital capability, strategic alignment, and barrier complexity.
            </p>
          </div>
        </div>

        {/* Progress Bar & Scale */}
        <div className="w-full sm:w-64 bg-stone-900/60 p-4 rounded-2xl border border-stone-800/60">
          <div className="flex justify-between items-center text-xs font-semibold text-stone-300 mb-2">
            <span>Current Benchmark</span>
            <span className="font-mono text-amber-400">{percentage.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-stone-800 rounded-full h-2.5 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-1000 ease-out"
              style={{ width: `${percentage}%`, backgroundColor: fill }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-stone-500 mt-2 font-mono">
            <span>0 (Ad-hoc)</span>
            <span>5 (Established)</span>
            <span>10 (Leader)</span>
          </div>
        </div>

      </div>
    </div>
  );
}
