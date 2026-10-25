export interface ScoreTier {
  color: string;
  bg: string;
  label: string;
}

// 3-tier maturity banding used by the dashboard and company cards.
// Thresholds and class strings copied verbatim from the original
// scoreColor/scoreBg/scoreLabel helpers (no visual change).
export function scoreTier(score: number | null): ScoreTier {
  if (score === null) {
    return {
      color: "text-stone-400",
      bg: "bg-stone-900/60 border-stone-800",
      label: "—",
    };
  }
  if (score >= 7) {
    return {
      color: "text-emerald-400",
      bg: "bg-emerald-950/40 border-emerald-800/60",
      label: "Advanced",
    };
  }
  if (score >= 4) {
    return {
      color: "text-amber-400",
      bg: "bg-amber-950/40 border-amber-800/60",
      label: "Developing",
    };
  }
  return {
    color: "text-rose-400",
    bg: "bg-rose-950/40 border-rose-800/60",
    label: "Early Stage",
  };
}

export interface ScoreBand {
  label: string;
  color: string;
  bg: string;
  fill: string;
}

// 4-tier banding used only by the results ScoreCard (distinct scale from
// scoreTier — do not merge them). `fill` values are SVG stroke colors: CSS
// var() is not supported in SVG presentation attributes, so these remain
// exact hex literals (unchanged from the original getScoreLabel).
export function scoreBand(score: number): ScoreBand {
  if (score <= 3) {
    return {
      label: "Early Stage",
      color: "text-rose-300",
      bg: "bg-rose-950/40 border-rose-800/40",
      fill: "#e11d48",
    };
  }
  if (score <= 5) {
    return {
      label: "Developing",
      color: "text-amber-300",
      bg: "bg-amber-950/40 border-amber-800/40",
      fill: "#fb923c",
    };
  }
  if (score <= 7) {
    return {
      label: "Established",
      color: "text-emerald-300",
      bg: "bg-emerald-950/40 border-emerald-800/40",
      fill: "#10b981",
    };
  }
  return {
    label: "Advanced Leader",
    color: "text-yellow-300",
    bg: "bg-yellow-950/40 border-yellow-800/40",
    fill: "#fbbf24",
  };
}
