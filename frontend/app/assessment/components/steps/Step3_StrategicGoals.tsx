import { AssessmentFormData } from "@/lib/types";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const HORIZONS = [
  { value: "short", label: "Short-term", description: "0–12 months" },
  { value: "medium", label: "Medium-term", description: "1–3 years" },
  { value: "long", label: "Long-term", description: "3+ years" },
];

export default function Step3_StrategicGoals({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Strategic Goals</h2>
        <p className="text-sm text-gray-500 mt-1">
          Define where you want to take your business through innovation.
        </p>
      </div>

      {/* Strategic goals */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          What are your primary strategic goals? <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-400">
          Why this matters: aligning innovation to strategy is the most critical factor for sustained growth.
        </p>
        <textarea
          value={data.strategicGoals}
          onChange={(e) => onChange("strategicGoals", e.target.value)}
          rows={3}
          placeholder="e.g. Expand into European markets, reduce churn by 20%, launch a new product vertical..."
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
        />
      </div>

      {/* Time horizon */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          What is your primary planning horizon? <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-3 gap-3">
          {HORIZONS.map(({ value, label, description }) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange("timeHorizon", value)}
              className={`border rounded-lg p-3 text-left transition-all
                ${data.timeHorizon === value
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
    </div>
  );
}