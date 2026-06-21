import { AssessmentFormData } from "@/lib/types";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const PROCESS_OPTIONS = [
  { value: "none", label: "No formal process", description: "Innovation happens ad-hoc" },
  { value: "informal", label: "Informal", description: "Some practices but not documented" },
  { value: "partial", label: "Partially structured", description: "Some formal processes exist" },
  { value: "formal", label: "Fully structured", description: "Documented and governed process" },
];

export default function Step2_InnovationState({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Current Innovation State</h2>
        <p className="text-sm text-gray-500 mt-1">
          Help us understand how your company currently approaches innovation.
        </p>
      </div>

      {/* Innovation process */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          How would you describe your current innovation process? <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {PROCESS_OPTIONS.map(({ value, label, description }) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange("innovationProcess", value)}
              className={`border rounded-lg p-3 text-left transition-all
                ${data.innovationProcess === value
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

      {/* Past initiatives */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          Describe any recent innovation initiatives or experiments
        </label>
        <p className="text-xs text-gray-400">
          Why this matters: past initiatives reveal your company's innovation DNA and risk appetite.
        </p>
        <textarea
          value={data.pastInitiatives}
          onChange={(e) => onChange("pastInitiatives", e.target.value)}
          rows={3}
          placeholder="e.g. We launched a new product line last year but it didn't gain traction..."
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
        />
      </div>
    </div>
  );
}