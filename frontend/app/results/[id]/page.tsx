"use client";

import { useQuery } from "@apollo/client/react";
import { useParams, useRouter } from "next/navigation";
import { GET_INSIGHT } from "@/lib/graphql/queries";
import { RefreshCw, Printer, Sparkles, AlertCircle, TrendingUp, TrendingDown, Minus, ChevronRight, ArrowRight } from "lucide-react";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
import { motion } from "framer-motion";
import ScoreCard from "./components/ScoreCard";
import OpportunitiesList from "./components/OpportunitiesList";
import NextStepsList from "./components/NextStepsList";
import WeaknessesList from "./components/WeaknessesList";
import ResultsSkeleton from "./components/ResultsSkeleton";

const dedupeKey = (item: Record<string, any>) =>
  `${item.type ?? ""}|${item.title ?? ""}|${item.rationale ?? ""}|${item.action ?? ""}`;

function dedupe<T extends Record<string, any>>(arr: T[] | undefined | null): T[] {
  if (!arr) return [];
  const seen = new Set<string>();
  return arr.filter((item) => {
    const key = dedupeKey(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string, 10);

  const { data, loading, error, refetch } = useQuery(GET_INSIGHT, {
    variables: { id },
    fetchPolicy: "no-cache",
  });

  const insightRaw = (data as any)?.getInsight;
  const insight = insightRaw ? {
    ...insightRaw,
    opportunities: dedupe(insightRaw.opportunities),
    nextSteps: dedupe(insightRaw.nextSteps),
    keyWeaknesses: [...new Set(insightRaw.keyWeaknesses ?? [])],
  } : null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-stone-950 flex flex-col selection:bg-amber-500 selection:text-white">
      
      <PageBackground variant="results" />

      <div className="print:hidden">
        <NavHeader />
      </div>

      {/* Main Content */}
      <main className="flex-1 py-10 px-4 relative z-10">
        <div className="w-full max-w-3xl mx-auto space-y-8">

          {/* Header Banner */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/40 text-amber-300 text-xs font-bold uppercase tracking-wider border border-amber-800/40">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Executive Advisory Report</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
              Strategic Innovation Roadmap
            </h1>
            <p className="text-sm text-stone-400">
              {loading ? "Generating strategic insights..." : `Analysis Reference #${id}`}
            </p>
            {insight?.companyName && (
              <p className="text-sm font-semibold text-amber-400">
                {insight.companyName} &middot; {insight.sector}
              </p>
            )}
          </div>

          {/* Loading Skeleton */}
          {loading && (
            <div className="space-y-6">
              <div className="flex flex-col items-center justify-center p-8 glass-card rounded-3xl border border-stone-800/80">
                <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mb-3" />
                <p className="text-sm font-semibold text-stone-300">Synthesizing corporate recommendations...</p>
              </div>
              <ResultsSkeleton />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-rose-950/40 border border-rose-800/60 rounded-3xl p-8 text-center space-y-3">
              <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
              <h3 className="text-lg font-bold text-rose-200">Unable to load report</h3>
              <p className="text-xs text-rose-300 max-w-sm mx-auto">{error.message}</p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
                <button
                  onClick={() => refetch()}
                  className="px-5 py-2.5 text-xs font-semibold bg-amber-400 text-stone-950 rounded-xl hover:opacity-90 transition"
                >
                  Try Again
                </button>
                <button
                  onClick={() => router.push("/assessment")}
                  className="px-5 py-2.5 text-xs font-semibold bg-rose-600 text-white rounded-xl hover:bg-rose-700 transition"
                >
                  Restart Assessment
                </button>
              </div>
            </div>
          )}

          {/* Report Data */}
          {insight && (
            <motion.div
              className="space-y-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              
              {/* Score Card */}
              {insight.innovationScore !== null && (
                <ScoreCard score={insight.innovationScore} />
              )}

              {/* Ranked Opportunities */}
              <OpportunitiesList opportunities={insight.opportunities} />

              {/* Actionable Next Steps */}
              <NextStepsList steps={insight.nextSteps} />

              {/* Identified Weaknesses */}
              <WeaknessesList weaknesses={insight.keyWeaknesses} />

              {/* Comparison to Previous Assessment */}
              {insight.comparisonToPrevious && (
                <div className="glass-card rounded-3xl border border-stone-800/80 p-6 space-y-4">
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    {insight.scoreDelta !== null && insight.scoreDelta > 0 ? (
                      <TrendingUp className="w-5 h-5 text-emerald-400" />
                    ) : insight.scoreDelta !== null && insight.scoreDelta < 0 ? (
                      <TrendingDown className="w-5 h-5 text-rose-400" />
                    ) : (
                      <Minus className="w-5 h-5 text-amber-400" />
                    )}
                    vs. Previous Assessment #{insight.comparisonToPrevious.assessmentNumber}
                  </h2>

                  <div className="flex items-center justify-center gap-4 p-4 rounded-xl bg-stone-900/40 border border-stone-800/60">
                    <div className="text-center">
                      <div className="text-xs text-stone-500 mb-1">Previous</div>
                      <div className="text-xl font-bold text-stone-400">
                        {insight.comparisonToPrevious.previousScore?.toFixed(1) ?? "—"}
                      </div>
                      <div className="text-[10px] text-stone-600">
                        {insight.comparisonToPrevious.previousDate}
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-stone-600" />
                    <div className="text-center">
                      <div className="text-xs text-stone-500 mb-1">Current</div>
                      <div className="text-xl font-bold text-white">
                        {insight.innovationScore?.toFixed(1) ?? "—"}
                      </div>
                      {insight.scoreDelta !== null && (
                        <div className={`text-xs font-bold ${
                          insight.scoreDelta > 0 ? "text-emerald-400" : insight.scoreDelta < 0 ? "text-rose-400" : "text-amber-400"
                        }`}>
                          {insight.scoreDelta > 0 ? "+" : ""}{insight.scoreDelta.toFixed(1)}
                        </div>
                      )}
                    </div>
                  </div>

                  {insight.comparisonToPrevious.keyChanges && (
                    <p className="text-sm text-stone-400 leading-relaxed">
                      {insight.comparisonToPrevious.keyChanges}
                    </p>
                  )}
                </div>
              )}

              {/* Progress Report */}
              {insight.progress && (
                <div className="glass-card rounded-3xl border border-stone-800/80 p-6 space-y-4">
                  <h2 className="text-lg font-bold text-white">Progress Report</h2>

                  {(insight.progress.improvements ?? []).length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-emerald-400 mb-2">Improvements</h3>
                      <ul className="space-y-1">
                        {insight.progress.improvements.map((item: string, i: number) => (
                          <li key={i} className="text-sm text-stone-300 flex items-start gap-2">
                            <span className="text-emerald-500 mt-1">+</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(insight.progress.persistentGaps ?? []).length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-amber-400 mb-2">Persistent Gaps</h3>
                      <ul className="space-y-1">
                        {insight.progress.persistentGaps.map((item: string, i: number) => (
                          <li key={i} className="text-sm text-stone-300 flex items-start gap-2">
                            <span className="text-amber-500 mt-1">~</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {(insight.progress.achievedMilestones ?? []).length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-blue-400 mb-2">Achieved Milestones</h3>
                      <ul className="space-y-1">
                        {insight.progress.achievedMilestones.map((item: string, i: number) => (
                          <li key={i} className="text-sm text-stone-300 flex items-start gap-2">
                            <span className="text-blue-500 mt-1">&#10003;</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Bottom Actions */}
              <div className="pt-6 border-t border-stone-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-center print:hidden">
                <button
                  onClick={() => router.push("/assessment")}
                  className="w-full sm:w-auto px-6 py-3 text-sm font-semibold text-stone-950 bg-amber-400 rounded-2xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Run Another Assessment</span>
                </button>

                <button
                  onClick={handlePrint}
                  className="w-full sm:w-auto px-6 py-3 text-sm font-semibold text-stone-300 bg-stone-900/80 border border-stone-800 rounded-2xl hover:bg-stone-800 transition flex items-center justify-center gap-2"
                >
                  <Printer className="w-4 h-4 text-stone-400" />
                  <span>Print or Save PDF Report</span>
                </button>
              </div>

            </motion.div>
          )}

        </div>
      </main>

    </div>
  );
}
