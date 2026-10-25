import { describe, it, expect } from "vitest";
import { EMPTY_FORM } from "./types";
import { isStepValid, buildAnswers, assessmentFromPrevious } from "./assessment";

describe("isStepValid", () => {
  it("accepts a fully-filled first step", () => {
    const form = {
      ...EMPTY_FORM,
      companyName: "Acme",
      sector: "SaaS / Software",
      size: "Medium",
      companyDescription: "desc",
    };
    expect(isStepValid(form, 0)).toBe(true);
  });

  it("rejects a first step missing a required field", () => {
    expect(isStepValid({ ...EMPTY_FORM, companyName: "Acme" }, 0)).toBe(false);
  });

  it("requires at least one barrier on the last step", () => {
    expect(isStepValid({ ...EMPTY_FORM, mainBarrier: [] }, 4)).toBe(false);
    expect(isStepValid({ ...EMPTY_FORM, mainBarrier: ["budget"] }, 4)).toBe(true);
  });
});

describe("buildAnswers", () => {
  it("maps camelCase form fields to snake_case answer keys", () => {
    const form = { ...EMPTY_FORM, companyDescription: "d", innovationProcess: "formal" };
    const answers = buildAnswers(form);
    expect(answers.company_description).toBe("d");
    expect(answers.innovation_process).toBe("formal");
    expect(answers.budgetPercentage).toBe(EMPTY_FORM.budgetPercentage);
    expect(answers.main_barrier).toEqual([]);
  });
});

describe("assessmentFromPrevious", () => {
  it("rehydrates from stored snake_case answers", () => {
    const prev = {
      companyName: "Acme",
      sector: "IT",
      size: "Small",
      previousAnswers: JSON.stringify({
        innovation_process: "informal",
        main_barrier: ["talent"],
      }),
    };
    const form = assessmentFromPrevious(prev);
    expect(form.companyName).toBe("Acme");
    expect(form.innovationProcess).toBe("informal");
    expect(form.mainBarrier).toEqual(["talent"]);
  });

  it("tolerates malformed previousAnswers JSON", () => {
    const form = assessmentFromPrevious({
      companyName: "Acme",
      previousAnswers: "{not json",
    });
    expect(form.companyName).toBe("Acme");
    expect(form.innovationProcess).toBe("");
  });
});
