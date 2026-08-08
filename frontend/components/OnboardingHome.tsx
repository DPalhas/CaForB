"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { ArrowRight, Clock, Sparkles, Route } from "lucide-react";

export default function OnboardingHome() {
  const { user } = useAuth();

  return (
    <div className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 py-16 max-w-3xl mx-auto">
      <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
        Welcome,{" "}
        <span className="text-amber-400">
          {user?.username}
        </span>
      </h1>
      <p className="text-base sm:text-lg text-stone-400 max-w-xl mb-12 leading-relaxed">
        Let's measure your organization's innovation maturity and get an
        AI-powered strategic roadmap tailored to your context.
      </p>

      {/* Decorative score gauge */}
      <div className="relative flex items-center justify-center mb-12">
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke="rgb(120 113 108)"
            strokeWidth="10"
          />
          <circle
            cx="80"
            cy="80"
            r="70"
            fill="none"
            stroke="#f59e0b"
            strokeWidth="10"
            strokeDasharray="55 385"
            strokeLinecap="round"
            transform="rotate(-90 80 80)"
            className="animate-pulse"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-amber-400">
            ?
          </span>
        </div>
      </div>

      {/* Feature pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl mb-12">
        {[
          {
            icon: <Clock className="w-5 h-5 text-amber-400" />,
            title: "5-Minute Survey",
            desc: "Structured across 5 clear sections",
          },
          {
            icon: <Sparkles className="w-5 h-5 text-orange-400" />,
            title: "AI-Powered Analysis",
            desc: "Gemma4 model with domain context",
          },
          {
            icon: <Route className="w-5 h-5 text-emerald-400" />,
            title: "Actionable Roadmap",
            desc: "Concrete steps, KPIs, and milestones",
          },
        ].map(({ icon, title, desc }, i) => (
          <div
            key={i}
            className="p-5 rounded-2xl bg-stone-900/60 border border-stone-800/80 backdrop-blur-sm text-center"
          >
            <div className="w-10 h-10 rounded-xl bg-stone-950 border border-stone-800 flex items-center justify-center mx-auto mb-3">
              {icon}
            </div>
            <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
            <p className="text-xs text-stone-500">{desc}</p>
          </div>
        ))}
      </div>

      {/* Main CTA */}
      <Link
        href="/assessment"
        className="px-10 py-4 text-base font-semibold text-stone-950 bg-amber-400 rounded-xl hover:opacity-95 transition-all shadow-xl shadow-amber-500/25 flex items-center gap-3 group"
      >
        <span>Start Your First Assessment</span>
        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </Link>
    </div>
  );
}
