export type CompanySize = "Micro" | "Small" | "Medium" | "Large";

export type RevenueRange =
  | "under_1m"
  | "1m_to_10m"
  | "10m_to_50m"
  | "over_50m"
  | "";

export interface AssessmentFormData {
  // Section 1 — Company Profile
  companyName: string;
  sector: string;
  size: CompanySize | "";

  // Section 2 — Innovation State
  innovationProcess: string;
  pastInitiatives: string;

  // Section 3 — Strategic Goals
  strategicGoals: string;
  timeHorizon: string;

  // Section 4 — Internal Capabilities
  teamSize: string;
  digitalMaturity: string;
  budgetPercentage: number;     // 0-100, replaces budgetAllocation dropdown
  revenueRange: RevenueRange;   // NEW — absolute revenue bracket
  decisionMaking: string;

  // Section 5 — Pain Points
  mainBarrier: string[];
  additionalContext: string;

  companyDescription: string;
  customerFeedback: string;
}

export const EMPTY_FORM: AssessmentFormData = {
  companyName: "",
  sector: "",
  size: "",
  innovationProcess: "",
  pastInitiatives: "",
  strategicGoals: "",
  timeHorizon: "",
  teamSize: "",
  digitalMaturity: "",
  budgetPercentage: 5,
  revenueRange: "",
  decisionMaking: "",
  mainBarrier: [],
  additionalContext: "",
  companyDescription: "",
  customerFeedback: "",
};