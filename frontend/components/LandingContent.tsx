import Link from "next/link";
import { Sparkles, ArrowRight, Zap, Target, TrendingUp } from "lucide-react";

export default function LandingContent() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 py-20 lg:py-28 max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-950/80 border border-amber-800/60 text-amber-300 text-xs font-semibold uppercase tracking-wider mb-8 shadow-inner">
          <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
          <span>AI-Powered Innovation Advisor</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.15] max-w-4xl mb-6">
          Transform your corporate context into a{" "}
          <span className="text-amber-400">
            strategic roadmap
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-stone-400 max-w-2xl mb-10 leading-relaxed font-normal">
          Complete a quick 5-section evaluation of your organization. Receive a
          tailored maturity score, prioritized opportunities, and an actionable
          execution plan powered by specialized AI.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto">
          <Link
            href="/assessment"
            className="w-full sm:w-auto px-8 py-4 text-base font-semibold text-stone-950 bg-amber-400 rounded-xl hover:opacity-95 transition-all shadow-xl shadow-amber-500/25 flex items-center justify-center gap-3 group"
          >
            <span>Begin Free Assessment</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Key Metrics / Highlights strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 pt-12 border-t border-stone-800/80 w-full max-w-4xl text-left">
          {[
            { label: "Completion Time", value: "< 3 Mins", desc: "5 structured sections" },
            { label: "AI Model", value: "Fine-tuned", desc: "Domain specific context" },
            { label: "Output", value: "360° Roadmap", desc: "Scored opportunities" },
            { label: "Privacy", value: "Enterprise-grade", desc: "Secure input analysis" },
          ].map((stat, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-stone-900/50 border border-stone-800/60 backdrop-blur-sm">
              <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
              <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">{stat.label}</p>
              <p className="text-xs text-stone-500">{stat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="relative z-10 bg-stone-900/60 border-t border-b border-stone-800/80 py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Precision Intelligence for Corporate Growth</h2>
            <p className="text-stone-400 text-sm sm:text-base">
              Designed specifically for corporate leaders, strategy managers, and innovation directors looking to make data-backed bets.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Target className="w-6 h-6 text-amber-400" />,
                title: "Context-Aware Scoring",
                desc: "Evaluates your company size, regulatory pressure, risk appetite, and budget constraints to filter out unrealistic strategies.",
              },
              {
                icon: <Zap className="w-6 h-6 text-orange-400" />,
                title: "Prioritized Opportunities",
                desc: "Distinguishes between quick-win incremental projects and high-impact radical transformations tailored to your industry.",
              },
              {
                icon: <TrendingUp className="w-6 h-6 text-emerald-400" />,
                title: "Actionable Execution Plans",
                desc: "Get concrete first steps, required resources, key performance indicators, and timeline milestones for immediate adoption.",
              },
            ].map(({ icon, title, desc }, idx) => (
              <div
                key={idx}
                className="p-8 rounded-2xl bg-stone-950/80 border border-stone-800 hover:border-amber-500/50 transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-stone-900 border border-stone-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  {icon}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
                <p className="text-sm text-stone-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 py-20 px-6 max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-white mb-3">Simple 3-Step Process</h2>
          <p className="text-stone-400 text-sm">From baseline assessment to executive implementation</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 relative">
          {[
            { step: "01", title: "Assessment Input", desc: "Share details on your process, team capabilities, budget, and strategic priorities." },
            { step: "02", title: "LLM Processing", desc: "Our model cross-examines your responses with corporate innovation frameworks." },
            { step: "03", title: "Strategy Delivery", desc: "Receive your maturity score and tailored roadmap immediately on screen." },
          ].map((item, idx) => (
            <div key={idx} className="p-6 rounded-2xl bg-stone-900/40 border border-stone-800 relative">
              <span className="text-4xl font-extrabold text-amber-500/20 font-mono block mb-4">{item.step}</span>
              <h3 className="text-base font-bold text-white mb-2">{item.title}</h3>
              <p className="text-xs text-stone-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <Link
            href="/assessment"
            className="inline-flex items-center gap-2 px-8 py-4 text-base font-semibold text-stone-950 bg-amber-400 rounded-xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20"
          >
            <span>Launch Assessment Now</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-stone-800/80 bg-stone-950 py-8 px-6 text-center text-xs text-stone-500">
        <p>© {new Date().getFullYear()} CaForB — Corporate Innovation Decision Support System. All rights reserved.</p>
      </footer>
    </>
  );
}
