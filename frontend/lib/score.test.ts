import { describe, it, expect } from "vitest";
import { scoreTier, scoreBand } from "./score";

describe("scoreTier (3-tier)", () => {
  it("returns neutral tier for null", () => {
    expect(scoreTier(null)).toEqual({
      color: "text-stone-400",
      bg: "bg-stone-900/60 border-stone-800",
      label: "—",
    });
  });

  it("labels a high score Advanced", () => {
    expect(scoreTier(8.2).label).toBe("Advanced");
    expect(scoreTier(7).label).toBe("Advanced");
  });

  it("labels a mid score Developing", () => {
    expect(scoreTier(4).label).toBe("Developing");
    expect(scoreTier(6.9).label).toBe("Developing");
  });

  it("labels a low score Early Stage", () => {
    expect(scoreTier(3.9).label).toBe("Early Stage");
    expect(scoreTier(0).label).toBe("Early Stage");
  });
});

describe("scoreBand (4-tier)", () => {
  it("returns Early Stage for <= 3", () => {
    expect(scoreBand(2)).toMatchObject({ label: "Early Stage", fill: "#e11d48" });
  });
  it("returns Developing for 4-5", () => {
    expect(scoreBand(5)).toMatchObject({ label: "Developing", fill: "#fb923c" });
  });
  it("returns Established for 6-7", () => {
    expect(scoreBand(7)).toMatchObject({ label: "Established", fill: "#10b981" });
  });
  it("returns Advanced Leader above 7", () => {
    expect(scoreBand(8)).toMatchObject({ label: "Advanced Leader", fill: "#fbbf24" });
  });
});
