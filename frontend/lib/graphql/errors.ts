export type AssessmentError = {
  code: string;
  message: string;
};

const UNKNOWN = {
  code: "unknown",
  message: "Something went wrong. Please try again.",
};

const MATCHERS: { code: string; match: RegExp; message: string }[] = [
  {
    code: "phase1_parse_failed",
    match: /Phase 1 LLM response could not be parsed/i,
    message:
      "The AI could not produce a complete analysis. This can happen intermittently — please try again.",
  },
  {
    code: "no_score",
    match: /Assessment generation failed: model returned no maturity score/i,
    message:
      "The AI could not produce a score for this assessment. Please try again.",
  },
  {
    code: "empty_response",
    match: /LLM returned empty response/i,
    message:
      "The AI model isn't responding properly. Make sure the AI service is running, then try again.",
  },
  {
    code: "parse_failed",
    match: /LLM response could not be parsed as JSON/i,
    message:
      "The AI produced an unreadable response. Please try again.",
  },
  {
    code: "model_not_found",
    match: /model.*not found|not found.*model|404/i,
    message:
      "The AI model isn't available locally. Run `ollama pull gemma4:12B`, then try again.",
  },
  {
    code: "network",
    match: /Failed to fetch|NetworkError|ERR_CONNECTION|fetch/i,
    message:
      "Could not reach the server. Check your connection and try again.",
  },
];

export function friendlyAssessmentError(err: unknown): AssessmentError {
  const raw =
    (err as any)?.graphQLErrors?.[0]?.message ||
    (err as any)?.networkError?.message ||
    (err as any)?.message ||
    "";

  for (const { code, match, message } of MATCHERS) {
    if (match.test(raw)) {
      return { code, message };
    }
  }

  return UNKNOWN;
}
