"use client";

import { useEffect, useState } from "react";
import { useMutation } from "@apollo/client/react";
import { useParams, useRouter } from "next/navigation";
import { SELECT_INSIGHT } from "@/lib/graphql/mutations";
import { normalize } from "@/lib/graphql/normalize";
import { useInsight } from "@/lib/hooks/useInsight";
import type { ChatTag, ReportSection, Insight } from "@/lib/types";
import { Button, buttonVariants } from "@/components/ui/button";
import { AlertCircle, MessageCircle } from "lucide-react";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
import { motion } from "framer-motion";
import ReportColumn from "./components/ReportColumn";
import ResultsSkeleton from "./components/ResultsSkeleton";
import ChatPanel from "./components/ChatPanel";

const MODEL_LABELS: Record<string, string> = {
  "gemma4:12B": "gemma4:12B — baseline",
  "caforb-v1": "caforb-v1 — fine-tuned",
};

const modelLabel = (c: Insight) =>
  MODEL_LABELS[c.modelName] ?? c.modelName ?? "Model";

const MODEL_SHORT_LABELS: Record<string, string> = {
  "gemma4:12B": "Base",
  "caforb-v1": "CaForB",
};

const shortLabel = (name: string) => MODEL_SHORT_LABELS[name] ?? name;

const VIEW_STORAGE_KEY = "caforb:results:view-mode";

function getInitialViewMode(): string {
  if (typeof window === "undefined") return "both";
  try {
    return localStorage.getItem(VIEW_STORAGE_KEY) ?? "both";
  } catch {
    return "both";
  }
}

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string, 10);

  const [chatOpen, setChatOpen] = useState(false);
  const [chatExpanded, setChatExpanded] = useState(false);
  const [pendingTag, setPendingTag] = useState<ChatTag | null>(null);
  const [viewMode, setViewMode] = useState<string>(getInitialViewMode);

  useEffect(() => {
    try {
      localStorage.setItem(VIEW_STORAGE_KEY, viewMode);
    } catch {
      /* ignore */
    }
  }, [viewMode]);

  const { insight: rawInsight, loading, error, refetch } = useInsight(id, "no-cache");
  const [selectInsight] = useMutation(SELECT_INSIGHT);

  const insight = normalize(rawInsight);
  const variants: Insight[] = (rawInsight?.variants ?? [])
    .map(normalize)
    .filter((v): v is Insight => v !== null);
  const columns = insight ? [insight, ...variants] : [];

  const modelNames = Array.from(new Set(columns.map((c) => c.modelName)));
  const effectiveViewMode = modelNames.includes(viewMode) ? viewMode : "both";
  const visibleColumns = columns.filter(
    (c) => effectiveViewMode === "both" || c.modelName === effectiveViewMode
  );

  const sections: ReportSection[] = insight
    ? [
        ...(insight.opportunities ?? []).map((o) => ({
          kind: "opportunity" as const,
          id: o.id,
          label: o.title,
        })),
        ...(insight.nextSteps ?? []).map((s) => ({
          kind: "nextStep" as const,
          id: s.id,
          label: s.action,
        })),
        ...(insight.keyWeaknesses ?? []).map((w: string, i: number) => ({
          kind: "weakness" as const,
          id: String(i),
          label: w,
        })),
      ]
    : [];

  const handlePrint = () => {
    window.print();
  };

  const handleSetPrimary = (col: Insight) => async () => {
    try {
      await selectInsight({ variables: { insightId: col.id } });
      await refetch();
    } catch {
      /* ignore */
    }
  };

  const handleAskOpportunity = (opp: { id: string; title: string }) => {
    setPendingTag({ kind: "opportunity", id: opp.id, label: opp.title });
    setChatOpen(true);
  };

  const handleAskNextStep = (step: { id: string; action: string }) => {
    setPendingTag({ kind: "nextStep", id: step.id, label: step.action });
    setChatOpen(true);
  };

  const handleAskWeakness = (weakness: { index: number; text: string }) => {
    setPendingTag({ kind: "weakness", id: String(weakness.index), label: weakness.text });
    setChatOpen(true);
  };

  return (
    <div className={`min-h-screen bg-stone-950 flex flex-col selection:bg-amber-500 selection:text-white transition-[padding] duration-300 ${chatExpanded ? "lg:pr-[calc(33.333%+1.5rem)]" : ""}`}>
      <PageBackground variant="results" />

      <div className="print:hidden">
        <NavHeader />
      </div>

      <main className="flex-1 py-10 px-4 relative z-10">
        <div className="w-full max-w-7xl mx-auto space-y-6">
          {/* Header Banner */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-amber-950/40 text-amber-300 text-xs font-bold uppercase tracking-wider border border-amber-800/40">
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
              <div className="flex flex-col items-center justify-center p-8 rounded-xl border border-stone-800/80 bg-stone-900/60 shadow-sm">
                <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mb-3" />
                <p className="text-sm font-semibold text-stone-300">Synthesizing corporate recommendations...</p>
              </div>
              <ResultsSkeleton />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-8 text-center space-y-3">
              <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
              <h3 className="text-lg font-bold text-rose-200">Unable to load report</h3>
              <p className="text-xs text-rose-300 max-w-sm mx-auto">{error.message}</p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
                <Button size="sm" onClick={() => refetch()}>
                  Try Again
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => router.push("/assessment")}
                >
                  Restart Assessment
                </Button>
              </div>
            </div>
          )}

          {/* Report Data */}
          {insight && (
            <motion.div
              className="space-y-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              {/* Report visibility toggle */}
              {columns.length > 1 && (
                <div
                  className="flex flex-wrap items-center gap-2 print:hidden"
                  role="group"
                  aria-label="Report visibility"
                >
                  <span className="text-xs text-stone-500 mr-1">View:</span>
                  <button
                    type="button"
                    onClick={() => setViewMode("both")}
                    aria-pressed={effectiveViewMode === "both"}
                    className={buttonVariants({
                      variant: effectiveViewMode === "both" ? "secondary" : "ghost",
                      size: "sm",
                    })}
                  >
                    Both
                  </button>
                  {modelNames.map((name) => (
                    <button
                      key={name}
                      type="button"
                      onClick={() => setViewMode(name)}
                      aria-pressed={effectiveViewMode === name}
                      className={buttonVariants({
                        variant: effectiveViewMode === name ? "secondary" : "ghost",
                        size: "sm",
                      })}
                    >
                      {shortLabel(name)}
                    </button>
                  ))}
                </div>
              )}

              {/* Model comparison strip */}
              {visibleColumns.length > 1 && (
                <div className="flex items-center gap-2 text-xs font-semibold text-stone-400 uppercase tracking-wider">
                  <span>Model comparison</span>
                </div>
              )}

              {visibleColumns.length > 1 && (
                <div className="grid grid-cols-2 gap-3">
                  {visibleColumns.map((col) => (
                    <div
                      key={col.id}
                      className={`rounded-xl border p-4 text-center ${
                        col.isSelected
                          ? "border-amber-500/60 bg-amber-950/30"
                          : "border-stone-800 bg-stone-900/40"
                      }`}
                    >
                      <div className="text-xs uppercase tracking-wider text-stone-500 font-semibold truncate">
                        {modelLabel(col)}
                      </div>
                      <div className="mt-1 text-3xl font-extrabold text-white">
                        {col.innovationScore != null ? col.innovationScore.toFixed(1) : "—"}
                      </div>
                      {col.scoreDelta != null && col.scoreDelta !== 0 && (
                        <div className={`mt-1 text-xs font-bold ${col.scoreDelta > 0 ? "text-emerald-400" : "text-rose-400"}`}>
                          {col.scoreDelta > 0 ? "+" : ""}{col.scoreDelta.toFixed(1)}
                        </div>
                      )}
                      {col.isSelected && (
                        <div className="mt-1 text-xs font-bold uppercase tracking-wider text-amber-400">
                          Primary
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Report columns */}
              <div
                className={
                  visibleColumns.length > 1
                    ? "grid grid-cols-1 lg:grid-cols-2 gap-6 items-start"
                    : "grid grid-cols-1 gap-6 max-w-3xl mx-auto"
                }
              >
                {visibleColumns.map((col) => (
                  <ReportColumn
                    key={col.id}
                    insight={col}
                    modelLabel={modelLabel(col)}
                    isPrimary={col.isSelected}
                    onSetPrimary={col.isSelected ? null : handleSetPrimary(col)}
                    onAskOpportunity={handleAskOpportunity}
                    onAskNextStep={handleAskNextStep}
                    onAskWeakness={handleAskWeakness}
                  />
                ))}
              </div>

              {/* Bottom Actions */}
              <div className="pt-6 border-t border-stone-800/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-center print:hidden">
                <Button
                  onClick={() => router.push("/assessment")}
                  className="w-full sm:w-auto"
                >
                  Run Another Assessment
                </Button>

                <Button
                  variant="secondary"
                  onClick={handlePrint}
                  className="w-full sm:w-auto"
                >
                  Print or Save PDF Report
                </Button>
              </div>
            </motion.div>
          )}
        </div>
      </main>

      {/* Ask AI chat */}
      {insight && !chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-400 text-stone-950 text-sm font-bold shadow-lg hover:bg-amber-300 transition print:hidden"
        >
          <MessageCircle className="w-4 h-4" />
          <span>Ask AI</span>
        </button>
      )}

      <ChatPanel
        insightId={id}
        open={chatOpen}
        onClose={() => {
          setChatOpen(false);
          setChatExpanded(false);
        }}
        expanded={chatExpanded}
        onToggleExpanded={() => setChatExpanded((v) => !v)}
        pendingTag={pendingTag}
        onSetTag={setPendingTag}
        onConsumeTag={() => setPendingTag(null)}
        sections={sections}
      />
    </div>
  );
}
