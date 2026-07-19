export type CompanySize = "Micro" | "Small" | "Medium" | "Large";

export type RevenueRange =
  | "under_1m"
  | "1m_to_10m"
  | "10m_to_50m"
  | "over_50m"
  | "";

export type RiskLevel = "low" | "medium" | "high" | "";

export type RiskAppetite = "conservative" | "balanced" | "bold" | "";

export type StrategicPriority =
  | "growth"
  | "efficiency"
  | "market_defense"
  | "diversification"
  | "";

export interface AssessmentFormData {
  // Section 1 — Company Profile
  companyName: string;
  sector: string;
  size: CompanySize | "";
  regulatoryEnvironment: RiskLevel;

  // Section 2 — Innovation State
  innovationProcess: string;
  pastInitiatives: string;

  // Section 3 — Strategic Goals
  strategicGoals: string;
  timeHorizon: string;
  riskAppetite: RiskAppetite;               // NEW
  strategicPriority: StrategicPriority;     // NEW

  // Section 4 — Internal Capabilities
  teamSize: string;
  digitalMaturity: string;
  budgetPercentage: number;
  revenueRange: RevenueRange;
  decisionMaking: string;

  // Section 5 — Pain Points
  mainBarrier: string[];
  competitivePressure: RiskLevel;
  additionalContext: string;

  companyDescription: string;
  customerFeedback: string;
}

export const EMPTY_FORM: AssessmentFormData = {
  companyName: "",
  sector: "",
  size: "",
  regulatoryEnvironment: "",
  innovationProcess: "",
  pastInitiatives: "",
  strategicGoals: "",
  timeHorizon: "",
  riskAppetite: "",
  strategicPriority: "",
  teamSize: "",
  digitalMaturity: "",
  budgetPercentage: 5,
  revenueRange: "",
  decisionMaking: "",
  mainBarrier: [],
  competitivePressure: "",
  additionalContext: "",
  companyDescription: "",
  customerFeedback: "",
};