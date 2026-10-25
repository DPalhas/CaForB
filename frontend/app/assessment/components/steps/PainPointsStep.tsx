import { AssessmentFormData } from "@/lib/types";
import { Check } from "lucide-react";
import SectionBadge from "../SectionBadge";

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

export default function PainPointsStep({ data, onChange }: Props) {
  const toggleBarrier = (value: string) => {
    const current = data.mainBarrier;
    const updated = current.includes(value)
      ? current.filter((b) => b !== value)
      : [...current, value];
    onChange("mainBarrier", updated);
  };

  return (
    <div className="space-y-6">
      <div>
        <SectionBadge>
          Section 5 of 5
        </SectionBadge>
        <h2 className="text-2xl font-bold text-white">Barriers & Market Context</h2>
        <p className="text-sm text-stone-400 mt-1">
          Identifying your specific friction points ensures the AI designs realistic, high-leverage solutions.
        </p>
      </div>

      {/* Main barriers */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Primary Innovation Barriers <span className="text-amber-400">*</span>
        </label>
        <p className="text-xs text-stone-400">Select all bottlenecks currently affecting your team.</p>
        <div className="grid sm:grid-cols-2 gap-3">
          {BARRIERS.map(({ value, label }) => {
            const isSelected = data.mainBarrier.includes(value);
            return (
              <button
                key={value}
                type="button"
                onClick={() => toggleBarrier(value)}
                className={`border rounded-xl px-4 py-3 text-xs text-left font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 flex items-center gap-3 ${
                  isSelected
                    ? "border-amber-500 bg-amber-950/40 text-amber-300 ring-2 ring-amber-500/30"
                    : "border-stone-800 text-stone-300 hover:border-stone-700 bg-stone-900/40"
                }`}
              >
                <span className={`w-5 h-5 rounded-lg border flex items-center justify-center flex-shrink-0 transition-colors ${
                  isSelected ? "bg-amber-600 border-amber-600 text-white" : "border-stone-600 bg-stone-800/60"
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
        <label className="block text-sm font-semibold text-stone-200">
          Competitive Market Urgency <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-3 gap-3">
          {COMPETITIVE_LEVELS.map(({ value, label, description }) => {
            const isSelected = data.competitivePressure === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("competitivePressure", value)}
                className={`border rounded-xl p-4 text-left transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 ${
                  isSelected
                    ? "border-amber-500 bg-amber-950/40 ring-2 ring-amber-500/30"
                    : "border-stone-800 hover:border-stone-700 bg-stone-900/40"
                }`}
              >
                <div className="mb-1">
                  <span className={`text-xs font-bold ${isSelected ? "text-amber-300" : "text-stone-200"}`}>
                    {label}
                  </span>
                </div>
                <div className="text-xs text-stone-400 leading-tight">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Additional context */}
      <div className="space-y-2">
        <label htmlFor="additionalContext" className="block text-sm font-semibold text-stone-200">
          Additional Strategic Context or Constraints
        </label>
        <textarea
          id="additionalContext"
          value={data.additionalContext}
          onChange={(e) => onChange("additionalContext", e.target.value)}
          rows={3}
          placeholder="e.g. Preparing for series B fundraising in 6 months, or restructuring management team..."
          className="w-full border border-stone-800 rounded-lg px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none"
        />
      </div>
    </div>
  );
}
