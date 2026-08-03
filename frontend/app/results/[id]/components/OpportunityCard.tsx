"use client";

import { useState } from "react";
import { ChevronDown, Zap, Target, Clock, ShieldCheck, Flag } from "lucide-react";

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
  const v = value.toLowerCase();
  if (v === "high" || v === "radical") return "bg-purple-950/40 text-purple-300 border-purple-800/40";
  if (v === "medium" || v === "strategic") return "bg-indigo-950/40 text-indigo-300 border-indigo-800/40";
  if (v === "low" || v === "incremental") return "bg-cyan-950/40 text-cyan-300 border-cyan-800/40";
  return "bg-slate-900/60 text-slate-300 border-slate-800/60";
};

const tagBgPill = (value: string) => {
  const v = value.toLowerCase();
  if (v === "high" || v === "radical") return "bg-purple-950/60 text-purple-300";
  if (v === "medium" || v === "strategic") return "bg-indigo-950/60 text-indigo-300";
  if (v === "low" || v === "incremental") return "bg-cyan-950/60 text-cyan-300";
  return "bg-slate-800/60 text-slate-300";
};

export default function OpportunityCard({ opportunity, index }: OpportunityCardProps) {
  const [expanded, setExpanded] = useState(false);
  const hasExecutionPlan = !!opportunity.executionPlan;

  return (
    <div className="glass-card rounded-3xl border border-slate-800/80 shadow-md hover:shadow-xl hover:shadow-purple-500/5 transition-all duration-300 overflow-hidden">
      <div className="p-6 sm:p-7">
        
        {/* Card Header */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-xl bg-purple-950/60 text-purple-400 font-mono text-xs font-bold flex items-center justify-center flex-shrink-0 border border-purple-800/40 shadow-sm">
              #{index + 1}
            </span>
            <div>
              <span className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border mb-1 inline-block ${tagColor(opportunity.type)}`}>
                {opportunity.type} Opportunity
              </span>
              <h3 className="text-lg font-bold text-white leading-snug">{opportunity.title}</h3>
            </div>
          </div>
        </div>

        {/* Rationale Text */}
        <p className="text-sm text-slate-300 leading-relaxed mb-6">
          {opportunity.rationale}
        </p>

        {/* Impact, Difficulty, Timeframe badges */}
        <div className="flex flex-wrap items-center gap-2.5 pt-4 border-t border-slate-800/60">
          <div className="flex items-center gap-1.5 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800/60 text-xs">
            <span className="text-slate-400 font-medium">Impact:</span>
            <span className={`font-bold capitalize ${tagBgPill(opportunity.impact)} px-2 py-0.5 rounded-md`}>
              {opportunity.impact}
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800/60 text-xs">
            <span className="text-slate-400 font-medium">Difficulty:</span>
            <span className={`font-bold capitalize ${tagBgPill(opportunity.difficulty)} px-2 py-0.5 rounded-md`}>
              {opportunity.difficulty}
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800/60 text-xs font-medium text-slate-300 ml-auto">
            <Clock className="w-3.5 h-3.5 text-purple-400" />
            <span>{opportunity.timeframe}</span>
          </div>
        </div>

        {/* Expandable Execution Roadmap */}
        {hasExecutionPlan && (
          <div className="mt-5 pt-4 border-t border-slate-800/60">
            <button
              onClick={() => setExpanded(!expanded)}
              className="w-full py-2.5 px-4 rounded-xl bg-purple-950/40 hover:bg-purple-950/60 border border-purple-800/40 text-xs font-bold text-purple-300 flex items-center justify-between transition group"
            >
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-purple-400" />
                <span>{expanded ? "Hide Execution Roadmap" : "View Detailed Execution Roadmap"}</span>
              </div>
              <ChevronDown className={`w-4 h-4 text-purple-400 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`} />
            </button>

            {expanded && (
              <div className="mt-5 space-y-5 bg-slate-900/60 p-5 rounded-2xl border border-slate-800/60 step-fade">

                {/* Immediate Actions */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-1.5">
                    <Target className="w-3.5 h-3.5 text-purple-400" />
                    <span>Immediate Action Steps</span>
                  </h4>
                  <ul className="space-y-2">
                    {opportunity.executionPlan!.firstActions.map((action, i) => (
                      <li key={i} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/60">
                        <span className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 flex-shrink-0" />
                        <span className="leading-relaxed">{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Resources Needed */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-2">Required Resources</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {opportunity.executionPlan!.resourcesNeeded.map((resource, i) => (
                      <span key={i} className="text-xs font-semibold bg-slate-950/60 text-slate-300 px-3 py-1 rounded-lg border border-slate-800/60 shadow-2xs">
                        {resource}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Success Metric */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-1.5 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                    <span>Success Metric (KPI)</span>
                  </h4>
                  <p className="text-xs font-semibold text-purple-300 bg-purple-950/40 px-3 py-2 rounded-xl border border-purple-800/40">
                    {opportunity.executionPlan!.successMetric}
                  </p>
                </div>

                {/* Milestones */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-2 flex items-center gap-1.5">
                    <Flag className="w-3.5 h-3.5 text-purple-400" />
                    <span>Key Timeline Milestones</span>
                  </h4>
                  <ul className="space-y-2">
                    {opportunity.executionPlan!.milestones.map((milestone, i) => (
                      <li key={i} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/60">
                        <span className="text-purple-400 font-mono font-bold">M{i+1}:</span>
                        <span className="leading-relaxed">{milestone}</span>
                      </li>
                    ))}
                  </ul>
                </div>

              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
