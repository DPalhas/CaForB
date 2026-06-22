import OpportunityCard from "./OpportunityCard";

interface Opportunity {
  type: string;
  title: string;
  rationale: string;
  impact: string;
  difficulty: string;
  timeframe: string;
}

interface OpportunitiesListProps {
  opportunities: Opportunity[];
}

export default function OpportunitiesList({ opportunities }: OpportunitiesListProps) {
  if (!opportunities.length) return null;

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        🚀 Innovation Opportunities
      </h2>
      <div className="flex flex-col gap-3">
        {opportunities.map((opp, index) => (
          <OpportunityCard key={index} opportunity={opp} index={index} />
        ))}
      </div>
    </div>
  );
}