"use client";

import Link from "next/link";
import { motion } from "framer-motion"
import { easeOut } from "@/lib/motion";
import { useAuth } from "@/lib/auth-context";
import { buttonVariants } from "@/components/ui/button";

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.12, delayChildren: 0.15 } },
};

const itemReveal = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: easeOut } },
};

export default function OnboardingHome() {
  const { user } = useAuth();

  return (
    <motion.div
      className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 py-16 max-w-3xl mx-auto"
      initial="hidden"
      animate="visible"
      variants={containerReveal}
    >
      <motion.h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-3" variants={itemReveal}>
        Welcome,{" "}
        <span className="text-amber-400">
          {user?.username}
        </span>
      </motion.h1>
      <motion.p className="text-base sm:text-lg text-stone-400 max-w-xl mb-12 leading-relaxed" variants={itemReveal}>
        Let&apos;s measure your organization&apos;s innovation maturity and get an
        AI-powered strategic roadmap tailored to your context.
      </motion.p>

      <motion.div className="relative flex items-center justify-center mb-12" variants={itemReveal}>
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="70" fill="none" stroke="rgb(120 113 108)" strokeWidth="10" />
          <circle cx="80" cy="80" r="70" fill="none" stroke="#f59e0b" strokeWidth="10"
            strokeDasharray="55 385" strokeLinecap="round" transform="rotate(-90 80 80)" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-amber-400 text-3xl font-bold">?</span>
        </div>
      </motion.div>

      <motion.div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl mb-12" variants={containerReveal}>
        {[
          { title: "5-Minute Survey", desc: "Structured across 5 clear sections" },
          { title: "AI-Powered Analysis", desc: "Gemma4 model with domain context" },
          { title: "Actionable Roadmap", desc: "Concrete steps, KPIs, and milestones" },
        ].map(({ title, desc }, i) => (
          <motion.div key={i} className="p-4 rounded-xl bg-stone-900/60 border border-stone-800/80 text-center" variants={itemReveal}>
            <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
            <p className="text-xs text-stone-500">{desc}</p>
          </motion.div>
        ))}
      </motion.div>

      <motion.div variants={itemReveal}>
        <Link
          href="/assessment"
          className={buttonVariants({ variant: "primary", size: "lg" })}
        >
          Start Your First Assessment
        </Link>
      </motion.div>
    </motion.div>
  );
}
