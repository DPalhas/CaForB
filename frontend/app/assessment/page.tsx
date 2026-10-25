"use client";

import { useState, useEffect, useMemo, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation } from "@apollo/client/react";
import { SUBMIT_QUESTIONNAIRE, SUBMIT_REASSESSMENT } from "@/lib/graphql/mutations";
import { friendlyAssessmentError } from "@/lib/graphql/errors";
import { AssessmentFormData, EMPTY_FORM } from "@/lib/types";
import { useCompanies } from "@/lib/hooks/useCompanies";
import { useInsight } from "@/lib/hooks/useInsight";
import { STEP_LABELS, isStepValid, buildAnswers, assessmentFromPrevious } from "@/lib/assessment";
import { ArrowLeft, Sparkles, CheckCircle, AlertCircle, Loader2, Building2 } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion"
import { easeOut } from "@/lib/motion";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading";
import StepIndicator from "./components/StepIndicator";
import CompanyProfileStep from "./components/steps/CompanyProfileStep";
import InnovationStateStep from "./components/steps/InnovationStateStep";
import StrategicGoalsStep from "./components/steps/StrategicGoalsStep";
import CapabilitiesStep from "./components/steps/CapabilitiesStep";
import PainPointsStep from "./components/steps/PainPointsStep";

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
    <div className="flex flex-col gap-4 w-full max-w-md bg-stone-900/60 p-6 rounded-xl border border-stone-800/80">
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
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            ) : (
              <span className="w-1 h-1 rounded-full bg-stone-700" />
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
    <div className="fixed inset-0 bg-stone-950/90 z-50 flex flex-col items-center justify-center gap-8 px-6">
      <div className="relative flex items-center justify-center">
        <div className="w-24 h-24 rounded-full border-2 border-amber-500/20 border-t-amber-400 animate-spin" />
        <div className="absolute inset-0 w-24 h-24 rounded-full border-2 border-emerald-500/20 border-b-emerald-400 animate-spin [animation-duration:3s]" />
        <div className="w-14 h-14 rounded-lg bg-amber-400 flex items-center justify-center">
          <Sparkles className="w-7 h-7 text-stone-950" />
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
  onSelectExisting: (companyId: number) => void;
}) {
  const { companies, loading } = useCompanies();

  if (loading) {
    return <LoadingState />;
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-stone-400">
        Choose an existing company to run a re-assessment, or create a new profile.
      </p>

      {companies.length > 0 && (
        <div className="flex flex-col gap-2">
          {companies.map((c) => (
            <button
              key={c.id}
              onClick={() => {
                onSelectExisting(c.id);
              }}
              className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 group"
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
              </div>
            </button>
          ))}
        </div>
      )}

      <button
        onClick={onSelectNew}
        className="flex items-center gap-2 justify-center w-full p-4 rounded-xl bg-amber-400/10 border border-amber-500/30 hover:bg-amber-400/20 transition"
      >
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
  const { insight, loading } = useInsight(previousInsightId, "network-only");
  const [statusOverrides, setStatusOverrides] = useState<Record<string, string>>({});
  const [changes, setChanges] = useState("");

  const initialStatuses = useMemo(() => {
    if (!insight) return {};
    const init: Record<string, string> = {};
    (insight.opportunities ?? []).forEach((o, i) => {
      init[o.id || `opp_${i}`] = "not_done";
    });
    (insight.nextSteps ?? []).forEach((s, i) => {
      init[s.id || `step_${i}`] = "not_done";
    });
    return init;
  }, [insight]);

  const statuses = { ...initialStatuses, ...statusOverrides };

  if (loading) {
    return <LoadingState className="py-8" />;
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
            {insight.opportunities.map((o, i) => {
              const key = o.id || `opp_${i}`;
              return (
              <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-stone-900/40 border border-stone-800/60">
                <span className="text-xs text-amber-400 flex-shrink-0">[{o.type}]</span>
                <span className="text-sm flex-1 text-stone-300">{o.title}</span>
                <select
                  value={statuses[key] ?? "not_done"}
                  onChange={(e) => {
                    const value = e.target.value;
                    setStatusOverrides((prev) => ({ ...prev, [key]: value }));
                    onProgress({ ...statuses, [key]: value }, changes);
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
            {insight.nextSteps.map((s, i) => {
              const key = s.id || `step_${i}`;
              return (
              <div key={key} className="flex items-center gap-3 p-3 rounded-lg bg-stone-900/40 border border-stone-800/60">
                <span className="text-xs flex-1 text-stone-400">{s.action}</span>
                <select
                  value={statuses[key] ?? "not_done"}
                  onChange={(e) => {
                    const value = e.target.value;
                    setStatusOverrides((prev) => ({ ...prev, [key]: value }));
                    onProgress({ ...statuses, [key]: value }, changes);
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
  const [progressData, setProgressData] = useState<{
    status: Record<string, string>; changes: string;
  }>({ status: {}, changes: "" });

  const [step, setStep] = useState(0);
  const [form, setForm] = useState<AssessmentFormData>(EMPTY_FORM);
  const [formInsightId, setFormInsightId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [isAnalysing, setIsAnalysing] = useState(false);

  const [submitQuestionnaire, { loading }] = useMutation<{
    submitQuestionnaire: { id: number };
  }>(SUBMIT_QUESTIONNAIRE);
  const [submitReassessment] = useMutation<{
    submitReassessment: { id: number };
  }>(SUBMIT_REASSESSMENT);

  const { companies } = useCompanies(mode !== "reassess");

  const previousInsightId = useMemo(() => {
    if (mode !== "reassess" || !selectedCompanyId) return null;
    const c = companies.find((x) => x.id === selectedCompanyId);
    return c?.latestInsightId ?? null;
  }, [mode, selectedCompanyId, companies]);

  const { insight: prev } = useInsight(previousInsightId, "network-only");

  if (prev && mode === "reassess" && formInsightId !== prev.id) {
    setFormInsightId(prev.id);
    setForm(assessmentFromPrevious(prev));
  }

  const handleChange = (
    field: keyof AssessmentFormData,
    value: string | number | string[]
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }) as AssessmentFormData);
    setError(null);
    setNotice(null);
  };

  const handleNext = () => {
    if (!isStepValid(form, step)) {
      setNotice("Please fill in all required fields before continuing.");
      return;
    }
    setStep((s) => s + 1);
    setError(null);
    setNotice(null);
  };

  const handleBack = () => {
    setStep((s) => s - 1);
    setError(null);
    setNotice(null);
  };

  const handleSubmit = async () => {
    if (!isStepValid(form, step)) {
      setNotice("Please fill in all required fields before submitting.");
      return;
    }
    setIsAnalysing(true);
    const answers = buildAnswers(form);

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
        resultId = data?.submitReassessment?.id ?? null;
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
        resultId = data?.submitQuestionnaire?.id ?? null;
      }

      if (resultId) {
        router.push(`/results/${resultId}`);
      }
    } catch (err) {
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
            <div className="rounded-xl border border-stone-800/80 bg-stone-900/60 p-6 shadow-sm">
              <h2 className="text-xl font-bold text-white mb-6">Start an Assessment</h2>
              <CompanyPicker
                onSelectNew={() => setMode("new")}
                onSelectExisting={(companyId) => {
                  setSelectedCompanyId(companyId);
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
    <CompanyProfileStep key="1" data={form} onChange={handleChange} />,
    <InnovationStateStep key="2" data={form} onChange={handleChange} />,
    <StrategicGoalsStep key="3" data={form} onChange={handleChange} />,
    <CapabilitiesStep key="4" data={form} onChange={handleChange} />,
    <PainPointsStep key="5" data={form} onChange={handleChange} />,
  ];

  const isReassess = mode === "reassess";

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      {isAnalysing && <AnalysingOverlay />}
      <PageBackground variant="assessment" />
      <NavHeader />

      <main className="flex-1 flex items-start justify-center py-10 px-4">
        <div className="w-full max-w-2xl">
          <div className="rounded-xl border border-stone-800/80 bg-stone-900/60 p-6 shadow-sm">

            {isReassess && previousInsightId && (
              <div className={step === 0 ? "mb-8 p-4 rounded-xl bg-amber-950/20 border border-amber-800/40" : "hidden"}>
                <ReassessmentProgress
                  previousInsightId={previousInsightId}
                  onProgress={(status, changes) =>
                    setProgressData({ status, changes })
                  }
                />
                <Button
                  onClick={() => setStep(1)}
                  className="mt-6 w-full"
                >
                  Continue to Questionnaire
                </Button>
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

                {notice && (
                  <div className="mt-6 flex items-center gap-3 rounded-xl border border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-200">
                    <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
                    <span>{notice}</span>
                  </div>
                )}

                {error && (
                  <div className="mt-6 rounded-xl border border-rose-800/60 bg-rose-950/40 p-6 text-center space-y-4">
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
                      <Button
                        onClick={handleSubmit}
                        disabled={loading || isAnalysing}
                        size="sm"
                      >
                        {loading || isAnalysing ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Retrying...</span>
                          </>
                        ) : (
                          "Try Again"
                        )}
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setError(null)}
                      >
                        Back to Form
                      </Button>
                    </div>
                  </div>
                )}

                <div className="flex justify-between items-center mt-10 pt-6 border-t border-stone-800">
                  <Button
                    variant="secondary"
                    onClick={handleBack}
                    disabled={step === 0}
                  >
                    <ArrowLeft className="w-4 h-4" />
                    <span>Back</span>
                  </Button>

                  {step < steps.length - 1 ? (
                    <Button onClick={handleNext}>
                      Continue
                    </Button>
                  ) : (
                    <Button
                      onClick={handleSubmit}
                      disabled={loading || isAnalysing}
                    >
                      {loading || isAnalysing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin text-stone-950" />
                          <span>Generating Analysis...</span>
                        </>
                      ) : (
                        "Generate Analysis"
                      )}
                    </Button>
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
