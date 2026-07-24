interface NextStep {
  action: string;
  owner: string;
  timeframe: string;
}

interface NextStepsListProps {
  steps: NextStep[];
}

export default function NextStepsList({ steps }: NextStepsListProps) {
  if (!steps.length) return null;

  return (
    <div className="bg-teal-50 rounded-2xl border border-teal-100 p-6">
      <h2 className="text-lg font-semibold text-teal-800 mb-4">
          Recommended Next Steps
      </h2>
      <ol className="flex flex-col gap-4">
        {steps.map((step, index) => (
          <li key={index} className="flex gap-3">
            <span className="w-6 h-6 rounded-full bg-teal-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
              {index + 1}
            </span>
            <div className="flex-1">
              <p className="text-sm text-teal-900 leading-relaxed">{step.action}</p>
              <div className="flex gap-3 mt-1.5">
                <span className="text-xs text-teal-600 bg-white px-2 py-0.5 rounded-full border border-teal-200">
                  👤 {step.owner}
                </span>
                <span className="text-xs text-teal-600 bg-white px-2 py-0.5 rounded-full border border-teal-200">
                  ⏱ {step.timeframe}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}