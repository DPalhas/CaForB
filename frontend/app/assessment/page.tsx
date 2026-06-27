"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@apollo/client/react";
import { SUBMIT_QUESTIONNAIRE } from "@/lib/graphql/mutations";
import { AssessmentFormData, EMPTY_FORM } from "@/lib/types";
import StepIndicator from "./components/StepIndicator";
import Step1_CompanyProfile from "./components/steps/Step1_CompanyProfile";
import Step2_InnovationState from "./components/steps/Step2_InnovationState";
import Step3_StrategicGoals from "./components/steps/Step3_StrategicGoals";
import Step4_Capabilities from "./components/steps/Step4_Capabilities";
import Step5_PainPoints from "./components/steps/Step5_PainPoints";

const STEP_LABELS = [
  "Company", "Innovation", "Strategy", "Capabilities", "Barriers",
];

const STEP_REQUIRED: (keyof AssessmentFormData)[][] = [
  ["companyName", "sector", "size"],
  ["innovationProcess"],
  ["strategicGoals", "timeHorizon"],
  ["teamSize", "digitalMaturity"],
  ["mainBarrier"],
];

// --- Analysis loading overlay ---

const ANALYSIS_STEPS = [
  "Reading company profile...",
  "Assessing innovation maturity...",
  "Identifying opportunities...",
  "Generating strategic roadmap...",
];

function AnalysisSteps() {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrent((prev) => (prev < ANALYSIS_STEPS.length - 1 ? prev + 1 : prev));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-3 w-64">
      {ANALYSIS_STEPS.map((step, i) => (
        <div
          key={i}
          className={`flex items-center gap-3 text-sm transition-all duration-500 ${
            i < current
              ? "text-teal-600"
              : i === current
              ? "text-gray-800 font-medium"
              : "text-gray-300"
          }`}
        >
          <span className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
            {i < current ? (
              <span className="text-teal-500 font-bold">✓</span>
            ) : i === current ? (
              <span className="w-2 h-2 rounded-full bg-teal-600 animate-pulse inline-block" />
            ) : (
              <span className="w-2 h-2 rounded-full bg-gray-200 inline-block" />
            )}
          </span>
          {step}
        </div>
      ))}
    </div>
  );
}

function AnalysingOverlay() {
  return (
    <div className="fixed inset-0 bg-white z-50 flex flex-col items-center justify-center gap-8 px-4">

      {/* Spinning ring */}
      <div className="relative w-20 h-20">
        <div className="absolute inset-0 rounded-full border-4 border-teal-100" />
        <div className="absolute inset-0 rounded-full border-4 border-teal-600 border-t-transparent animate-spin" />
      </div>

      {/* Title */}
      <div className="text-center">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          Analysing your company profile
        </h2>
        <p className="text-sm text-gray-500 max-w-xs leading-relaxed">
          Our AI is reviewing your answers and generating a personalised
          innovation strategy. This usually takes 15–30 seconds.
        </p>
      </div>

      {/* Step tracker */}
      <AnalysisSteps />

    </div>
  );
}

// --- Main page ---

export default function AssessmentPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<AssessmentFormData>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [isAnalysing, setIsAnalysing] = useState(false);

  const [submitQuestionnaire, { loading }] = useMutation(SUBMIT_QUESTIONNAIRE);

  const handleChange = (field: keyof AssessmentFormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const isStepValid = () =>
    STEP_REQUIRED[step].every((field) => form[field] !== "");

  const handleNext = () => {
    if (!isStepValid()) {
      setError("Please fill in all required fields before continuing.");
      return;
    }
    setStep((s) => s + 1);
    setError(null);
  };

  const handleBack = () => {
    setStep((s) => s - 1);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!isStepValid()) {
      setError("Please fill in all required fields before submitting.");
      return;
    }

    const answers = {
      innovation_process: form.innovationProcess,
      past_initiatives: form.pastInitiatives,
      strategic_goals: form.strategicGoals,
      time_horizon: form.timeHorizon,
      team_size: form.teamSize,
      digital_maturity: form.digitalMaturity,
      main_barrier: form.mainBarrier,
      additional_context: form.additionalContext,
    };

    setIsAnalysing(true);

    try {
      const { data } = await submitQuestionnaire({
        variables: {
          companyName: form.companyName,
          sector: form.sector,
          size: form.size,
          answers,
        },
      });
      router.push(`/results/${data.submitQuestionnaire.id}`);
    } catch (err) {
      setIsAnalysing(false);
      setError("Something went wrong. Please try again.");
      console.error(err);
    }
  };

  const steps = [
    <Step1_CompanyProfile key="1" data={form} onChange={handleChange} />,
    <Step2_InnovationState key="2" data={form} onChange={handleChange} />,
    <Step3_StrategicGoals key="3" data={form} onChange={handleChange} />,
    <Step4_Capabilities key="4" data={form} onChange={handleChange} />,
    <Step5_PainPoints key="5" data={form} onChange={handleChange} />,
  ];

  return (
    <>
      {/* Full-screen loading overlay — shown while LLM is running */}
      {isAnalysing && <AnalysingOverlay />}

      <main className="min-h-screen bg-gray-50 flex items-start justify-center py-12 px-4">
        <div className="w-full max-w-2xl">

          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900">Innovation Assessment</h1>
            <p className="text-sm text-gray-500 mt-1">
              Answer 5 short sections to receive your personalised innovation strategy.
            </p>
          </div>

          {/* Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            <StepIndicator
              currentStep={step}
              totalSteps={steps.length}
              labels={STEP_LABELS}
            />

            {/* Step content */}
            <div key={step} className="min-h-[320px] step-fade">
              {steps[step]}
            </div>

            {/* Error */}
            {error && (
              <p className="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-2">
                {error}
              </p>
            )}

            {/* Navigation */}
            <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-100">
              <button
                onClick={handleBack}
                disabled={step === 0}
                className="px-5 py-2.5 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed transition"
              >
                Back
              </button>

              {step < steps.length - 1 ? (
                <button
                  onClick={handleNext}
                  className="px-6 py-2.5 text-sm font-semibold text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition"
                >
                  Continue →
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={loading || isAnalysing}
                  className="px-6 py-2.5 text-sm font-semibold text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:opacity-60 disabled:cursor-not-allowed transition flex items-center gap-2"
                >
                  {loading || isAnalysing ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Analysing...
                    </>
                  ) : (
                    "Generate Analysis →"
                  )}
                </button>
              )}
            </div>
          </div>

          {/* Step counter */}
          <p className="text-center text-xs text-gray-400 mt-4">
            Step {step + 1} of {steps.length}
          </p>

        </div>
      </main>
    </>
  );
}