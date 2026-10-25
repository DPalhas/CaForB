"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useCompanies } from "@/lib/hooks/useCompanies";
import NavHeader from "@/components/NavHeader";
import PageBackground from "@/components/PageBackground";
import { scoreTier } from "@/lib/score";
import { formatDate } from "@/lib/format";
import { buttonVariants } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading";
import { ErrorState } from "@/components/ui/error-state";
import { EmptyState } from "@/components/ui/empty-state";
import {
  ChevronRight,
  TrendingUp,
  Building2,
  Calendar,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { companies, loading, error } = useCompanies();

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      <PageBackground variant="default" />

      <NavHeader />

      <main className="relative z-10 flex-1 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white">Companies</h1>
              <p className="text-sm text-stone-400 mt-1">
                Your corporate innovation assessment history, grouped by company
              </p>
            </div>
            <Link
              href="/assessment"
              className={buttonVariants({ variant: "primary", size: "md" })}
            >
              New Assessment
            </Link>
          </div>

          {loading && <LoadingState label="Loading companies..." />}

          {error && (
            <ErrorState
              title="Failed to load companies"
              message="Please try again."
            />
          )}

          {!loading && !error && companies.length === 0 && (
            <EmptyState
              icon={<TrendingUp className="w-7 h-7 text-amber-400" />}
              title="No companies yet"
              description="Run your first corporate innovation assessment to receive an AI-powered strategic roadmap."
              action={
                <Link
                  href="/assessment"
                  className={buttonVariants({ variant: "primary", size: "md" })}
                >
                  Start Your First Assessment
                </Link>
              }
            />
          )}

          {!loading && !error && companies.length > 0 && (
            <div className="flex flex-col gap-4">
              {companies.map((c) => (
                <button
                  key={c.id}
                  onClick={() => router.push(`/company/${c.id}`)}
                  className="w-full text-left p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 hover:border-amber-500/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50 group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-stone-950 border border-stone-800 flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-6 h-6 text-amber-400" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <h3 className="text-base font-semibold text-white truncate group-hover:text-amber-300 transition">
                        {c.name}
                      </h3>
                      <div className="flex items-center gap-3 mt-1">
                        <span className="text-xs text-stone-500">{c.sector}</span>
                        <span className="text-xs text-stone-500 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(c.createdAt)}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="text-xs text-stone-500">
                          {c.assessmentCount} assessment{c.assessmentCount !== 1 ? "s" : ""}
                        </span>
                      </div>
                    </div>

                    <div className="text-right flex flex-col items-end gap-1">
                      <div
                        className={`flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-semibold ${scoreTier(c.latestScore).bg} ${scoreTier(c.latestScore).color}`}
                      >
                        {c.latestScore !== null ? (
                          <>
                            <span>{scoreTier(c.latestScore).label}</span>
                            <span className="font-mono">{c.latestScore.toFixed(1)}</span>
                          </>
                        ) : (
                          <span>No assessments</span>
                        )}
                      </div>
                    </div>

                    <ChevronRight className="w-5 h-5 text-stone-500 group-hover:text-amber-400 transition flex-shrink-0" />
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
