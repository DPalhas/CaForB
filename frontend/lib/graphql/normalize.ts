import type { Insight } from "@/lib/types";

function dedupeKey(item: unknown): string {
  const i = item as {
    type?: string;
    title?: string;
    rationale?: string;
    action?: string;
  };
  return `${i.type ?? ""}|${i.title ?? ""}|${i.rationale ?? ""}|${i.action ?? ""}`;
}

export function dedupe<T>(arr: T[] | undefined | null): T[] {
  if (!arr) return [];
  const seen = new Set<string>();
  return arr.filter((item) => {
    const key = dedupeKey(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function normalize(raw: Insight | null | undefined): Insight | null {
  if (!raw) return null;
  return {
    ...raw,
    opportunities: dedupe(raw.opportunities),
    nextSteps: dedupe(raw.nextSteps),
    keyWeaknesses: [...new Set(raw.keyWeaknesses ?? [])],
  };
}
