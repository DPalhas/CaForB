import { describe, it, expect } from "vitest";
import { dedupe, normalize } from "./normalize";
import type { Insight } from "@/lib/types";

describe("dedupe", () => {
  it("removes items with identical type/title/rationale/action", () => {
    const a = { type: "incremental", title: "A", rationale: "r", action: "" };
    const b = { type: "incremental", title: "A", rationale: "r", action: "" };
    const c = { type: "radical", title: "B", rationale: "r", action: "" };
    expect(dedupe([a, b, c])).toHaveLength(2);
  });

  it("returns empty for null/undefined", () => {
    expect(dedupe(null)).toEqual([]);
    expect(dedupe(undefined)).toEqual([]);
  });

  it("keeps distinct actions", () => {
    const a = { action: "x" };
    const b = { action: "y" };
    expect(dedupe([a, b])).toHaveLength(2);
  });
});

describe("normalize", () => {
  it("returns null for falsy input", () => {
    expect(normalize(null)).toBeNull();
    expect(normalize(undefined)).toBeNull();
  });

  it("dedupes opportunities/nextSteps and unique-ifies weaknesses", () => {
    const raw = {
      id: 1,
      aiOutput: "",
      innovationScore: 5,
      scoreDelta: 0,
      opportunities: [
        { id: "1", type: "t", title: "o", rationale: "r", impact: "", difficulty: "", timeframe: "" },
        { id: "2", type: "t", title: "o", rationale: "r", impact: "", difficulty: "", timeframe: "" },
      ],
      nextSteps: [{ id: "1", action: "s", owner: "", timeframe: "" }, { id: "2", action: "s", owner: "", timeframe: "" }],
      keyWeaknesses: ["w", "w", "x"],
      assessmentNumber: 1,
      companyName: "",
      sector: "",
      size: "",
      previousAnswers: "",
      modelName: "",
      isSelected: false,
    } as unknown as Insight;
    const out = normalize(raw)!;
    expect(out.opportunities).toHaveLength(1);
    expect(out.nextSteps).toHaveLength(1);
    expect(out.keyWeaknesses).toEqual(["w", "x"]);
  });
});
