"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Plus,
  TrendingUp,
  Trophy,
  CalendarDays,
  BarChart3,
  ChevronRight,
  Building2,
} from "lucide-react";

interface AssessmentRow {
  id: number;
  companyName: string;
  sector: string;
  innovationScore: number | null;
  submittedAt: string;
}

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

function formatRelative(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const days = Math.floor(diff / 86400000);
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

export default function DashboardHome({
  assessments,
}: {
  assessments: AssessmentRow[];
}) {
  const router = useRouter();

  const scored = assessments.filter((a) => a.innovationScore !== null);
  const avgScore =
    scored.length > 0
      ? scored.reduce((s, a) => s + a.innovationScore!, 0) / scored.length
      : null;
  const maxAssess = scored.length > 0
    ? scored.reduce((best, a) => (a.innovationScore! > best.innovationScore! ? a : best))
    : null;

  const earlyCount = scored.filter((a) => a.innovationScore! < 4).length;
  const devCount = scored.filter(
    (a) => a.innovationScore! >= 4 && a.innovationScore! < 7
  ).length;
  const advCount = scored.filter((a) => a.innovationScore! >= 7).length;
  const unknownCount = assessments.length - scored.length;

  const recent = assessments.slice(0, 5);

  return (
    <main className="relative z-10 flex-1 py-10 px-4">
      <div className="max-w-5xl mx-auto space-y-10">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">
              Innovation Dashboard
            </h1>
            <p className="text-sm text-stone-400 mt-1">
              Aggregated insights across {assessments.length}{" "}
              {assessments.length === 1 ? "assessment" : "assessments"}
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

        {/* Metrics strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-stone-900/60 border border-stone-800/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider">
                Assessments
              </span>
            </div>
            <p className="text-3xl font-bold text-white">{assessments.length}</p>
          </div>

          <div className="p-5 rounded-2xl bg-stone-900/60 border border-stone-800/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider">
                Avg. Score
              </span>
            </div>
            <p className="text-3xl font-bold text-white">
              {avgScore !== null ? avgScore.toFixed(1) : "—"}
            </p>
            {avgScore !== null && (
              <span className={`text-xs font-semibold ${scoreColor(avgScore)}`}>
                {scoreLabel(avgScore)}
              </span>
            )}
          </div>

          <div className="p-5 rounded-2xl bg-stone-900/60 border border-stone-800/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider">
                Highest
              </span>
            </div>
            <p className="text-3xl font-bold text-white">
              {maxAssess ? maxAssess.innovationScore!.toFixed(1) : "—"}
            </p>
            {maxAssess && (
              <span className="text-xs text-stone-500 truncate block">
                {maxAssess.companyName}
              </span>
            )}
          </div>

          <div className="p-5 rounded-2xl bg-stone-900/60 border border-stone-800/80 backdrop-blur-sm">
            <div className="flex items-center gap-2 mb-2">
              <CalendarDays className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-stone-400 uppercase tracking-wider">
                Latest
              </span>
            </div>
            <p className="text-base font-bold text-white truncate">
              {assessments[0].companyName}
            </p>
            <span className="text-xs text-stone-500">
              {formatRelative(assessments[0].submittedAt)}
            </span>
          </div>
        </div>

        {/* Score distribution */}
        {scored.length > 0 && (
          <div className="p-6 rounded-2xl bg-stone-900/60 border border-stone-800/80 backdrop-blur-sm">
            <h3 className="text-sm font-semibold text-stone-300 mb-4">
              Maturity Distribution
            </h3>
            <div className="flex gap-2 h-6 rounded-full overflow-hidden bg-stone-950/80">
              {earlyCount > 0 && (
                <div
                  className="bg-rose-500/60 flex items-center justify-center text-xs font-semibold text-white"
                  style={{ width: `${(earlyCount / scored.length) * 100}%` }}
                >
                  {earlyCount}
                </div>
              )}
              {devCount > 0 && (
                <div
                  className="bg-amber-500/60 flex items-center justify-center text-xs font-semibold text-white"
                  style={{ width: `${(devCount / scored.length) * 100}%` }}
                >
                  {devCount}
                </div>
              )}
              {advCount > 0 && (
                <div
                  className="bg-emerald-500/60 flex items-center justify-center text-xs font-semibold text-white"
                  style={{ width: `${(advCount / scored.length) * 100}%` }}
                >
                  {advCount}
                </div>
              )}
              {unknownCount > 0 && (
                <div
                  className="bg-stone-700/60"
                  style={{ width: `${(unknownCount / assessments.length) * 100}%` }}
                />
              )}
            </div>
            <div className="flex flex-wrap gap-4 mt-3 text-xs">
              <span className="flex items-center gap-1.5 text-stone-400">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500/60" />
                Early Stage ({earlyCount})
              </span>
              <span className="flex items-center gap-1.5 text-stone-400">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
                Developing ({devCount})
              </span>
              <span className="flex items-center gap-1.5 text-stone-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/60" />
                Advanced ({advCount})
              </span>
            </div>
          </div>
        )}

        {/* Recent assessments */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-stone-300">
              Recent Assessments
            </h3>
            {assessments.length > 5 && (
              <Link
                href="/dashboard"
                className="text-xs font-semibold text-amber-400 hover:text-amber-300 transition"
              >
                View all →
              </Link>
            )}
          </div>

          <div className="flex flex-col gap-3">
            {recent.map((a) => (
              <button
                key={a.id}
                onClick={() => router.push(`/results/${a.id}`)}
                className="w-full text-left p-4 rounded-2xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-stone-950 border border-stone-800 flex items-center justify-center flex-shrink-0">
                    <Building2 className="w-5 h-5 text-amber-400" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-white truncate group-hover:text-amber-300 transition">
                      {a.companyName}
                    </h4>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-xs text-stone-500">{a.sector}</span>
                      <span className="text-xs text-stone-600">
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

                  <ChevronRight className="w-4 h-4 text-stone-600 group-hover:text-amber-400 transition flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
