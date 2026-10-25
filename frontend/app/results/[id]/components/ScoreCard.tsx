"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { easeOut } from "@/lib/motion";
import { scoreBand } from "@/lib/score";

interface ScoreCardProps {
  score: number;
}

function AnimatedCounter({ value, className }: { value: number; className?: string }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    let raf: number;
    const duration = 1200;
    const start = performance.now();

    const animate = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      setDisplay(progress * value);
      if (progress < 1) {
        raf = requestAnimationFrame(animate);
      }
    };

    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, [value]);

  return <span className={className}>{display.toFixed(1)}</span>;
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const { label, color, bg, fill } = scoreBand(score);
  const percentage = Math.min(100, Math.max(0, (score / 10) * 100));

  return (
    <motion.div
      className="rounded-xl border border-stone-800/80 bg-stone-900/60 p-6 shadow-sm"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: easeOut }}
    >
      <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
        
        {/* Score Circular Metric */}
        <div className="flex items-center gap-6">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-stone-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <motion.path
                strokeWidth="3.5"
                strokeDasharray={`${percentage}, 100`}
                strokeLinecap="round"
                stroke={fill}
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1.2, ease: "easeOut" }}
                style={{ pathLength: 1, strokeDasharray: `${percentage}, 100` }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <AnimatedCounter
                value={score}
                className={`text-3xl font-extrabold tracking-tight font-mono ${color}`}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-400">Innovation Index</span>
              <span className={`text-xs font-bold px-2 py-1 rounded-full border ${bg} ${color}`}>
                {label}
              </span>
            </div>
            <h3 className="text-xl font-bold text-white">Maturity Score</h3>
            <p className="text-xs text-stone-400 max-w-xs mt-1">
              Calculated based on governance structure, digital capability, strategic alignment, and barrier complexity.
            </p>
          </div>
        </div>

      </div>
    </motion.div>
  );
}
