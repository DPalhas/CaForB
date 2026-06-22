interface NextStepsListProps {
  steps: string[];
}

export default function NextStepsList({ steps }: NextStepsListProps) {
  if (!steps.length) return null;

  return (
    <div className="bg-teal-50 rounded-2xl border border-teal-100 p-6">
      <h2 className="text-lg font-semibold text-teal-800 mb-4">
        ✅ Recommended Next Steps
      </h2>
      <ol className="flex flex-col gap-3">
        {steps.map((step, index) => (
          <li key={index} className="flex gap-3">
            <span className="w-6 h-6 rounded-full bg-teal-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
              {index + 1}
            </span>
            <p className="text-sm text-teal-900 leading-relaxed">{step}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}