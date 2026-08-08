"use client";

import { useQuery } from "@apollo/client/react";
import { useAuth } from "@/lib/auth-context";
import { MY_INSIGHTS } from "@/lib/graphql/queries";
import NavHeader from "@/components/NavHeader";
import LandingContent from "@/components/LandingContent";
import OnboardingHome from "@/components/OnboardingHome";
import DashboardHome from "@/components/DashboardHome";
import { Loader2 } from "lucide-react";

export default function HomePage() {
  const { user, loading: authLoading } = useAuth();
  const { data, loading: dataLoading } = useQuery(MY_INSIGHTS, {
    skip: !user,
  });

  const assessments = (data as any)?.myInsights ?? [];

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      {/* Background Glow Overlay */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-amber-500/15 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -right-40 w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl" />
      </div>

      <NavHeader />

      {authLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
        </div>
      ) : !user ? (
        <LandingContent />
      ) : dataLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
        </div>
      ) : assessments.length === 0 ? (
        <OnboardingHome />
      ) : (
        <DashboardHome assessments={assessments} />
      )}
    </div>
  );
}
