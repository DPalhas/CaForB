"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery, useMutation } from "@apollo/client/react";
import { SUBMIT_QUESTIONNAIRE, SUBMIT_REASSESSMENT } from "@/lib/graphql/mutations";
import { GET_INSIGHT, MY_COMPANIES } from "@/lib/graphql/queries";
import { friendlyAssessmentError } from "@/lib/graphql/errors";
import { AssessmentFormData, EMPTY_FORM } from "@/lib/types";
import { ArrowLeft, ArrowRight, Sparkles, CheckCircle, AlertCircle, Loader2, Building2, Plus, RefreshCw } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion"
import { easeOut } from "@/lib/easing";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
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
  "Resolving assessment context & company profile...",
  "Building strategic prompt with constraints...",
  "Phase 1 — Evaluating maturity score & opportunities...",
  "Phase 2 — Generating next steps, weaknesses & progress report...",
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
    <div className="flex flex-col gap-3.5 w-full max-w-md bg-stone-900/60 p-6 rounded-2xl border border-stone-800/80 backdrop-blur-md">
      {ANALYSIS_STEPS.map((step, i) => (
        <div
          key={i}
          className={`flex items-center gap-3 text-sm transition-all duration-500 ${
            i < current
              ? "text-amber-400 font-medium"
              : i === current
              ? "text-white font-semibold"
              : "text-stone-500"
          }`}
        >
          <span className="w-6 h-6 flex-shrink-0 flex items-center justify-center rounded-full border border-stone-800 bg-stone-950">
            {i < current ? (
              <CheckCircle className="w-4 h-4 text-amber-400" />
            ) : i === current ? (
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
            ) : (
              <span className="w-1.5 h-1.5 rounded-full bg-stone-700" />
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
    <div className="fixed inset-0 bg-stone-950/90 backdrop-blur-xl z-50 flex flex-col items-center justify-center gap-8 px-6">
      <div className="relative flex items-center justify-center">
        <div className="w-24 h-24 rounded-full border-2 border-amber-500/20 border-t-amber-400 animate-spin" />
        <div className="absolute inset-0 w-24 h-24 rounded-full border-2 border-emerald-500/20 border-b-emerald-400 animate-spin [animation-duration:3s]" />
        <div className="w-14 h-14 rounded-2xl bg-amber-400 flex items-center justify-center shadow-xl shadow-amber-500/30">
          <Sparkles className="w-7 h-7 text-stone-950 animate-pulse" />
        </div>
      </div>
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-white mb-2">
          Evaluating Corporate Intelligence
        </h2>
        <p className="text-sm text-stone-400 leading-relaxed">
          Our specialized LLM is analyzing your company&apos;s inputs against corporate innovation frameworks.
        </p>
      </div>
      <AnalysisSteps />
    </div>
  );
}

// --- Company picker (pre-step for re-use) ---

function CompanyPicker({
  onSelectNew,
  onSelectExisting,
}: {
  onSelectNew: () => void;
  onSelectExisting: (companyId: number, lastInsightId: number) => void;
}) {
  const { data, loading } = useQuery(MY_COMPANIES);
  const companies = (data as any)?.myCompanies ?? [];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-amber-400" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-stone-400">
        Choose an existing company to run a re-assessment, or create a new profile.
      </p>

      {companies.length > 0 && (
        <div className="flex flex-col gap-2">
          {companies.map((c: any) => (
            <button
              key={c.id}
              onClick={() => {
                onSelectExisting(c.id, c.latestInsightId);
              }}
              className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition group"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-stone-950 border border-stone-800 flex items-center justify-center flex-shrink-0">
                  <Building2 className="w-5 h-5 text-amber-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-white group-hover:text-amber-300 transition">
                    {c.name}
                  </div>
                  <div className="text-xs text-stone-500">
                    {c.sector} &middot; {c.size} &middot; {c.assessmentCount} assessment{c.assessmentCount !== 1 ? "s" : ""}
                    {c.latestScore !== null && (
                      <span className="ml-1">
                        &middot; Latest score: <span className="text-amber-400">{c.latestScore.toFixed(1)}</span>
                      </span>
                    )}
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-stone-600 group-hover:text-amber-400 transition" />
              </div>
            </button>
          ))}
        </div>
      )}

      <button
        onClick={onSelectNew}
        className="flex items-center gap-2 justify-center w-full p-4 rounded-xl bg-amber-400/10 border border-amber-500/30 hover:bg-amber-400/20 transition"
      >
        <Plus className="w-4 h-4 text-amber-400" />
        <span className="text-sm font-semibold text-amber-400">Create New Company</span>
      </button>
    </div>
  );
}

// --- Progress tracker for previous recommendations (Step 0 in re-assessment) ---

function ReassessmentProgress({
  previousInsightId,
  onProgress,
}: {
  previousInsightId: number;
  onProgress: (status: Record<string, string>, changes: string) => void;
}) {
  const { data, loading } = useQuery(GET_INSIGHT, {
    variables: { id: previousInsightId },
    fetchPolicy: "network-only",
  });
  const insight = (data as any)?.getInsight;
  const [statuses, setStatuses] = useState<Record<string, string>>({});
  const [changes, setChanges] = useState("");

  useEffect(() => {
    if (insight) {
      const init: Record<string, string> = {};
      (insight.opportunities ?? []).forEach((o: any, i: number) => {
        const key = o.id || `opp_${i}`;
        init[key] = "not_done";
      });
      (insight.nextSteps ?? []).forEach((s: any, i: number) => {
        const key = s.id || `step_${i}`;
        init[key] = "not_done";
      });
      setStatuses(init);
    }
  }, [insight]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-5 h-5 animate-spin text-amber-400" />
      </div>
    );
  }

  if (!insight) return null;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h3 className="text-lg font-bold text-white mb-1">Since Your Last Assessment</h3>
        <p className="text-xs text-stone-500">
          Assessment #{insight.assessmentNumber} &middot; Score: {insight.innovationScore?.toFixed(1) ?? "—"}
        </p>
      </div>

      {/* Previous opportunities — mark progress */}
      {(insight.opportunities ?? []).length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-stone-300 mb-2">Progress on Opportunities</h4>
          <div className="flex flex-col gap-2">
            {insight.opportunities.map((o: any, i: number) => {
              const key = o.id || `opp_${i}`;
              return (
              <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-stone-900/40 border border-stone-800/60">
                <span className="text-xs text-amber-400 flex-shrink-0">[{o.type}]</span>
                <span className="text-sm flex-1 text-stone-300">{o.title}</span>
                <select
                  value={statuses[key] ?? "not_done"}
                  onChange={(e) => {
                    const next = { ...statuses, [key]: e.target.value };
                    setStatuses(next);
                    onProgress(next, changes);
                  }}
                  className="text-xs bg-stone-950 border border-stone-700 rounded-lg px-2 py-1 text-stone-300"
                >
                  <option value="completed">Done</option>
                  <option value="in_progress">In Progress</option>
                  <option value="not_done">Not Started</option>
                  <option value="superseded">Superseded</option>
                </select>
              </div>
            );})}
          </div>
        </div>
      )}

      {/* Previous next steps — mark progress */}
      {(insight.nextSteps ?? []).length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-stone-300 mb-2">Progress on Next Steps</h4>
          <div className="flex flex-col gap-2">
            {insight.nextSteps.map((s: any, i: number) => {
              const key = s.id || `step_${i}`;
              return (
              <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-stone-900/40 border border-stone-800/60">
                <span className="text-xs flex-1 text-stone-400">{s.action}</span>
                <select
                  value={statuses[key] ?? "not_done"}
                  onChange={(e) => {
                    const next = { ...statuses, [key]: e.target.value };
                    setStatuses(next);
                    onProgress(next, changes);
                  }}
                  className="text-xs bg-stone-950 border border-stone-700 rounded-lg px-2 py-1 text-stone-300"
                >
                  <option value="completed">Done</option>
                  <option value="in_progress">In Progress</option>
                  <option value="not_done">Not Started</option>
                </select>
              </div>
            );})}
          </div>
        </div>
      )}

      {/* Free-text changes */}
      <div>
        <label className="text-sm font-semibold text-stone-300 mb-2 block">
          What changed since your last assessment?
        </label>
        <textarea
          value={changes}
          onChange={(e) => {
            setChanges(e.target.value);
            onProgress(statuses, e.target.value);
          }}
          placeholder="e.g. Hired 3 engineers, launched mobile app, competitor X entered the market..."
          className="w-full bg-stone-950 border border-stone-700 rounded-xl p-3 text-sm text-stone-200 placeholder-stone-600 focus:outline-none focus:border-amber-500/50 transition resize-none"
          rows={3}
        />
      </div>
    </div>
  );
}

// --- Main page ---

function AssessmentPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlCompanyId = searchParams.get("companyId");
  const [mode, setMode] = useState<"choose" | "new" | "reassess">(
    urlCompanyId ? "reassess" : "choose"
  );
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(
    urlCompanyId ? parseInt(urlCompanyId, 10) : null
  );
  const [previousInsightId, setPreviousInsightId] = useState<number | null>(null);
  const [progressData, setProgressData] = useState<{
    status: Record<string, string>; changes: string;
  }>({ status: {}, changes: "" });

  const [step, setStep] = useState(0);
  const [form, setForm] = useState<AssessmentFormData>(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);
  const [isAnalysing, setIsAnalysing] = useState(false);

  const [submitQuestionnaire, { loading }] = useMutation(SUBMIT_QUESTIONNAIRE);
  const [submitReassessment] = useMutation(SUBMIT_REASSESSMENT);

  const { data: prevData } = useQuery(GET_INSIGHT, {
    variables: { id: previousInsightId! },
    skip: !previousInsightId,
    fetchPolicy: "network-only",
  });

  const { data: companiesData } = useQuery(MY_COMPANIES, {
    skip: mode !== "reassess" || !!previousInsightId,
  });

  useEffect(() => {
    if (mode === "reassess" && selectedCompanyId && !previousInsightId) {
      const companies = (companiesData as any)?.myCompanies ?? [];
      const c = companies.find((x: any) => x.id === selectedCompanyId);
      if (c?.latestInsightId) {
        setPreviousInsightId(c.latestInsightId);
      }
    }
  }, [companiesData, mode, selectedCompanyId, previousInsightId]);

  useEffect(() => {
    const prev = (prevData as any)?.getInsight;
    if (!prev || mode !== "reassess") return;
    let prevAnswers: Record<string, any> = {};
    try {
      prevAnswers = JSON.parse(prev.previousAnswers || "{}");
    } catch {}
    setForm({
      companyName: prev.companyName || "",
      sector: prev.sector || "",
      size: prev.size || "",
      regulatoryEnvironment: prevAnswers.regulatoryEnvironment || "",
      innovationProcess: prevAnswers.innovation_process || "",
      pastInitiatives: prevAnswers.past_initiatives || "",
      strategicGoals: prevAnswers.strategic_goals || "",
      timeHorizon: prevAnswers.time_horizon || "",
      riskAppetite: prevAnswers.riskAppetite || "",
      strategicPriority: prevAnswers.strategicPriority || "",
      teamSize: prevAnswers.team_size || "",
      digitalMaturity: prevAnswers.digital_maturity || "",
      budgetPercentage: prevAnswers.budgetPercentage ?? 5,
      revenueRange: prevAnswers.revenueRange || "",
      decisionMaking: prevAnswers.decision_making || "",
      mainBarrier: prevAnswers.main_barrier || [],
      competitivePressure: prevAnswers.competitivePressure || "",
      additionalContext: prevAnswers.additional_context || "",
      companyDescription: prevAnswers.company_description || "",
      customerFeedback: prevAnswers.customer_feedback || "",
    });
  }, [prevData, mode]);

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

  const buildAnswers = () => ({
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
  });

  const handleSubmit = async () => {
    if (!isStepValid()) {
      setError("Please fill in all required fields before submitting.");
      return;
    }
    setIsAnalysing(true);
    const answers = buildAnswers();

    try {
      let resultId: number | null = null;

      if (mode === "reassess" && selectedCompanyId && previousInsightId) {
        const { data } = await submitReassessment({
          variables: {
            companyId: selectedCompanyId,
            companyName: form.companyName,
            sector: form.sector,
            size: form.size,
            answers,
            previousInsightId,
            recommendationStatus: progressData.status,
            changesSinceLast: progressData.changes || "",
          },
        });
        resultId = (data as any)?.submitReassessment?.id;
      } else {
        const { data } = await submitQuestionnaire({
          variables: {
            companyName: form.companyName,
            sector: form.sector,
            size: form.size,
            answers,
            companyId: mode === "new" ? null : selectedCompanyId || null,
          },
        });
        resultId = (data as any)?.submitQuestionnaire?.id;
      }

      if (resultId) {
        router.push(`/results/${resultId}`);
      }
    } catch (err: any) {
      setIsAnalysing(false);
      const { message } = friendlyAssessmentError(err);
      setError(message);
      console.error(err);
    }
  };

  // --- Render the company-chooser if no mode selected ---
  if (mode === "choose") {
    return (
      <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
        <NavHeader />
        <main className="flex-1 flex items-start justify-center py-10 px-4">
          <div className="w-full max-w-2xl">
            <div className="glass-card rounded-3xl border border-stone-800/80 p-6 sm:p-10 shadow-2xl">
              <h2 className="text-xl font-bold text-white mb-6">Start an Assessment</h2>
              <CompanyPicker
                onSelectNew={() => setMode("new")}
                onSelectExisting={(companyId, lastInsightId) => {
                  setSelectedCompanyId(companyId);
                  setPreviousInsightId(lastInsightId);
                  setMode("reassess");
                }}
              />
            </div>
          </div>
        </main>
      </div>
    );
  }

  // --- Main questionnaire flow ---

  const steps = [
    <Step1_CompanyProfile key="1" data={form} onChange={handleChange} />,
    <Step2_InnovationState key="2" data={form} onChange={handleChange} />,
    <Step3_StrategicGoals key="3" data={form} onChange={handleChange} />,
    <Step4_Capabilities key="4" data={form} onChange={handleChange} />,
    <Step5_PainPoints key="5" data={form} onChange={handleChange} />,
  ];

  const isReassess = mode === "reassess";

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      {isAnalysing && <AnalysingOverlay />}
      <PageBackground variant="assessment" />
      <NavHeader />

      <main className="flex-1 flex items-start justify-center py-10 px-4">
        <div className="w-full max-w-2xl">
          <div className="glass-card rounded-3xl border border-stone-800/80 p-6 sm:p-10 shadow-2xl">

            {isReassess && previousInsightId && (
              <div className={step === 0 ? "mb-8 p-5 rounded-2xl bg-amber-950/20 border border-amber-800/40" : "hidden"}>
                <ReassessmentProgress
                  previousInsightId={previousInsightId}
                  onProgress={(status, changes) =>
                    setProgressData({ status, changes })
                  }
                />
                <button
                  onClick={() => setStep(1)}
                  className="mt-6 w-full px-6 py-3 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:opacity-90 transition shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2 group"
                >
                  <span>Continue to Questionnaire</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
            )}

            {/* Only show the 5 steps after "Continue" is clicked in re-assessment,
                or immediately for new company */}
            {(!isReassess || step > 0) && (
              <>
                <StepIndicator
                  currentStep={step}
                  totalSteps={steps.length}
                  labels={STEP_LABELS}
                />

                <AnimatePresence mode="wait">
                  <motion.div
                    key={step}
                    className="min-h-[340px]"
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -30 }}
                    transition={{ duration: 0.25, ease: easeOut }}
                  >
                    {steps[step]}
                  </motion.div>
                </AnimatePresence>

                {error && (
                  <div className="mt-6 rounded-2xl border border-rose-800/60 bg-rose-950/40 p-6 text-center space-y-4">
                    <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
                    <div>
                      <h3 className="text-lg font-bold text-rose-200">
                        We couldn&apos;t generate your analysis
                      </h3>
                      <p className="text-sm text-rose-300 max-w-sm mx-auto mt-2">
                        {error}
                      </p>
                    </div>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                      <button
                        onClick={handleSubmit}
                        disabled={loading || isAnalysing}
                        className="px-6 py-2.5 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:opacity-90 transition disabled:opacity-60 flex items-center gap-2"
                      >
                        {loading || isAnalysing ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Retrying...</span>
                          </>
                        ) : (
                          <>
                            <RefreshCw className="w-4 h-4" />
                            <span>Try Again</span>
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => setError(null)}
                        className="px-6 py-2.5 text-sm font-semibold text-stone-300 bg-stone-900/80 border border-stone-800 rounded-xl hover:bg-stone-800 transition"
                      >
                        Back to Form
                      </button>
                    </div>
                  </div>
                )}

                <div className="flex justify-between items-center mt-10 pt-6 border-t border-stone-800">
                  <button
                    onClick={handleBack}
                    disabled={step === 0}
                    className="px-5 py-3 text-sm font-semibold text-stone-300 bg-stone-900/80 border border-stone-800 rounded-xl hover:bg-stone-800 disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center gap-2"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Back</span>
                  </button>

                  {step < steps.length - 1 ? (
                    <button
                      onClick={handleNext}
                      className="px-7 py-3 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:opacity-90 transition shadow-lg shadow-amber-500/20 flex items-center gap-2 group"
                    >
                      <span>Continue</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={loading || isAnalysing}
                      className="px-7 py-3 text-sm font-bold text-stone-950 bg-amber-400 rounded-xl hover:opacity-95 disabled:opacity-60 disabled:cursor-not-allowed transition shadow-xl shadow-amber-500/25 flex items-center gap-2"
                    >
                      {loading || isAnalysing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin text-stone-950" />
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
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function AssessmentPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-stone-950" />}>
      <AssessmentPageInner />
    </Suspense>
  );
}
