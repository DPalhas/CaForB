import { AssessmentFormData } from "@/lib/types";
import { Slider } from "@/components/ui/slider";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string | number) => void;
}

const DIGITAL_MATURITY = [
  { value: "1", label: "Beginner", description: "Mostly manual processes" },
  { value: "2", label: "Developing", description: "Some digital tools adopted" },
  { value: "3", label: "Established", description: "Digital-first operations" },
  { value: "4", label: "Advanced", description: "Data-driven and automated" },
];

const REVENUE_RANGES = [
  { value: "under_1m", label: "Under €1M" },
  { value: "1m_to_10m", label: "€1M – €10M" },
  { value: "10m_to_50m", label: "€10M – €50M" },
  { value: "over_50m", label: "€50M+" },
];

export default function Step4_Capabilities({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Internal Capabilities</h2>
        <p className="text-sm text-gray-500 mt-1">
          Help us assess the resources and digital readiness available to you.
        </p>
      </div>

      {/* Team size */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          How large is the team driving innovation? <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={data.teamSize}
          onChange={(e) => onChange("teamSize", e.target.value)}
          placeholder="e.g. 3 dedicated people, or 'shared across departments'"
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
        />
      </div>

      {/* Digital maturity */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          How would you rate your company's digital maturity? <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {DIGITAL_MATURITY.map(({ value, label, description }) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange("digitalMaturity", value)}
              className={`border rounded-lg p-3 text-left transition-all
                ${data.digitalMaturity === value
                  ? "border-teal-600 bg-teal-50 ring-2 ring-teal-500"
                  : "border-gray-200 hover:border-gray-300"
                }`}
            >
              <div className="text-sm font-semibold text-gray-800">{label}</div>
              <div className="text-xs text-gray-500">{description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Revenue range — NEW */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          What is your company's approximate annual revenue? <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {REVENUE_RANGES.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange("revenueRange", value)}
              className={`border rounded-lg p-3 text-left transition-all
                ${data.revenueRange === value
                  ? "border-teal-600 bg-teal-50 ring-2 ring-teal-500"
                  : "border-gray-200 hover:border-gray-300"
                }`}
            >
              <div className="text-sm font-semibold text-gray-800">{label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Budget allocation — now a slider */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Budget allocation <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500">
          What percentage of revenue is currently allocated to innovation activities?
        </p>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">0%</span>
          <span className="text-sm font-semibold text-teal-700">{data.budgetPercentage}%</span>
          <span className="text-xs text-gray-400">30%+</span>
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
          className="py-2"
        />
      </div>

      {/* Decision Making Structure */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Decision-making structure *
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Who typically approves new innovation initiatives in your organisation?
        </p>
        <select
          value={data.decisionMaking}
          onChange={(e) => onChange("decisionMaking", e.target.value)}
          className="w-full px-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
        >
          <option value="">Select an option</option>
          <option value="owner_alone">Owner/founder alone</option>
          <option value="small_leadership_team">Small leadership team</option>
          <option value="formal_committee">Formal committee</option>
          <option value="varies_by_project">Varies by project</option>
        </select>
      </div>
    </div>
  );
}