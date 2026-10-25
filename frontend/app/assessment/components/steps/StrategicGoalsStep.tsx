import { AssessmentFormData } from "@/lib/types";
import SectionBadge from "../SectionBadge";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const HORIZONS = [
  { value: "short", label: "Short-Term", description: "0–12 months target" },
  { value: "medium", label: "Medium-Term", description: "1–3 years target" },
  { value: "long", label: "Long-Term", description: "3+ years transformational" },
];

const RISK_APPETITES = [
  { value: "conservative", label: "Conservative", description: "Proven, low-disruption changes with fast ROI" },
  { value: "balanced", label: "Balanced", description: "Open to moderate risk if upside justifies investment" },
  { value: "bold", label: "Bold", description: "Willing to make transformative bets with higher risk" },
];

const STRATEGIC_PRIORITIES = [
  { value: "growth", label: "Revenue & Market Growth", description: "Expand market share & launch new verticals" },
  { value: "efficiency", label: "Operational Efficiency", description: "Automate processes & optimize unit economics" },
  { value: "market_defense", label: "Market Defense", description: "Protect core business against emerging competitors" },
  { value: "diversification", label: "Business Model Diversification", description: "Explore new revenue channels & product lines" },
];

export default function StrategicGoalsStep({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <SectionBadge>
          Section 3 of 5
        </SectionBadge>
        <h2 className="text-2xl font-bold text-white">Strategic Goals & Risk Profile</h2>
        <p className="text-sm text-stone-400 mt-1">
          Align innovation initiatives with your corporate strategic agenda and risk threshold.
        </p>
      </div>

      {/* Strategic goals text */}
      <div className="space-y-2">
        <label htmlFor="strategicGoals" className="block text-sm font-semibold text-stone-200">
          Primary Corporate Strategic Goals <span className="text-amber-400">*</span>
        </label>
        <textarea
          id="strategicGoals"
          value={data.strategicGoals}
          onChange={(e) => onChange("strategicGoals", e.target.value)}
          rows={3}
          placeholder="e.g. Increase customer retention by 15%, launch an AI-assisted service line, enter LATAM market..."
          className="w-full border border-stone-800 rounded-lg px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none"
        />
      </div>

      {/* Strategic priority */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Top Strategic Priority <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-2 gap-3">
          {STRATEGIC_PRIORITIES.map(({ value, label, description }) => {
            const isSelected = data.strategicPriority === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("strategicPriority", value)}
                className={`border rounded-xl p-4 text-left transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 relative ${
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

      {/* Time horizon */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Target Time Horizon <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-3 gap-3">
          {HORIZONS.map(({ value, label, description }) => {
            const isSelected = data.timeHorizon === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("timeHorizon", value)}
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
                <div className="text-xs text-stone-400">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Risk appetite */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Organizational Risk Appetite <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-3 gap-3">
          {RISK_APPETITES.map(({ value, label, description }) => {
            const isSelected = data.riskAppetite === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("riskAppetite", value)}
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
    </div>
  );
}
