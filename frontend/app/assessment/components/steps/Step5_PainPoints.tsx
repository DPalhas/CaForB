import { AssessmentFormData } from "@/lib/types";
import { AlertTriangle, Check, ShieldAlert, Zap } from "lucide-react";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string | string[]) => void;
}

const BARRIERS = [
  { value: "budget", label: "Financial / Capital Constraints" },
  { value: "talent", label: "Talent & Specialized Skill Gap" },
  { value: "process", label: "Absence of Execution Process" },
  { value: "culture", label: "Cultural Resistance to Change" },
  { value: "time", label: "Lack of Bandwidth / Time" },
  { value: "strategy", label: "Unclear Strategic Focus" },
];

const COMPETITIVE_LEVELS = [
  { value: "low", label: "Low Threat", description: "We are leading or keeping comfortable pace" },
  { value: "medium", label: "Moderate Pressure", description: "Select competitors are moving faster in key niches" },
  { value: "high", label: "High Urgency", description: "Competitors are innovating rapidly & disrupting market" },
];

export default function Step5_PainPoints({ data, onChange }: Props) {
  const toggleBarrier = (value: string) => {
    const current = data.mainBarrier;
    const updated = current.includes(value)
      ? current.filter((b) => b !== value)
      : [...current, value];
    onChange("mainBarrier", updated);
  };

  return (
    <div className="space-y-7">
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950/40 text-purple-300 text-xs font-bold uppercase tracking-wider mb-2 border border-purple-800/40">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Section 5 of 5</span>
        </div>
        <h2 className="text-2xl font-bold text-white">Barriers & Market Context</h2>
        <p className="text-sm text-slate-400 mt-1">
          Identifying your specific friction points ensures the AI designs realistic, high-leverage solutions.
        </p>
      </div>

      {/* Main barriers */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Primary Innovation Barriers <span className="text-purple-400">*</span>
        </label>
        <p className="text-xs text-slate-400">Select all bottlenecks currently affecting your team.</p>
        <div className="grid sm:grid-cols-2 gap-3">
          {BARRIERS.map(({ value, label }) => {
            const isSelected = data.mainBarrier.includes(value);
            return (
              <button
                key={value}
                type="button"
                onClick={() => toggleBarrier(value)}
                className={`border rounded-2xl px-4 py-3.5 text-xs text-left font-semibold transition-all flex items-center gap-3 ${
                  isSelected
                    ? "border-purple-500 bg-purple-950/40 text-purple-300 ring-2 ring-purple-500/30 shadow-sm"
                    : "border-slate-800 text-slate-300 hover:border-slate-700 bg-slate-900/40"
                }`}
              >
                <span className={`w-5 h-5 rounded-lg border flex items-center justify-center flex-shrink-0 transition-colors ${
                  isSelected ? "bg-purple-600 border-purple-600 text-white" : "border-slate-600 bg-slate-800/60"
                }`}>
                  {isSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                </span>
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Competitive pressure */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Competitive Market Urgency <span className="text-purple-400">*</span>
        </label>
        <div className="grid sm:grid-cols-3 gap-3">
          {COMPETITIVE_LEVELS.map(({ value, label, description }) => {
            const isSelected = data.competitivePressure === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("competitivePressure", value)}
                className={`border rounded-2xl p-3.5 text-left transition-all ${
                  isSelected
                    ? "border-purple-500 bg-purple-950/40 ring-2 ring-purple-500/30 shadow-sm"
                    : "border-slate-800 hover:border-slate-700 bg-slate-900/40"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-xs font-bold ${isSelected ? "text-purple-300" : "text-slate-200"}`}>
                    {label}
                  </span>
                  <Zap className={`w-3.5 h-3.5 ${isSelected ? "text-purple-400" : "text-slate-500"}`} />
                </div>
                <div className="text-[11px] text-slate-400 leading-tight">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Additional context */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Additional Strategic Context or Constraints
        </label>
        <textarea
          value={data.additionalContext}
          onChange={(e) => onChange("additionalContext", e.target.value)}
          rows={3}
          placeholder="e.g. Preparing for series B fundraising in 6 months, or restructuring management team..."
          className="w-full border border-slate-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none shadow-sm"
        />
      </div>
    </div>
  );
}
