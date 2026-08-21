"use client";

import { motion } from "framer-motion";
import { AlertTriangle, MessageCircle } from "lucide-react";

interface WeaknessesListProps {
  weaknesses: string[];
  onAsk: (weakness: { index: number; text: string }) => void;
}

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06, delayChildren: 0.1 } },
};

const itemReveal = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] as const } },
};

export default function WeaknessesList({ weaknesses, onAsk }: WeaknessesListProps) {
  if (!weaknesses.length) return null;

  return (
    <motion.div
      className="bg-amber-950/30 rounded-3xl border border-amber-800/40 p-6 sm:p-7"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] as const }}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-600/40 flex items-center justify-center text-amber-400">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-amber-200">
            Key Strategic Vulnerabilities & Barriers
          </h2>
          <p className="text-xs text-amber-400/70">Risk areas identified from your operational & process inputs</p>
        </div>
      </div>

      <motion.ul className="space-y-2.5" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={containerReveal}>
        {weaknesses.map((weakness, index) => (
          <motion.li
            key={index}
            className="flex items-start gap-3 bg-stone-950/60 p-3.5 rounded-2xl border border-amber-800/40 shadow-2xs"
            variants={itemReveal}
          >
            <span className="w-2 h-2 rounded-full bg-amber-400 mt-2 flex-shrink-0" />
            <p className="text-sm font-medium text-amber-100 leading-relaxed flex-1">{weakness}</p>
            <button
              onClick={() => onAsk({ index, text: weakness })}
              className="flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-stone-900/60 border border-stone-700/60 text-[11px] font-semibold text-stone-300 hover:text-amber-300 hover:border-amber-500/40 transition print:hidden"
            >
              <MessageCircle className="w-3.5 h-3.5" />
              Ask AI
            </button>
          </motion.li>
        ))}
      </motion.ul>
    </motion.div>
  );
}
