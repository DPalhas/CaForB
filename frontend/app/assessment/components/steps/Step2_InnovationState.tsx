import { AssessmentFormData } from "@/lib/types";
import { Compass, Lightbulb, MessageSquare } from "lucide-react";

interface Props {
  data: AssessmentFormData;
  onChange: (field: keyof AssessmentFormData, value: string) => void;
}

const PROCESS_OPTIONS = [
  { value: "none", label: "No Formal Process", description: "Innovation happens ad-hoc when urgent problems arise" },
  { value: "informal", label: "Informal Practices", description: "Some team initiatives exist but are undocumented" },
  { value: "partial", label: "Partially Structured", description: "Stage-gate or agile process used in select units" },
  { value: "formal", label: "Fully Structured", description: "Documented, governed, and budgeted innovation pipeline" },
];

export default function Step2_InnovationState({ data, onChange }: Props) {
  return (
    <div className="space-y-7">
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/40 text-amber-300 text-xs font-bold uppercase tracking-wider mb-2 border border-amber-800/40">
          <Compass className="w-3.5 h-3.5" />
          <span>Section 2 of 5</span>
        </div>
        <h2 className="text-2xl font-bold text-white">Current Innovation State</h2>
        <p className="text-sm text-stone-400 mt-1">
          Evaluate your organization's current innovation maturity and feedback mechanisms.
        </p>
      </div>

      {/* Innovation process */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Innovation Governance & Process <span className="text-amber-400">*</span>
        </label>
        <div className="grid sm:grid-cols-2 gap-3">
          {PROCESS_OPTIONS.map(({ value, label, description }) => {
            const isSelected = data.innovationProcess === value;
            return (
              <button
                key={value}
                type="button"
                onClick={() => onChange("innovationProcess", value)}
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
                  <Lightbulb className={`w-4 h-4 ${isSelected ? "text-amber-400" : "text-stone-500"}`} />
                </div>
                <div className="text-xs text-stone-400 leading-relaxed">{description}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Past initiatives */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Recent Innovation Experiments & Past Initiatives
        </label>
        <p className="text-xs text-stone-400">
          Mention recent launches, prototypes, or failed experiments. This reveals your risk appetite.
        </p>
        <textarea
          value={data.pastInitiatives}
          onChange={(e) => onChange("pastInitiatives", e.target.value)}
          rows={3}
          placeholder="e.g. We piloted an automated internal workflow tool last quarter with moderate adoption..."
          className="w-full border border-stone-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none shadow-sm"
        />
      </div>

      {/* Customer/Market Feedback */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-stone-200">
          Customer & Market Feedback Channels <span className="text-amber-400">*</span>
        </label>
        <div className="relative">
          <select
            value={data.customerFeedback}
            onChange={(e) => onChange("customerFeedback", e.target.value)}
            className="w-full border border-stone-800 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-stone-900/60 shadow-sm appearance-none cursor-pointer"
          >
            <option value="">Select feedback mechanism...</option>
            <option value="no_formal_process">No formal process (Reactive only)</option>
            <option value="informal_conversations">Informal sales & support conversations</option>
            <option value="surveys_nps">Structured surveys, NPS & client reviews</option>
            <option value="dedicated_research">Dedicated UX/Market research unit</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-stone-500">
            <MessageSquare className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
}