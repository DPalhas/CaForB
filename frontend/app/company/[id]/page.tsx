"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useCompany } from "@/lib/hooks/useCompany";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
import { scoreTier } from "@/lib/score";
import { formatDate } from "@/lib/format";
import { buttonVariants } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading";
import { ErrorState } from "@/components/ui/error-state";
import { EmptyState } from "@/components/ui/empty-state";
import {
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  ChevronRight,
  Building2,
  Calendar,
} from "lucide-react";

function rowDelta(current: number | null, previous: number | null): string {
  if (current === null || previous === null) return "";
  const diff = current - previous;
  return diff > 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1);
}

export default function CompanyPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(String(params.id), 10);

  const { company, loading, error } = useCompany(id);

  if (isNaN(id)) {
    return (
      <div className="min-h-screen bg-stone-950 text-stone-100 flex items-center justify-center">
        <p className="text-stone-400">Invalid company ID</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      <PageBackground variant="default" />

      <NavHeader />

      <main className="relative z-10 flex-1 py-12 px-4">
        <div className="max-w-3xl mx-auto">
          {loading && <LoadingState />}

          {error && (
            <ErrorState
              title="Failed to load company"
              message="Please try again."
            />
          )}

          {company && (
            <>
              {/* Company header */}
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 rounded-xl bg-stone-900 border border-stone-800 flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-white">{company.name}</h1>
                    <p className="text-sm text-stone-400">
                      {company.sector} &middot; {company.size}
                    </p>
                  </div>
                </div>

                {/* Score & trend metrics */}
                <div className="grid grid-cols-3 gap-3 mt-6">
                  <div className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80">
                    <p className="text-xs text-stone-500 mb-1">Latest Score</p>
                    <p className={`text-2xl font-bold ${scoreTier(company.latestScore).color}`}>
                      {company.latestScore !== null ? company.latestScore.toFixed(1) : "—"}
                    </p>
                  </div>
                  <div className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80">
                    <p className="text-xs text-stone-500 mb-1">Trend</p>
                    <div className="flex items-center gap-1">
                      {company.scoreTrend === "improving" ? (
                        <ArrowUpRight className="w-5 h-5 text-emerald-400" />
                      ) : company.scoreTrend === "declining" ? (
                        <ArrowDownRight className="w-5 h-5 text-rose-400" />
                      ) : (
                        <Minus className="w-5 h-5 text-amber-400" />
                      )}
                      <span className="text-lg font-bold capitalize text-white">
                        {company.scoreTrend}
                      </span>
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80">
                    <p className="text-xs text-stone-500 mb-1">Assessments</p>
                    <p className="text-2xl font-bold text-white">{company.assessmentCount}</p>
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex items-center gap-3 mt-4">
                  <Link
                    href={`/assessment?companyId=${id}`}
                    className={buttonVariants({ variant: "primary", size: "md", className: "flex-1" })}
                  >
                    Re-assess
                  </Link>
                </div>
              </div>

              {/* Assessment timeline */}
              <div>
                <h2 className="text-xl font-semibold text-white mb-4">
                  Score Timeline
                </h2>

                {company.delta !== 0 && (
                  <div className="mb-4 text-sm text-stone-400">
                    {company.delta > 0 ? (
                      <span className="text-emerald-400">
                        +{company.delta.toFixed(1)} since first assessment
                      </span>
                    ) : (
                      <span className="text-rose-400">
                        {company.delta.toFixed(1)} since first assessment
                      </span>
                    )}
                  </div>
                )}

                <div className="flex flex-col gap-2">
                  {(company.assessments ?? []).map((a, i: number) => (
                    <button
                      key={a.id}
                      onClick={() => router.push(`/results/${a.id}`)}
                      className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 group"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold ${scoreTier(a.innovationScore).bg} ${scoreTier(a.innovationScore).color} border`}>
                          #{a.assessmentNumber}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-semibold text-white group-hover:text-amber-300 transition">
                            Assessment #{a.assessmentNumber}
                            {a.periodLabel && (
                              <span className="text-stone-500 ml-1">
                                — {a.periodLabel}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-stone-500 flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {formatDate(a.generatedAt)}
                            </span>
                            {a.scoreDelta !== null && a.scoreDelta !== 0 && (
                              <span className={`text-xs font-semibold ${
                                a.scoreDelta > 0 ? "text-emerald-400" : "text-rose-400"
                              }`}>
                                {a.scoreDelta > 0 ? "+" : ""}{a.scoreDelta.toFixed(1)}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className={`text-right ${scoreTier(a.innovationScore).color}`}>
                          <span className="text-lg font-bold">
                            {a.innovationScore !== null ? a.innovationScore.toFixed(1) : "—"}
                          </span>
                          {i > 0 && (
                            <div className="text-xs text-stone-500">
                              {rowDelta(a.innovationScore, company.assessments[i - 1].innovationScore)}
                            </div>
                          )}
                        </div>
                        <ChevronRight className="w-4 h-4 text-stone-500 group-hover:text-amber-400 transition" />
                      </div>
                    </button>
                  ))}
                </div>

                {(!company.assessments || company.assessments.length === 0) && (
                  <EmptyState
                    title="No assessments yet"
                    action={
                      <Link
                        href="/assessment"
                        className={buttonVariants({ variant: "secondary", size: "sm" })}
                      >
                        Run first assessment
                      </Link>
                    }
                  />
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
