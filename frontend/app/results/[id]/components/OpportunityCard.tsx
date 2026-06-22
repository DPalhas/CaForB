interface Opportunity {
  type: string;
  title: string;
  rationale: string;
  impact: string;
  difficulty: string;
  timeframe: string;
}

interface OpportunityCardProps {
  opportunity: Opportunity;
  index: number;
}

const tagColor = (value: string) => {
  const map: Record<string, string> = {
    high: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-700",
    low: "bg-gray-100 text-gray-600",
    radical: "bg-purple-100 text-purple-700",
    incremental: "bg-blue-100 text-blue-700",
  };
  return map[value.toLowerCase()] ?? "bg-gray-100 text-gray-600";
};

export default function OpportunityCard({ opportunity, index }: OpportunityCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3">
          <span className="w-7 h-7 rounded-full bg-teal-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">
            {index + 1}
          </span>
          <h3 className="text-sm font-semibold text-gray-800">{opportunity.title}</h3>
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-full flex-shrink-0 capitalize ${tagColor(opportunity.type)}`}>
          {opportunity.type}
        </span>
      </div>

      <p className="text-sm text-gray-600 leading-relaxed mb-4 pl-10">{opportunity.rationale}</p>

      <div className="flex flex-wrap gap-2 pl-10">
        <span className="text-xs text-gray-500">Impact:</span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${tagColor(opportunity.impact)}`}>
          {opportunity.impact}
        </span>
        <span className="text-xs text-gray-500 ml-2">Difficulty:</span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${tagColor(opportunity.difficulty)}`}>
          {opportunity.difficulty}
        </span>
        <span className="text-xs text-gray-500 ml-2">⏱ {opportunity.timeframe}</span>
      </div>
    </div>
  );
}