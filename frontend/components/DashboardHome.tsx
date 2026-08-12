"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion"
import { easeOut } from "@/lib/easing";
import {
  Plus,
  Building2,
  ChevronRight,
  BarChart3,
} from "lucide-react";

interface CompanyRow {
  id: number;
  name: string;
  sector: string;
  size: string;
  latestScore: number | null;
  latestInsightId: number | null;
  assessmentCount: number;
  createdAt: string;
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

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};

const itemReveal = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: easeOut } },
};

interface DashboardHomeProps {
  companies: CompanyRow[];
}

export default function DashboardHome({ companies }: DashboardHomeProps) {
  const router = useRouter();

  const totalAssessments = companies.reduce((sum, c) => sum + c.assessmentCount, 0);
  const scored = companies.filter((c) => c.latestScore !== null);
  const avgScore = scored.length > 0
    ? scored.reduce((s, c) => s + (c.latestScore ?? 0), 0) / scored.length
    : null;
  const best = scored.length > 0
    ? scored.reduce((best, c) =>
      (c.latestScore ?? 0) > (best.latestScore ?? 0) ? c : best
    )
    : null;

  return (
    <motion.main className="relative z-10 flex-1 py-10 px-4" initial="hidden" animate="visible" variants={containerReveal}>
      <div className="max-w-4xl mx-auto">
        <motion.div className="flex items-center justify-between mb-8" variants={itemReveal}>
          <div>
            <h1 className="text-3xl font-bold text-white">Your Dashboard</h1>
            <p className="text-sm text-stone-400 mt-1">
              Track innovation maturity across your portfolio
            </p>
          </div>
          <Link
            href="/assessment"
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-stone-950 bg-amber-400 rounded-xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>New Assessment</span>
          </Link>
        </motion.div>

        <motion.div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8" variants={containerReveal}>
          {[{ label: "Companies", value: companies.length },
            { label: "Assessments", value: totalAssessments },
            { label: "Avg Score", value: avgScore !== null ? avgScore.toFixed(1) : "—" },
            ...(best ? [{ label: "Highest", value: best.name, sub: `${best.latestScore?.toFixed(1)}`, subColor: scoreColor(best.latestScore) }] : []),
          ].map((m, i) => (
            <motion.div key={i} className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80" variants={itemReveal}>
              <p className="text-xs text-stone-500 mb-1">{m.label}</p>
              <p className="text-xl font-bold text-white">{m.value}</p>
              {(m as any).sub && (
                <p className={`text-lg font-bold ${(m as any).subColor}`}>{(m as any).sub}</p>
              )}
            </motion.div>
          ))}
        </motion.div>

        <div>
          <motion.h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2" variants={itemReveal}>
            <Building2 className="w-5 h-5 text-amber-400" />
            Your Companies
          </motion.h2>
          <motion.div className="flex flex-col gap-3" variants={containerReveal}>
            {companies.map((c) => (
              <motion.button
                key={c.id}
                onClick={() => router.push(`/company/${c.id}`)}
                className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition group"
                variants={itemReveal}
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
                    </div>
                  </div>
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${scoreBg(c.latestScore)} ${scoreColor(c.latestScore)}`}>
                    {c.latestScore !== null ? (
                      <>
                        <span>{scoreLabel(c.latestScore)}</span>
                        <span className="font-mono">{c.latestScore.toFixed(1)}</span>
                      </>
                    ) : (
                      <span>Pending</span>
                    )}
                  </div>
                  <ChevronRight className="w-4 h-4 text-stone-600 group-hover:text-amber-400 transition flex-shrink-0" />
                </div>
              </motion.button>
            ))}
          </motion.div>

          <motion.div className="mt-6 text-center" variants={itemReveal}>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1 text-sm text-amber-400 hover:text-amber-300 transition"
            >
              <BarChart3 className="w-4 h-4" />
              <span>View all companies &amp; assessments</span>
            </Link>
          </motion.div>
        </div>
      </div>
    </motion.main>
  );
}
