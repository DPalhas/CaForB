import { AssessmentFormData, CompanySize } from "@/lib/types";
import { Building2, Globe2, Users2, ShieldAlert } from "lucide-react";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const SECTORS = [
  "Agriculture, Forestry & Fishing",
  "Mining & Extraction",
  "Manufacturing",
  "Construction",
  "Energy & Utilities",
  "Retail & Wholesale Trade",
  "E-commerce",
  "Transportation & Logistics",
  "Hospitality & Tourism",
  "Information Technology",
  "SaaS / Software",
  "Telecommunications",
  "Fintech",
  "Financial Services",
  "Insurance",
  "Real Estate",
  "Professional & Consulting Services",
  "Legal Services",
  "Education",
  "Healthtech",
  "Healthcare & Medical",
  "Pharmaceuticals & Biotech",
  "Arts, Entertainment & Media",
  "Public Administration",
  "Nonprofit / NGO",
  "Other",
];

const SIZES: { value: CompanySize; label: string; description: string }[] = [
  { value: "Micro", label: "Micro", description: "1–9 employees" },
  { value: "Small", label: "Small", description: "10–49 employees" },
  { value: "Medium", label: "Medium", description: "50–249 employees" },
  { value: "Large", label: "Large", description: "250+ employees" },
];

const REGULATORY_LEVELS: { value: string; label: string; description: string }[] = [
  { value: "low", label: "Low Oversight", description: "Minimal compliance, typical in standard software" },
  { value: "medium", label: "Moderate", description: "Standard industry regulations & data rules" },
  { value: "high", label: "Heavily Regulated", description: "Strict oversight: Finance, Health, Energy" },
];

export default function Step1_CompanyProfile({ data, onChange }: Props) {
  return (
    <div className="space-y-7">
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/40 text-amber-300 text-xs font-bold uppercase tracking-wider mb-2 border border-amber-800/40">
          <Building2 className="w-3.5 h-3.5" />
          <span>Section 1 of 5</span>
        </div>
        <h2 className="text-2xl font-bold text-white">Company Profile</h2>
        <p className="text-sm text-stone-400 mt-1">
          Provide your company baseline so the AI can calibrate industry context and benchmarks.
        </p>
      </div>

      {/* Company Name */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Company Name <span className="text-amber-400">*</span>
        </label>
        <div className="relative">
          <input
            type="text"
            value={data.companyName}
            onChange={(e) => onChange("companyName", e.target.value)}
            placeholder="e.g. Acme Innovations Corp"
            className="w-full border border-stone-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent shadow-sm"
          />
        </div>
      </div>

      {/* Sector */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Industry Sector <span className="text-amber-400">*</span>
        </label>
        <div className="relative">
          <select
            value={data.sector}
            onChange={(e) => onChange("sector", e.target.value)}
            className="w-full border border-stone-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-stone-900/60 shadow-sm appearance-none cursor-pointer"
          >
            <option value="">Select your sector...</option>
            {SECTORS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-stone-500">
            <Globe2 className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Size */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Company Size <span className="text-amber-400">*</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {SIZES.map(({ value, label, description }) => {
            const isSelected = data.size === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("size", value)}
                className={`border rounded-2xl p-4 text-left transition-all relative ${
                  isSelected
                    ? "border-amber-500 bg-amber-950/40 ring-2 ring-amber-500/30 shadow-sm text-amber-300"
                    : "border-stone-800 hover:border-stone-700 bg-stone-900/40 text-stone-300"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-sm font-bold ${isSelected ? "text-amber-300" : "text-stone-200"}`}>
                    {label}
                  </span>
                  <Users2 className={`w-4 h-4 ${isSelected ? "text-amber-400" : "text-stone-500"}`} />
                </div>
                <div className="text-xs text-stone-400">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Regulatory environment */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Industry Regulatory Environment <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-3 gap-3">
          {REGULATORY_LEVELS.map(({ value, label, description }) => {
            const isSelected = data.regulatoryEnvironment === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("regulatoryEnvironment", value)}
                className={`border rounded-2xl p-3.5 text-left transition-all ${
                  isSelected
                    ? "border-amber-500 bg-amber-950/40 ring-2 ring-amber-500/30 shadow-sm text-amber-300"
                    : "border-stone-800 hover:border-stone-700 bg-stone-900/40 text-stone-300"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-xs font-bold ${isSelected ? "text-amber-300" : "text-stone-200"}`}>
                    {label}
                  </span>
                  <ShieldAlert className={`w-3.5 h-3.5 ${isSelected ? "text-amber-400" : "text-stone-500"}`} />
                </div>
                <div className="text-[11px] text-stone-400 leading-tight">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Company Description */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Brief Business Activity Overview <span className="text-amber-400">*</span>
        </label>
        <textarea
          value={data.companyDescription}
          onChange={(e) => onChange("companyDescription", e.target.value)}
          placeholder="e.g. We develop B2B software for supply chain tracking with 40 active enterprise clients..."
          rows={3}
          className="w-full px-4 py-3 text-sm font-medium border border-stone-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none shadow-sm"
        />
      </div>
    </div>
  );
}