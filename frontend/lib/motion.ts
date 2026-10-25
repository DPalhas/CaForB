// Shared framer-motion easing. The reveal variants (containerReveal /
// itemReveal) intentionally remain local to each file for now — they differ
// per component (stagger/delay/axis) and are slated for a parametrized
// factory in a later phase.
export const easeOut = [0.22, 1, 0.36, 1] as const;
