import { Building2, Compass, Target, Cpu, AlertTriangle, Check } from "lucide-react";

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
  labels: string[];
}

const STEP_ICONS = [Building2, Compass, Target, Cpu, AlertTriangle];

export default function StepIndicator({
  currentStep,
  totalSteps,
  labels,
}: StepIndicatorProps) {
  const progressPercent = ((currentStep + 1) / totalSteps) * 100;

  return (
    <div className="w-full mb-10">
      {/* Step Header info */}
      <div className="flex items-center justify-between mb-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
        <span>Step {currentStep + 1} of {totalSteps}</span>
        <span className="text-purple-400 font-mono font-bold">{Math.round(progressPercent)}% Complete</span>
      </div>

      {/* Progress Bar Container */}
      <div className="w-full bg-slate-900/60 rounded-full h-2 mb-6 overflow-hidden p-0.5 border border-slate-800/80 shadow-inner">
        <div
          className="bg-gradient-to-r from-purple-500 via-fuchsia-500 to-indigo-500 h-full rounded-full transition-all duration-500 ease-out shadow-sm"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-5 gap-2">
        {labels.map((label, index) => {
          const Icon = STEP_ICONS[index] || Building2;
          const isCompleted = index < currentStep;
          const isActive = index === currentStep;

          return (
            <div key={index} className="flex flex-col items-center text-center group">
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 mb-2 relative ${
                  isCompleted
                    ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
                    : isActive
                    ? "bg-slate-900 text-purple-400 ring-4 ring-purple-500/20 border border-purple-500 shadow-lg"
                    : "bg-slate-900/40 text-slate-500 border border-slate-800"
                }`}
              >
                {isCompleted ? (
                  <Check className="w-5 h-5 stroke-[2.5]" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}

                {isActive && (
                  <span className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full animate-ping" />
                )}
              </div>

              <span
                className={`text-xs font-medium transition-colors hidden sm:block ${
                  isActive
                    ? "text-purple-400 font-bold"
                    : isCompleted
                    ? "text-slate-300 font-semibold"
                    : "text-slate-500"
                }`}
              >
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}