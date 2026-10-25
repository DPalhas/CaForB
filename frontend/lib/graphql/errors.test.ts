import { describe, it, expect } from "vitest";
import { friendlyAssessmentError } from "./errors";

const graphQlError = (message: string) => ({
  graphQLErrors: [{ message }],
});

describe("friendlyAssessmentError", () => {
  it("maps the phase-1 parse failure", () => {
    const e = graphQlError("Phase 1 LLM response could not be parsed");
    expect(friendlyAssessmentError(e).code).toBe("phase1_parse_failed");
  });

  it("maps the no-score failure", () => {
    const e = graphQlError(
      "Assessment generation failed: model returned no maturity score"
    );
    expect(friendlyAssessmentError(e).code).toBe("no_score");
  });

  it("maps a model-not-found failure", () => {
    const e = graphQlError("model gemma4:12B not found");
    expect(friendlyAssessmentError(e).code).toBe("model_not_found");
  });

  it("maps a network failure", () => {
    const e = { networkError: { message: "Failed to fetch" } };
    expect(friendlyAssessmentError(e).code).toBe("network");
  });

  it("falls back to unknown for unrecognized errors", () => {
    expect(friendlyAssessmentError({}).code).toBe("unknown");
  });
});
