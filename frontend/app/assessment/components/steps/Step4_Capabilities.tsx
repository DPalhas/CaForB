import { AssessmentFormData } from "@/lib/types";
import { Slider } from "@/components/ui/slider";
import { Cpu, Users, DollarSign, Layers } from "lucide-react";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string | number) => void;
}

const DIGITAL_MATURITY = [
  { value: "1", label: "Digital Beginner", description: "Mostly manual & legacy systems" },
  { value: "2", label: "Developing", description: "Standard digital tools & cloud apps adopted" },
  { value: "3", label: "Established", description: "Digital-first operational workflows" },
  { value: "4", label: "Advanced AI & Automation", description: "Data-driven, automated & AI-integrated" },
];

const REVENUE_RANGES = [
  { value: "under_1m", label: "Under €1M" },
  { value: "1m_to_10m", label: "€1M – €10M" },
  { value: "10m_to_50m", label: "€10M – €50M" },
  { value: "over_50m", label: "€50M+" },
];

export default function Step4_Capabilities({ data, onChange }: Props) {
  return (
    <div className="space-y-7">
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-950/40 text-purple-300 text-xs font-bold uppercase tracking-wider mb-2 border border-purple-800/40">
          <Cpu className="w-3.5 h-3.5" />
          <span>Section 4 of 5</span>
        </div>
        <h2 className="text-2xl font-bold text-white">Internal Capabilities & Budget</h2>
        <p className="text-sm text-slate-400 mt-1">
          Assess available team bandwidth, digital infrastructure, and innovation budget allocation.
        </p>
      </div>

      {/* Team size */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Innovation Team Size / Resource Allocation <span className="text-purple-400">*</span>
        </label>
        <input
          type="text"
          value={data.teamSize}
          onChange={(e) => onChange("teamSize", e.target.value)}
          placeholder="e.g. 4 dedicated R&D engineers, or 2 part-time innovation leads"
          className="w-full border border-slate-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent shadow-sm"
        />
      </div>

      {/* Digital maturity */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Digital Infrastructure Maturity <span className="text-purple-400">*</span>
        </label>
        <div className="grid sm:grid-cols-2 gap-3">
          {DIGITAL_MATURITY.map(({ value, label, description }) => {
            const isSelected = data.digitalMaturity === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("digitalMaturity", value)}
                className={`border rounded-2xl p-4 text-left transition-all relative ${
                  isSelected
                    ? "border-purple-500 bg-purple-950/40 ring-2 ring-purple-500/30 shadow-sm"
                    : "border-slate-800 hover:border-slate-700 bg-slate-900/40"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-xs font-bold ${isSelected ? "text-purple-300" : "text-slate-200"}`}>
                    {label}
                  </span>
                  <Cpu className={`w-3.5 h-3.5 ${isSelected ? "text-purple-400" : "text-slate-500"}`} />
                </div>
                <div className="text-[11px] text-slate-400">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Revenue range */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Approximate Annual Revenue Range <span className="text-purple-400">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {REVENUE_RANGES.map(({ value, label }) => {
            const isSelected = data.revenueRange === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("revenueRange", value)}
                className={`border rounded-xl p-3 text-center transition-all ${
                  isSelected
                    ? "border-purple-500 bg-purple-950/40 ring-2 ring-purple-500/30 font-bold text-purple-300 shadow-sm"
                    : "border-slate-800 hover:border-slate-700 bg-slate-900/40 text-slate-200 font-medium"
                }`}
              >
                <span className="text-xs">{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Budget percentage slider */}
      <div className="space-y-3 bg-slate-900/40 p-5 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between">
          <div>
            <label className="block text-sm font-semibold text-slate-200">
              Innovation Budget Allocation (% of revenue) <span className="text-purple-400">*</span>
            </label>
            <p className="text-xs text-slate-400">Slide to indicate percentage of turnover dedicated to innovation</p>
          </div>
          <span className="text-lg font-bold text-purple-300 bg-purple-950/40 px-3 py-1 rounded-xl font-mono border border-purple-800/40">
            {data.budgetPercentage ?? 0}%
          </span>
        </div>

        <Slider
          value={[data.budgetPercentage ?? 0]}
          onValueChange={(val) => {
            const num = Array.isArray(val) ? val[0] : val;
            onChange("budgetPercentage", num);
          }}
          min={0}
          max={30}
          step={1}
          className="py-2 cursor-pointer"
        />
        <div className="flex justify-between text-[11px] text-slate-500 font-mono">
          <span>0% (Minimal)</span>
          <span>15% (Industry standard)</span>
          <span>30%+ (Aggressive)</span>
        </div>
      </div>

      {/* Decision Making Structure */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-slate-200">
          Governance & Decision-Making Speed <span className="text-purple-400">*</span>
        </label>
        <div className="relative">
          <select
            value={data.decisionMaking}
            onChange={(e) => onChange("decisionMaking", e.target.value)}
            className="w-full border border-slate-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-slate-900/60 shadow-sm appearance-none cursor-pointer"
          >
            <option value="">Select approval structure...</option>
            <option value="owner_alone">Founder / Managing Director alone (Fastest)</option>
            <option value="small_leadership_team">Small executive committee (1-2 weeks)</option>
            <option value="formal_committee">Formal Board / Governance Committee (Stage-gate approval)</option>
            <option value="varies_by_project">Varies by project budget threshold</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-500">
            <Layers className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
}
