"use client";

import { useAuth } from "@/lib/auth-context";
import { useCompanies } from "@/lib/hooks/useCompanies";
import NavHeader from "@/components/NavHeader";
import LandingContent from "@/components/LandingContent";
import OnboardingHome from "@/components/OnboardingHome";
import HomeOverview from "@/components/HomeOverview";
import PageBackground from "@/components/PageBackground";
import { LoadingState } from "@/components/ui/loading";

export default function HomePage() {
  const { user, loading: authLoading } = useAuth();
  const { companies, loading: dataLoading } = useCompanies(!user);

  const bgVariant = !user ? "hero" : "default";

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col selection:bg-amber-500 selection:text-white">
      <PageBackground variant={bgVariant} />

      <NavHeader />

      {authLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <LoadingState />
        </div>
      ) : !user ? (
        <LandingContent />
      ) : dataLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <LoadingState />
        </div>
      ) : companies.length === 0 ? (
        <OnboardingHome />
      ) : (
        <HomeOverview companies={companies} />
      )}
    </div>
  );
}
