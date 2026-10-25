import { AssessmentFormData } from "@/lib/types";

export const STEP_LABELS = [
  "Company",
  "Innovation",
  "Strategy",
  "Capabilities",
  "Barriers",
];

export const STEP_REQUIRED: (keyof AssessmentFormData)[][] = [
  ["companyName", "sector", "size", "companyDescription"],
  ["innovationProcess", "customerFeedback"],
  ["strategicGoals", "timeHorizon"],
  ["teamSize", "digitalMaturity", "budgetPercentage", "decisionMaking"],
  ["mainBarrier"],
];

export function isStepValid(form: AssessmentFormData, step: number): boolean {
  return STEP_REQUIRED[step].every((field) => {
    const value = form[field];
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === "number") return true;
    return value !== "" && value !== undefined && value !== null;
  });
}

export function buildAnswers(form: AssessmentFormData) {
  return {
    company_description: form.companyDescription,
    innovation_process: form.innovationProcess,
    past_initiatives: form.pastInitiatives,
    customer_feedback: form.customerFeedback,
    strategic_goals: form.strategicGoals,
    time_horizon: form.timeHorizon,
    team_size: form.teamSize,
    digital_maturity: form.digitalMaturity,
    budgetPercentage: form.budgetPercentage,
    revenueRange: form.revenueRange,
    decision_making: form.decisionMaking,
    regulatoryEnvironment: form.regulatoryEnvironment,
    riskAppetite: form.riskAppetite,
    strategicPriority: form.strategicPriority,
    competitivePressure: form.competitivePressure,
    main_barrier: form.mainBarrier,
    additional_context: form.additionalContext,
  };
}

interface StoredAnswers {
  regulatoryEnvironment?: string;
  innovation_process?: string;
  past_initiatives?: string;
  customer_feedback?: string;
  strategic_goals?: string;
  time_horizon?: string;
  riskAppetite?: string;
  strategicPriority?: string;
  team_size?: string;
  digital_maturity?: string;
  budgetPercentage?: number;
  revenueRange?: string;
  decision_making?: string;
  main_barrier?: string[];
  competitivePressure?: string;
  additional_context?: string;
  company_description?: string;
}

// Rehydrate a form from a prior insight's stored answers (snake_case JSON).
export function assessmentFromPrevious(prev: {
  companyName?: string;
  sector?: string;
  size?: string;
  previousAnswers?: string;
}): AssessmentFormData {
  let prevAnswers: StoredAnswers = {};
  try {
    prevAnswers = JSON.parse(prev.previousAnswers || "{}") as StoredAnswers;
  } catch {
    // ignore malformed stored JSON
  }
  return {
    companyName: prev.companyName || "",
    sector: prev.sector || "",
    size: prev.size || "",
    regulatoryEnvironment: prevAnswers.regulatoryEnvironment || "",
    innovationProcess: prevAnswers.innovation_process || "",
    pastInitiatives: prevAnswers.past_initiatives || "",
    strategicGoals: prevAnswers.strategic_goals || "",
    timeHorizon: prevAnswers.time_horizon || "",
    riskAppetite: prevAnswers.riskAppetite || "",
    strategicPriority: prevAnswers.strategicPriority || "",
    teamSize: prevAnswers.team_size || "",
    digitalMaturity: prevAnswers.digital_maturity || "",
    budgetPercentage: prevAnswers.budgetPercentage ?? 5,
    revenueRange: prevAnswers.revenueRange || "",
    decisionMaking: prevAnswers.decision_making || "",
    mainBarrier: prevAnswers.main_barrier || [],
    competitivePressure: prevAnswers.competitivePressure || "",
    additionalContext: prevAnswers.additional_context || "",
    companyDescription: prevAnswers.company_description || "",
    customerFeedback: prevAnswers.customer_feedback || "",
  } as AssessmentFormData;
}
