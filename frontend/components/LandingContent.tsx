"use client";

import Link from "next/link";
import { motion, useInView } from "framer-motion"
import { easeOut } from "@/lib/motion";
import { useRef } from "react";
import { buttonVariants } from "@/components/ui/button";

const containerReveal = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemReveal = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: easeOut } },
};

function SectionInView({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div
      ref={ref}
      className={className}
      initial="hidden"
      animate={inView ? "visible" : "hidden"}
      variants={containerReveal}
    >
      {children}
    </motion.div>
  );
}

function AnimatedHeading({ text, highlighted }: { text: string; highlighted?: string }) {
  const words = text.split(" ");
  if (!highlighted) {
    return (
      <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-[1.15] max-w-4xl mb-6">
        {words.map((word, i) => (
          <motion.span
            key={i}
            custom={i}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 + i * 0.06, ease: easeOut }}
            className="inline-block mr-[0.25em]"
          >
            {word}
          </motion.span>
        ))}
      </h1>
    );
  }

  const before = text.split(highlighted)[0].trim().split(" ");
  const after = text.split(highlighted)[1].trim().split(" ");
  const allWords = [...before, highlighted, ...after];
  const highlightIndex = before.length;

  return (
    <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-[1.15] max-w-4xl mb-6">
      {allWords.map((word, i) => (
        <motion.span
          key={i}
          custom={i}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 + i * 0.06, ease: easeOut }}
          className={`inline-block mr-[0.25em] ${i === highlightIndex ? "text-amber-400" : ""}`}
        >
          {word}
        </motion.span>
      ))}
    </h1>
  );
}

export default function LandingContent() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-20 lg:py-28 max-w-5xl mx-auto">
        <div className="w-full lg:grid lg:grid-cols-12 lg:gap-12 lg:items-center">
          <div className="lg:col-span-7 text-left">
        <motion.div
          className="inline-flex items-center px-4 py-2 rounded-full bg-amber-950/80 border border-amber-800/60 text-amber-300 text-xs font-semibold uppercase tracking-wider mb-8"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: easeOut }}
        >
          <span>AI-Powered Innovation Advisor</span>
        </motion.div>

        <AnimatedHeading
          text="Transform your corporate context into a strategic roadmap"
          highlighted="strategic roadmap"
        />

        <motion.p
          className="text-lg sm:text-xl text-stone-400 max-w-2xl mb-10 leading-relaxed font-normal"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.0, ease: easeOut }}
        >
          Complete a quick 5-section evaluation of your organization. Receive a
          tailored maturity score, prioritized opportunities, and an actionable
          execution plan powered by specialized AI.
        </motion.p>

        <motion.div
          className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 w-full sm:w-auto"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.2, ease: easeOut }}
        >
          <Link
            href="/assessment"
            className={buttonVariants({ variant: "primary", size: "lg", className: "w-full sm:w-auto" })}
          >
            Begin Free Assessment
          </Link>
        </motion.div>
        </div>

        {/* Right column — Key Metrics */}
        <motion.div
          className="lg:col-span-5 mt-12 lg:mt-0"
          initial="hidden"
          animate="visible"
          variants={containerReveal}
        >
          <div className="grid grid-cols-2 gap-4 w-full text-left">
            {[
              { label: "Completion Time", value: "< 3 Mins", desc: "5 structured sections", accent: "amber" },
              { label: "AI Model", value: "Fine-tuned", desc: "Domain specific context", accent: "indigo" },
              { label: "Output", value: "360 Roadmap", desc: "Scored opportunities", accent: "emerald" },
              { label: "Privacy", value: "Enterprise-grade", desc: "Secure input analysis", accent: "amber" },
            ].map((stat, idx) => {
              const accentMap: Record<string, string> = {
                amber: "text-amber-400 border-amber-800/20 bg-amber-500/5",
                indigo: "text-indigo-400 border-indigo-800/20 bg-indigo-500/5",
                emerald: "text-emerald-400 border-emerald-800/20 bg-emerald-500/5",
              };
              return (
                <motion.div
                  key={idx}
                  className={`p-4 rounded-xl border ${accentMap[stat.accent]}`}
                  variants={itemReveal}
                >
                  <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
                  <p className="text-xs font-semibold uppercase tracking-wider mb-1 opacity-90">{stat.label}</p>
                  <p className="text-xs text-stone-500">{stat.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="relative z-10 bg-stone-900/60 border-t border-b border-stone-800/80 py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <SectionInView className="max-w-2xl mb-16">
            <motion.h2 className="text-3xl font-bold text-white mb-4" variants={itemReveal}>
              Precision Intelligence for Corporate Growth
            </motion.h2>
            <motion.p className="text-stone-400 text-sm sm:text-base" variants={itemReveal}>
              Designed specifically for corporate leaders, strategy managers, and innovation directors.
            </motion.p>
          </SectionInView>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Context-Aware Scoring",
                desc: "Evaluates your company size, regulatory pressure, risk appetite, and budget constraints to filter out unrealistic strategies.",
              },
              {
                title: "Prioritized Opportunities",
                desc: "Distinguishes between quick-win incremental projects and high-impact radical transformations tailored to your industry.",
              },
              {
                title: "Actionable Execution Plans",
                desc: "Get concrete first steps, required resources, key performance indicators, and timeline milestones for immediate adoption.",
              },
            ].map(({ title, desc }, idx) => (
              <SectionInView key={idx}>
                <motion.div
                  className="p-6 rounded-xl bg-stone-950/80 border border-stone-800 hover:border-amber-500/50 transition-colors"
                  variants={itemReveal}
                >
                  <h3 className="text-base font-semibold text-white mb-2">{title}</h3>
                  <p className="text-sm text-stone-400 leading-relaxed">{desc}</p>
                </motion.div>
              </SectionInView>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 py-20 px-6 max-w-5xl mx-auto">
        <SectionInView className="mb-16">
          <motion.h2 className="text-3xl font-bold text-white mb-3" variants={itemReveal}>
            Simple 3-Step Process
          </motion.h2>
          <motion.p className="text-stone-400 text-sm" variants={itemReveal}>
            From baseline assessment to executive implementation
          </motion.p>
        </SectionInView>

        <SectionInView className="grid md:grid-cols-3 gap-6 relative">
          {[
            { step: "01", title: "Assessment Input", desc: "Share details on your process, team capabilities, budget, and strategic priorities." },
            { step: "02", title: "LLM Processing", desc: "Our model cross-examines your responses with corporate innovation frameworks." },
            { step: "03", title: "Strategy Delivery", desc: "Receive your maturity score and tailored roadmap immediately on screen." },
          ].map((item, idx) => (
            <motion.div
              key={idx}
              className="p-6 rounded-xl bg-stone-900/40 border border-stone-800"
              variants={itemReveal}
            >
              <span className="text-4xl font-extrabold text-amber-500/20 font-mono block mb-4">{item.step}</span>
              <h3 className="text-base font-bold text-white mb-2">{item.title}</h3>
              <p className="text-xs text-stone-400 leading-relaxed">{item.desc}</p>
            </motion.div>
          ))}
        </SectionInView>

        <motion.div
          className="mt-16"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, ease: easeOut }}
        >
          <Link
            href="/assessment"
            className={buttonVariants({ variant: "secondary", size: "lg" })}
          >
            Launch Assessment Now
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-stone-800/80 bg-stone-950 py-8 px-6 text-center text-xs text-stone-500">
        <p>© {new Date().getFullYear()} CaForB — Corporate Innovation Decision Support System. All rights reserved.</p>
      </footer>
    </>
  );
}
