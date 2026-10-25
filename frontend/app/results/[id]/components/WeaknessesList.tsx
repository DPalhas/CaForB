"use client";

import { motion } from "framer-motion";
import { easeOut } from "@/lib/motion";
import { MessageCircle } from "lucide-react";

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
  visible: { opacity: 1, x: 0, transition: { duration: 0.35, ease: easeOut } },
};

export default function WeaknessesList({ weaknesses, onAsk }: WeaknessesListProps) {
  if (!weaknesses.length) return null;

  return (
    <motion.div
      className="bg-amber-950/30 rounded-xl border border-amber-800/40 p-6"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, ease: easeOut }}
    >
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-amber-200">
          Key Strategic Vulnerabilities &amp; Barriers
        </h2>
        <p className="text-xs text-amber-400/70">Risk areas identified from your operational &amp; process inputs</p>
      </div>

      <motion.ul className="space-y-2" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={containerReveal}>
        {weaknesses.map((weakness, index) => (
          <motion.li
            key={index}
            className="group flex items-start gap-3 bg-stone-950/60 p-4 rounded-xl border border-amber-800/40"
            variants={itemReveal}
          >
            <span className="w-2 h-2 rounded-full bg-amber-400 mt-2 flex-shrink-0" />
            <p className="text-sm font-medium text-amber-100 leading-relaxed flex-1">{weakness}</p>
            <button
              onClick={() => onAsk({ index, text: weakness })}
              aria-label="Ask AI about this vulnerability"
              title="Ask AI about this vulnerability"
              className="flex-shrink-0 p-2 rounded-lg text-stone-400 hover:text-amber-300 hover:bg-stone-800/60 transition opacity-0 group-hover:opacity-100 focus-visible:opacity-100 print:hidden"
            >
              <MessageCircle className="w-4 h-4" />
            </button>
          </motion.li>
        ))}
      </motion.ul>
    </motion.div>
  );
}
