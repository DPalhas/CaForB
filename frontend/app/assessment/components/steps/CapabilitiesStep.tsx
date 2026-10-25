import { AssessmentFormData } from "@/lib/types";
import { Slider } from "@/components/ui/slider";
import SectionBadge from "../SectionBadge";
import SelectField from "../SelectField";

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

export default function CapabilitiesStep({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <SectionBadge>
          Section 4 of 5
        </SectionBadge>
        <h2 className="text-2xl font-bold text-white">Internal Capabilities & Budget</h2>
        <p className="text-sm text-stone-400 mt-1">
          Assess available team bandwidth, digital infrastructure, and innovation budget allocation.
        </p>
      </div>

      {/* Team size */}
      <div className="space-y-2">
        <label htmlFor="teamSize" className="block text-sm font-semibold text-stone-200">
          Innovation Team Size / Resource Allocation <span className="text-amber-400">*</span>
        </label>
        <input
          id="teamSize"
          type="text"
          value={data.teamSize}
          onChange={(e) => onChange("teamSize", e.target.value)}
          placeholder="e.g. 4 dedicated R&D engineers, or 2 part-time innovation leads"
          className="w-full border border-stone-800 rounded-lg px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
        />
      </div>

      {/* Digital maturity */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Digital Infrastructure Maturity <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-2 gap-3">
          {DIGITAL_MATURITY.map(({ value, label, description }) => {
            const isSelected = data.digitalMaturity === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("digitalMaturity", value)}
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
                <div className="text-xs text-stone-400">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Revenue range */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Approximate Annual Revenue Range <span className="text-amber-400">*</span>
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {REVENUE_RANGES.map(({ value, label }) => {
            const isSelected = data.revenueRange === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("revenueRange", value)}
                className={`border rounded-lg p-3 text-center transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 ${
                  isSelected
                    ? "border-amber-500 bg-amber-950/40 ring-2 ring-amber-500/30 font-bold text-amber-300"
                    : "border-stone-800 hover:border-stone-700 bg-stone-900/40 text-stone-200 font-medium"
                }`}
              >
                <span className="text-xs">{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Budget percentage slider */}
      <div className="space-y-3 bg-stone-900/40 p-5 rounded-xl border border-stone-800">
        <div className="flex items-center justify-between">
          <div>
            <label className="block text-sm font-semibold text-stone-200">
              Innovation Budget Allocation (% of revenue) <span className="text-amber-400">*</span>
            </label>
            <p className="text-xs text-stone-400">Slide to indicate percentage of turnover dedicated to innovation</p>
          </div>
          <span className="text-lg font-bold text-amber-300 bg-amber-950/40 px-3 py-1 rounded-lg font-mono border border-amber-800/40">
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
        <div className="flex justify-between text-xs text-stone-500 font-mono">
          <span>0% (Minimal)</span>
          <span>15% (Industry standard)</span>
          <span>30%+ (Aggressive)</span>
        </div>
      </div>

      {/* Decision Making Structure */}
      <div className="space-y-2">
        <label htmlFor="decisionMaking" className="block text-sm font-semibold text-stone-200">
          Governance & Decision-Making Speed <span className="text-amber-400">*</span>
        </label>
        <SelectField
          id="decisionMaking"
          value={data.decisionMaking}
          onChange={(e) => onChange("decisionMaking", e.target.value)}
        >
          <option value="">Select approval structure...</option>
          <option value="owner_alone">Founder / Managing Director alone (Fastest)</option>
          <option value="small_leadership_team">Small executive committee (1-2 weeks)</option>
          <option value="formal_committee">Formal Board / Governance Committee (Stage-gate approval)</option>
          <option value="varies_by_project">Varies by project budget threshold</option>
        </SelectField>
      </div>
    </div>
  );
}
