import { AssessmentFormData } from "@/lib/types";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const DIGITAL_MATURITY = [
  { value: "1", label: "Beginner", description: "Mostly manual processes" },
  { value: "2", label: "Developing", description: "Some digital tools adopted" },
  { value: "3", label: "Established", description: "Digital-first operations" },
  { value: "4", label: "Advanced", description: "Data-driven and automated" },
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
    </div>
  );
}