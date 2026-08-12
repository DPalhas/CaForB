"use client";

import { motion } from "framer-motion";
import OpportunityCard from "./OpportunityCard";

interface Opportunity {
  type: string;
  title: string;
  rationale: string;
  impact: string;
  difficulty: string;
  timeframe: string;
}

interface OpportunitiesListProps {
  opportunities: Opportunity[];
}

const containerReveal = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.12 } },
};

export default function OpportunitiesList({ opportunities }: OpportunitiesListProps) {
  if (!opportunities.length) return null;

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-40px" }}
      variants={containerReveal}
    >
      <motion.h2 className="text-lg font-semibold text-white mb-4" variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}>
        Innovation Opportunities
      </motion.h2>
      <div className="flex flex-col gap-3">
        {opportunities.map((opp, index) => (
          <OpportunityCard key={index} opportunity={opp} index={index} />
        ))}
      </div>
    </motion.div>
  );
}
