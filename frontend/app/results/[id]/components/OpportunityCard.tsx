"use client";

import { useState } from "react";

interface ExecutionPlan {
  firstActions: string[];
  resourcesNeeded: string[];
  successMetric: string;
  milestones: string[];
}

interface Opportunity {
  type: string;
  title: string;
  rationale: string;
  executionPlan?: ExecutionPlan;
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
  const [expanded, setExpanded] = useState(false);
  const hasExecutionPlan = !!opportunity.executionPlan;

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

      <div className="flex flex-wrap gap-2 pl-10 mb-4">
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

      {hasExecutionPlan && (
        <div className="pl-10">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs font-semibold text-teal-700 hover:text-teal-800 flex items-center gap-1.5 transition"
          >
            <span className={`transition-transform ${expanded ? "rotate-90" : ""}`}>▶</span>
            {expanded ? "Hide execution plan" : "How to execute"}
          </button>

          {expanded && (
            <div className="mt-4 flex flex-col gap-4 border-t border-gray-100 pt-4">

              <div>
                <p className="text-xs font-semibold text-gray-700 mb-2">🎯 First Actions</p>
                <ul className="flex flex-col gap-1.5">
                  {opportunity.executionPlan!.firstActions.map((action, i) => (
                    <li key={i} className="text-xs text-gray-600 leading-relaxed flex gap-2">
                      <span className="text-teal-500">•</span>
                      {action}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-700 mb-2">🧰 Resources Needed</p>
                <div className="flex flex-wrap gap-1.5">
                  {opportunity.executionPlan!.resourcesNeeded.map((resource, i) => (
                    <span key={i} className="text-xs bg-gray-50 text-gray-600 px-2 py-1 rounded-lg border border-gray-100">
                      {resource}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-700 mb-1.5">📊 Success Metric</p>
                <p className="text-xs text-teal-700 font-medium bg-teal-50 px-3 py-2 rounded-lg border border-teal-100">
                  {opportunity.executionPlan!.successMetric}
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-700 mb-2">🗓 Milestones</p>
                <ul className="flex flex-col gap-1.5">
                  {opportunity.executionPlan!.milestones.map((milestone, i) => (
                    <li key={i} className="text-xs text-gray-600 leading-relaxed flex gap-2">
                      <span className="text-teal-500 font-mono">→</span>
                      {milestone}
                    </li>
                  ))}
                </ul>
              </div>

            </div>
          )}
        </div>
      )}
    </div>
  );
}