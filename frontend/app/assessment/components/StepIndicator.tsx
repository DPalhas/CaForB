interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
  labels: string[];
}

export default function StepIndicator({
  currentStep,
  totalSteps,
  labels,
}: StepIndicatorProps) {
  return (
    <div className="w-full mb-8">
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-1.5 mb-4">
        <div
          className="bg-teal-600 h-1.5 rounded-full transition-all duration-500"
          style={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
        />
      </div>

      {/* Step labels */}
      <div className="flex justify-between">
        {labels.map((label, index) => (
          <div key={index} className="flex flex-col items-center gap-1">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-colors
                ${index < currentStep
                  ? "bg-teal-600 text-white"
                  : index === currentStep
                  ? "bg-teal-600 text-white ring-4 ring-teal-100"
                  : "bg-gray-200 text-gray-400"
                }`}
            >
              {index < currentStep ? "✓" : index + 1}
            </div>
            <span
              className={`text-xs hidden sm:block ${
                index === currentStep
                  ? "text-teal-700 font-medium"
                  : "text-gray-400"
              }`}
            >
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}