"use client";

import { useQuery } from "@apollo/client/react";
import { useParams, useRouter } from "next/navigation";
import { GET_INSIGHT } from "@/lib/graphql/queries";
import { RefreshCw, Printer, Sparkles, AlertCircle } from "lucide-react";
import NavHeader from "@/components/NavHeader";
import ScoreCard from "./components/ScoreCard";
import OpportunitiesList from "./components/OpportunitiesList";
import NextStepsList from "./components/NextStepsList";
import WeaknessesList from "./components/WeaknessesList";
import ResultsSkeleton from "./components/ResultsSkeleton";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string, 10);

  const { data, loading, error } = useQuery(GET_INSIGHT, {
    variables: { id },
  });

  const insight = (data as any)?.getInsight;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-stone-950 flex flex-col selection:bg-amber-500 selection:text-white">
      
      {/* Radial gradient overlays (matching landing page) */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-amber-500/15 rounded-full blur-3xl opacity-60" />
        <div className="absolute top-1/3 -right-40 w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl opacity-60" />
        <div className="absolute -bottom-40 left-1/4 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl opacity-50" />
      </div>

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
              <button
                onClick={() => router.push("/assessment")}
                className="mt-2 px-5 py-2.5 text-xs font-semibold bg-rose-600 text-white rounded-xl hover:bg-rose-700 transition"
              >
                Restart Assessment
              </button>
            </div>
          )}

          {/* Report Data */}
          {insight && (
            <div className="space-y-8 step-fade">
              
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

            </div>
          )}

        </div>
      </main>

    </div>
  );
}
