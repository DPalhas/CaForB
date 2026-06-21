import { AssessmentFormData } from "@/lib/types";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const BARRIERS = [
  { value: "budget", label: "Lack of budget" },
  { value: "talent", label: "Lack of skilled talent" },
  { value: "process", label: "No structured process" },
  { value: "culture", label: "Resistance to change" },
  { value: "time", label: "Insufficient time" },
  { value: "strategy", label: "Unclear strategic direction" },
];

export default function Step5_PainPoints({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Barriers & Context</h2>
        <p className="text-sm text-gray-500 mt-1">
          Understanding your constraints helps generate realistic, actionable recommendations.
        </p>
      </div>

      {/* Main barrier */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          What is your biggest barrier to innovation? <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {BARRIERS.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange("mainBarrier", value)}
              className={`border rounded-lg px-4 py-2.5 text-sm text-left font-medium transition-all
                ${data.mainBarrier === value
                  ? "border-teal-600 bg-teal-50 text-teal-700 ring-2 ring-teal-500"
                  : "border-gray-200 text-gray-700 hover:border-gray-300"
                }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Additional context */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          Anything else you'd like the analysis to consider?
        </label>
        <textarea
          value={data.additionalContext}
          onChange={(e) => onChange("additionalContext", e.target.value)}
          rows={3}
          placeholder="e.g. We recently lost a key product manager, or we are entering a highly regulated market..."
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
        />
      </div>
    </div>
  );
}