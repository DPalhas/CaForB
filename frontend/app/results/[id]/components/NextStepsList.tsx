"use client";

import { motion } from "framer-motion";
import { easeOut } from "@/lib/motion";
import { User, Clock, MessageCircle } from "lucide-react";

interface NextStep {
  id: string;
  action: string;
  owner: string;
  timeframe: string;
}

interface NextStepsListProps {
  steps: NextStep[];
  onAsk: (step: { id: string; action: string }) => void;
}

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
};

const itemReveal = {
  hidden: { opacity: 0, x: -16 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.4, ease: easeOut } },
};

export default function NextStepsList({ steps, onAsk }: NextStepsListProps) {
  if (!steps.length) return null;

  return (
    <motion.div
      className="bg-amber-950/80 rounded-xl p-6 text-white border border-amber-800/40"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, ease: easeOut }}
    >
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-white tracking-tight">
          Immediate Executive Next Steps
        </h2>
        <p className="text-xs text-stone-400">Prioritized implementation roadmap for leadership alignment</p>
      </div>

      <motion.ol className="space-y-4" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={containerReveal}>
        {steps.map((step, index) => (
          <motion.li
            key={index}
            className="group bg-stone-900/80 rounded-xl p-4 border border-stone-800/80 hover:border-amber-500/40 transition-colors flex items-start gap-4"
            variants={itemReveal}
          >
            <span className="w-7 h-7 rounded-lg bg-amber-400 text-stone-950 font-extrabold text-xs flex items-center justify-center flex-shrink-0 mt-1">
              {index + 1}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-stone-100 leading-relaxed">{step.action}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="text-xs font-semibold text-amber-300 bg-amber-950/80 px-3 py-1 rounded-lg border border-amber-800/60 flex items-center gap-2">
                  <User className="w-3.5 h-3.5 text-amber-400" />
                  {step.owner}
                </span>
                <span className="text-xs font-semibold text-stone-300 bg-stone-800/80 px-3 py-1 rounded-lg border border-stone-700/60 flex items-center gap-2 font-mono">
                  <Clock className="w-3.5 h-3.5 text-stone-400" />
                  {step.timeframe}
                </span>
              </div>
            </div>
            <button
              onClick={() => onAsk({ id: step.id, action: step.action })}
              aria-label="Ask AI about this next step"
              title="Ask AI about this next step"
              className="flex-shrink-0 p-2 rounded-lg text-stone-400 hover:text-amber-300 hover:bg-stone-800/60 transition opacity-0 group-hover:opacity-100 focus-visible:opacity-100 print:hidden"
            >
              <MessageCircle className="w-4 h-4" />
            </button>
          </motion.li>
        ))}
      </motion.ol>
    </motion.div>
  );
}
