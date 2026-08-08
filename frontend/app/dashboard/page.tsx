"use client";

import { useQuery } from "@apollo/client/react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { MY_INSIGHTS } from "@/lib/graphql/queries";
import { useAuth } from "@/lib/auth-context";
import NavHeader from "@/components/NavHeader";
import {
  ChevronRight,
  Plus,
  TrendingUp,
  AlertCircle,
  Loader2,
  Building2,
  Calendar,
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

function scoreLabel(score: number | null): string {
  if (score === null) return "—";
  if (score >= 7) return "Advanced";
  if (score >= 4) return "Developing";
  return "Early Stage";
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function DashboardPage() {
  const router = useRouter();
  const { loading: authLoading } = useAuth();
  const { data, loading, error } = useQuery(MY_INSIGHTS);

  const assessments = (data as any)?.myInsights ?? [];

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-amber-500/15 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -right-40 w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl" />
      </div>

      <NavHeader />

      <main className="relative z-10 flex-1 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white">My Assessments</h1>
              <p className="text-sm text-stone-400 mt-1">
                Your corporate innovation assessment history
              </p>
            </div>
            <Link
              href="/assessment"
              className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20"
            >
              <Plus className="w-4 h-4" />
              <span>New Assessment</span>
            </Link>
          </div>

          {loading && (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
              <p className="text-sm text-stone-400">Loading assessments...</p>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-3 text-sm text-rose-300 bg-rose-950/40 border border-rose-800/60 rounded-xl p-5">
              <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
              <span>Failed to load assessments. Please try again.</span>
            </div>
          )}

          {!loading && !error && assessments.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
              <div className="w-16 h-16 rounded-2xl bg-stone-900 border border-stone-800 flex items-center justify-center">
                <TrendingUp className="w-7 h-7 text-amber-400" />
              </div>
              <h2 className="text-xl font-bold text-white">No assessments yet</h2>
              <p className="text-sm text-stone-400 max-w-sm">
                Run your first corporate innovation assessment to receive an
                AI-powered strategic roadmap.
              </p>
              <Link
                href="/assessment"
                className="mt-2 px-6 py-3 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20"
              >
                Start Your First Assessment
              </Link>
            </div>
          )}

          {!loading && !error && assessments.length > 0 && (
            <div className="flex flex-col gap-3">
              {assessments.map((a: any) => (
                <button
                  key={a.id}
                  onClick={() => router.push(`/results/${a.id}`)}
                  className="w-full text-left p-5 rounded-2xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-stone-950 border border-stone-800 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-5 h-5 text-amber-400" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-semibold text-white truncate group-hover:text-amber-300 transition">
                        {a.companyName}
                      </h3>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-stone-500">{a.sector}</span>
                        <span className="flex items-center gap-1 text-xs text-stone-600">
                          <Calendar className="w-3 h-3" />
                          {formatDate(a.submittedAt)}
                        </span>
                      </div>
                    </div>

                    <div
                      className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${scoreBg(a.innovationScore)} ${scoreColor(a.innovationScore)}`}
                    >
                      <span>{scoreLabel(a.innovationScore)}</span>
                      <span className="font-mono">
                        {a.innovationScore !== null
                          ? a.innovationScore.toFixed(1)
                          : "—"}
                      </span>
                    </div>

                    <ChevronRight className="w-5 h-5 text-stone-600 group-hover:text-amber-400 transition flex-shrink-0" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
