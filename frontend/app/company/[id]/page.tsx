"use client";

import { useQuery } from "@apollo/client/react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { COMPANY_DETAIL } from "@/lib/graphql/queries";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
import {
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  ChevronRight,
  Loader2,
  Building2,
  Calendar,
  TrendingUp,
  RefreshCw,
  Plus,
} from "lucide-react";

function scoreColor(score: number | null): string {
  if (score === null) return "text-stone-400";
  if (score >= 7) return "text-emerald-400";
  if (score >= 4) return "text-amber-400";
  return "text-rose-400";
}

function scoreBg(score: number | null): string {
  if (score === null) return "bg-stone-900/60 border-stone-800";
  if (score >= 7) return "bg-emerald-950/40 border-emerald-800/60";
  if (score >= 4) return "bg-amber-950/40 border-amber-800/60";
  return "bg-rose-950/40 border-rose-800/60";
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function CompanyPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(String(params.id), 10);

  const { data, loading, error } = useQuery(COMPANY_DETAIL, {
    variables: { id },
    skip: isNaN(id),
  });

  const company = (data as any)?.company;

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
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
            </div>
          )}

          {error && (
            <div className="flex items-center gap-3 text-sm text-rose-300 bg-rose-950/40 border border-rose-800/60 rounded-xl p-5">
              <span>Failed to load company.</span>
            </div>
          )}

          {company && (
            <>
              {/* Company header */}
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 rounded-2xl bg-stone-900 border border-stone-800 flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">{company.name}</h1>
                    <p className="text-sm text-stone-400">
                      {company.sector} &middot; {company.size}
                    </p>
                  </div>
                </div>

                {/* Score & trend metrics */}
                <div className="grid grid-cols-3 gap-3 mt-6">
                  <div className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80">
                    <p className="text-xs text-stone-500 mb-1">Latest Score</p>
                    <p className={`text-2xl font-bold ${scoreColor(company.latestScore)}`}>
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
                    className="flex-1 flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Re-assess</span>
                  </Link>
                </div>
              </div>

              {/* Assessment timeline */}
              <div>
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-amber-400" />
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
                  {(company.assessments ?? []).map((a: any, i: number) => (
                    <button
                      key={a.id}
                      onClick={() => router.push(`/results/${a.id}`)}
                      className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition group"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold ${scoreBg(a.innovationScore)} ${scoreColor(a.innovationScore)} border`}>
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
                        <div className={`text-right ${scoreColor(a.innovationScore)}`}>
                          <span className="text-lg font-bold">
                            {a.innovationScore !== null ? a.innovationScore.toFixed(1) : "—"}
                          </span>
                          {i > 0 && (
                            <div className="text-[10px] text-stone-600">
                              {a.innovationScore !== null && company.assessments[i-1].innovationScore !== null
                                ? (a.innovationScore > company.assessments[i-1].innovationScore
                                  ? "+" + (a.innovationScore - company.assessments[i-1].innovationScore).toFixed(1)
                                  : (a.innovationScore - company.assessments[i-1].innovationScore).toFixed(1))
                                : ""}
                            </div>
                          )}
                        </div>
                        <ChevronRight className="w-4 h-4 text-stone-600 group-hover:text-amber-400 transition" />
                      </div>
                    </button>
                  ))}
                </div>

                {(!company.assessments || company.assessments.length === 0) && (
                  <div className="text-center py-12 text-stone-500">
                    <p>No assessments yet.</p>
                    <Link
                      href="/assessment"
                      className="inline-flex items-center gap-1 mt-2 text-sm text-amber-400 hover:text-amber-300"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Run first assessment</span>
                    </Link>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
