interface ScoreCardProps {
  score: number;
}

const getScoreLabel = (score: number) => {
  if (score <= 3) return { label: "Early Stage", color: "text-red-600", bg: "bg-red-50", bar: "bg-red-500" };
  if (score <= 5) return { label: "Developing", color: "text-orange-600", bg: "bg-orange-50", bar: "bg-orange-500" };
  if (score <= 7) return { label: "Established", color: "text-teal-600", bg: "bg-teal-50", bar: "bg-teal-500" };
  return { label: "Advanced", color: "text-green-600", bg: "bg-green-50", bar: "bg-green-500" };
};

export default function ScoreCard({ score }: ScoreCardProps) {
  const { label, color, bg, bar } = getScoreLabel(score);
  const percentage = (score / 10) * 100;

  return (
    <div className={`rounded-2xl border p-6 ${bg}`}>
      <p className="text-sm font-medium text-gray-500 mb-1">Innovation Maturity Score</p>
      <div className="flex items-end gap-3 mb-4">
        <span className={`text-6xl font-bold ${color}`}>{score.toFixed(1)}</span>
        <span className="text-2xl text-gray-400 mb-2">/ 10</span>
        <span className={`mb-2 text-sm font-semibold px-3 py-1 rounded-full ${bg} ${color} border border-current`}>
          {label}
        </span>
      </div>
      {/* Progress bar */}
      <div className="w-full bg-white rounded-full h-3 shadow-inner">
        <div
          className={`h-3 rounded-full transition-all duration-700 ${bar}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between mt-1 text-xs text-gray-400">
        <span>0 — No process</span>
        <span>10 — World class</span>
      </div>
    </div>
  );
}