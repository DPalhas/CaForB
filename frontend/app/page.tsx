"use client";

import { useQuery } from "@apollo/client/react";
import { useAuth } from "@/lib/auth-context";
import { MY_COMPANIES } from "@/lib/graphql/queries";
import NavHeader from "@/components/NavHeader";
import LandingContent from "@/components/LandingContent";
import OnboardingHome from "@/components/OnboardingHome";
import DashboardHome from "@/components/DashboardHome";
import PageBackground from "@/components/PageBackground";
import { Loader2 } from "lucide-react";

export default function HomePage() {
  const { user, loading: authLoading } = useAuth();
  const { data, loading: dataLoading } = useQuery(MY_COMPANIES, {
    skip: !user,
  });

  const companies = (data as any)?.myCompanies ?? [];
  const bgVariant = !user ? "hero" : "default";

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      <PageBackground variant={bgVariant} />

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
      ) : companies.length === 0 ? (
        <OnboardingHome />
      ) : (
        <DashboardHome companies={companies} />
      )}
    </div>
  );
}
