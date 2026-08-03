"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useMutation } from "@apollo/client/react";
import { SUBMIT_QUESTIONNAIRE } from "@/lib/graphql/mutations";
import { AssessmentFormData, EMPTY_FORM } from "@/lib/types";
import { ArrowLeft, ArrowRight, Sparkles, Cpu, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
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
  ["companyName", "sector", "size", "companyDescription"],
  ["innovationProcess", "customerFeedback"],
  ["strategicGoals", "timeHorizon"],
  ["teamSize", "digitalMaturity", "budgetPercentage", "decisionMaking"],
  ["mainBarrier"],
];

// --- Analysis loading overlay ---

const ANALYSIS_STEPS = [
  "Parsing corporate profile & industry sector...",
  "Evaluating digital maturity & internal capabilities...",
  "Identifying strategic innovation opportunities...",
  "Synthesizing actionable executive roadmap...",
];

function AnalysisSteps() {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrent((prev) => (prev < ANALYSIS_STEPS.length - 1 ? prev + 1 : prev));
    }, 4500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col gap-3.5 w-full max-w-md bg-slate-900/60 p-6 rounded-2xl border border-slate-800/80 backdrop-blur-md">
      {ANALYSIS_STEPS.map((step, i) => (
        <div
          key={i}
          className={`flex items-center gap-3 text-sm transition-all duration-500 ${
            i < current
              ? "text-purple-400 font-medium"
              : i === current
              ? "text-white font-semibold"
              : "text-slate-500"
          }`}
        >
          <span className="w-6 h-6 flex-shrink-0 flex items-center justify-center rounded-full border border-slate-855 bg-slate-950">
            {i < current ? (
              <CheckCircle className="w-4 h-4 text-purple-400" />
            ) : i === current ? (
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-pulse" />
            ) : (
              <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
            )}
          </span>
          <span>{step}</span>
        </div>
      ))}
    </div>
  );
}

function AnalysingOverlay() {
  return (
    <div className="fixed inset-0 bg-slate-950/90 backdrop-blur-xl z-50 flex flex-col items-center justify-center gap-8 px-6">
      
      {/* High-tech pulsing AI core indicator */}
      <div className="relative flex items-center justify-center">
        <div className="w-24 h-24 rounded-full border-2 border-purple-500/20 border-t-purple-400 animate-spin" />
        <div className="absolute inset-0 w-24 h-24 rounded-full border-2 border-indigo-500/20 border-b-indigo-400 animate-spin [animation-duration:3s]" />
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-purple-500 to-indigo-400 flex items-center justify-center shadow-xl shadow-purple-500/30">
          <Sparkles className="w-7 h-7 text-slate-950 animate-pulse" />
        </div>
      </div>

      {/* Title */}
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-white mb-2">
          Evaluating Corporate Intelligence
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed">
          Our specialized LLM is analyzing your company's inputs against corporate innovation frameworks.
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

  const handleChange = (field: keyof AssessmentFormData, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const isStepValid = () =>
    STEP_REQUIRED[step].every((field) => {
      const value = form[field];
      if (Array.isArray(value)) return value.length > 0;
      if (typeof value === "number") return true;
      return value !== "" && value !== undefined && value !== null;
    });

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
      company_description: form.companyDescription,
      innovation_process: form.innovationProcess,
      past_initiatives: form.pastInitiatives,
      customer_feedback: form.customerFeedback,
      strategic_goals: form.strategicGoals,
      time_horizon: form.timeHorizon,
      team_size: form.teamSize,
      digital_maturity: form.digitalMaturity,
      budgetPercentage: form.budgetPercentage,
      revenueRange: form.revenueRange,
      decision_making: form.decisionMaking,
      regulatoryEnvironment: form.regulatoryEnvironment,
      riskAppetite: form.riskAppetite,
      strategicPriority: form.strategicPriority,
      competitivePressure: form.competitivePressure,
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
      const resultId = (data as any)?.submitQuestionnaire?.id;
      if (resultId) {
        router.push(`/results/${resultId}`);
      }
    } catch (err) {
      setIsAnalysing(false);
      setError("Something went wrong processing your request. Please try again.");
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-purple-500 selection:text-white">
      
      {/* Full-screen loading overlay */}
      {isAnalysing && <AnalysingOverlay />}

      {/* Sticky Header */}
      <header className="sticky top-0 z-30 w-full bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center text-white">
              <Cpu className="w-4 h-4" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight group-hover:text-purple-400 transition">CaForB</span>
          </Link>

          <span className="text-xs font-semibold text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-full border border-slate-800">
            Corporate Assessment Engine
          </span>
        </div>
      </header>

      {/* Main Form Container */}
      <main className="flex-1 flex items-start justify-center py-10 px-4">
        <div className="w-full max-w-2xl">

          {/* Main Card */}
          <div className="glass-card rounded-3xl border border-slate-800/80 p-6 sm:p-10 shadow-2xl">
            
            <StepIndicator
              currentStep={step}
              totalSteps={steps.length}
              labels={STEP_LABELS}
            />

            {/* Active Step Content */}
            <div key={step} className="min-h-[340px] step-fade">
              {steps[step]}
            </div>

            {/* Error Notification */}
            {error && (
              <div className="mt-6 flex items-center gap-3 text-sm text-rose-300 bg-rose-950/40 border border-rose-800/60 rounded-xl p-4">
                <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {/* Navigation Bar */}
            <div className="flex justify-between items-center mt-10 pt-6 border-t border-slate-800">
              <button
                onClick={handleBack}
                disabled={step === 0}
                className="px-5 py-3 text-sm font-semibold text-slate-300 bg-slate-900/80 border border-slate-800 rounded-xl hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>

              {step < steps.length - 1 ? (
                <button
                  onClick={handleNext}
                  className="px-7 py-3 text-sm font-semibold text-slate-950 bg-gradient-to-r from-purple-400 to-indigo-400 rounded-xl hover:opacity-90 transition shadow-lg shadow-purple-500/20 flex items-center gap-2 group"
                >
                  <span>Continue</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={loading || isAnalysing}
                  className="px-7 py-3 text-sm font-bold text-slate-950 bg-gradient-to-r from-purple-400 via-fuchsia-400 to-indigo-400 rounded-xl hover:opacity-95 disabled:opacity-60 disabled:cursor-not-allowed transition shadow-xl shadow-purple-500/25 flex items-center gap-2"
                >
                  {loading || isAnalysing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      <span>Generating Analysis...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Generate Analysis</span>
                    </>
                  )}
                </button>
              )}
            </div>

          </div>

        </div>
      </main>

    </div>
  );
}