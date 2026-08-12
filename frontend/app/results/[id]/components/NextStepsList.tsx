"use client";

import { motion } from "framer-motion";
import { CheckSquare, User, Clock } from "lucide-react";

interface NextStep {
  action: string;
  owner: string;
  timeframe: string;
}

interface NextStepsListProps {
  steps: NextStep[];
}

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};

const itemReveal = {
  hidden: { opacity: 0, x: -16 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] as const } },
};

export default function NextStepsList({ steps }: NextStepsListProps) {
  if (!steps.length) return null;

  return (
    <motion.div
      className="bg-amber-950/80 rounded-3xl p-7 text-white shadow-xl shadow-amber-950/20 border border-amber-800/40"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as const }}
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
          <CheckSquare className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Immediate Executive Next Steps
          </h2>
          <p className="text-xs text-stone-400">Prioritized implementation roadmap for leadership alignment</p>
        </div>
      </div>

      <motion.ol className="space-y-4" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={containerReveal}>
        {steps.map((step, index) => (
          <motion.li
            key={index}
            className="bg-stone-900/80 rounded-2xl p-5 border border-stone-800/80 hover:border-amber-500/40 transition flex items-start gap-4"
            variants={itemReveal}
          >
            <span className="w-7 h-7 rounded-xl bg-amber-400 text-stone-950 font-extrabold text-xs flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md">
              {index + 1}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-stone-100 leading-relaxed">{step.action}</p>
              <div className="flex flex-wrap gap-2.5 mt-3">
                <span className="text-xs font-semibold text-amber-300 bg-amber-950/80 px-3 py-1 rounded-lg border border-amber-800/60 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-amber-400" />
                  {step.owner}
                </span>
                <span className="text-xs font-semibold text-stone-300 bg-stone-800/80 px-3 py-1 rounded-lg border border-stone-700/60 flex items-center gap-1.5 font-mono">
                  <Clock className="w-3.5 h-3.5 text-stone-400" />
                  {step.timeframe}
                </span>
              </div>
            </div>
          </motion.li>
        ))}
      </motion.ol>
    </motion.div>
  );
}
