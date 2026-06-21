import { AssessmentFormData, CompanySize } from "@/lib/types";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const SECTORS = [
  "SaaS / Software", "E-commerce", "Fintech", "Healthtech",
  "Manufacturing", "Retail", "Consulting", "Education", "Other",
];

const SIZES: { value: CompanySize; label: string; description: string }[] = [
  { value: "SME", label: "SME", description: "1–50 employees" },
  { value: "Mid", label: "Mid-size", description: "51–250 employees" },
  { value: "Large", label: "Large", description: "250+ employees" },
];

export default function Step1_CompanyProfile({ data, onChange }: Props) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Company Profile</h2>
        <p className="text-sm text-gray-500 mt-1">
          Tell us about your organisation so we can tailor the assessment.
        </p>
      </div>

      {/* Company Name */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          Company name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={data.companyName}
          onChange={(e) => onChange("companyName", e.target.value)}
          placeholder="e.g. Acme Technologies"
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
        />
      </div>

      {/* Sector */}
      <div className="space-y-1">
        <label className="block text-sm font-medium text-gray-700">
          Industry sector <span className="text-red-500">*</span>
        </label>
        <select
          value={data.sector}
          onChange={(e) => onChange("sector", e.target.value)}
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 bg-white"
        >
          <option value="">Select a sector</option>
          {SECTORS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Size */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Company size <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-3 gap-3">
          {SIZES.map(({ value, label, description }) => (
            <button
              key={value}
              type="button"
              onClick={() => onChange("size", value)}
              className={`border rounded-lg p-3 text-left transition-all
                ${data.size === value
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