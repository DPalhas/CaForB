"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion"
import { easeOut } from "@/lib/motion";
import { scoreTier } from "@/lib/score";
import type { CompanySummary } from "@/lib/types";
import { buttonVariants } from "@/components/ui/button";
import {
  Building2,
  ChevronRight,
} from "lucide-react";

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};

const itemReveal = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: easeOut } },
};

interface HomeOverviewProps {
  companies: CompanySummary[];
}

export default function HomeOverview({ companies }: HomeOverviewProps) {
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
            className={buttonVariants({ variant: "primary", size: "md" })}
          >
            New Assessment
          </Link>
        </motion.div>

        <motion.div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8" variants={containerReveal}>
          {(
            [
              { label: "Companies", value: companies.length },
              { label: "Assessments", value: totalAssessments },
              { label: "Avg Score", value: avgScore !== null ? avgScore.toFixed(1) : "—" },
              ...(best ? [{ label: "Highest", value: best.name, sub: `${best.latestScore?.toFixed(1)}`, subColor: scoreTier(best.latestScore).color }] : []),
            ] as { label: string; value: string | number; sub?: string; subColor?: string }[]
          ).map((m, i) => (
            <motion.div key={i} className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80" variants={itemReveal}>
              <p className="text-xs text-stone-500 mb-1">{m.label}</p>
              <p className="text-xl font-bold text-white">{m.value}</p>
              {m.sub && (
                <p className={`text-lg font-bold ${m.subColor}`}>{m.sub}</p>
              )}
            </motion.div>
          ))}
        </motion.div>

        <div>
          <motion.h2 className="text-xl font-semibold text-white mb-3" variants={itemReveal}>
            Your Companies
          </motion.h2>
          <motion.div className="flex flex-col gap-3" variants={containerReveal}>
            {companies.map((c) => (
              <motion.button
                key={c.id}
                onClick={() => router.push(`/company/${c.id}`)}
                className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 group"
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
                  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${scoreTier(c.latestScore).bg} ${scoreTier(c.latestScore).color}`}>
                    {c.latestScore !== null ? (
                      <>
                        <span>{scoreTier(c.latestScore).label}</span>
                        <span className="font-mono">{c.latestScore.toFixed(1)}</span>
                      </>
                    ) : (
                      <span>Pending</span>
                    )}
                  </div>
                  <ChevronRight className="w-4 h-4 text-stone-500 group-hover:text-amber-400 transition flex-shrink-0" />
                </div>
              </motion.button>
            ))}
          </motion.div>

          <motion.div className="mt-6 text-center" variants={itemReveal}>
            <Link
              href="/dashboard"
              className="text-sm text-amber-400 hover:text-amber-300 transition"
            >
              View all companies &amp; assessments
            </Link>
          </motion.div>
        </div>
      </div>
    </motion.main>
  );
}
