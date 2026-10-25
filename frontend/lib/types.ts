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
  riskAppetite: RiskAppetite;
  strategicPriority: StrategicPriority;

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

export type ChatTag =
  | { kind: "opportunity"; id: string; label: string }
  | { kind: "nextStep"; id: string; label: string }
  | { kind: "weakness"; id: string; label: string };

export type ReportSection = {
  kind: "opportunity" | "nextStep" | "weakness";
  id: string;
  label: string;
};

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

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface CompanySummary {
  id: number;
  name: string;
  sector: string;
  size: string;
  latestScore: number | null;
  latestInsightId: number | null;
  assessmentCount: number;
  createdAt: string;
}

export interface ExecutionPlan {
  firstActions: string[];
  resourcesNeeded: string[];
  successMetric: string;
  milestones: string[];
}

export interface Opportunity {
  id: string;
  type: string;
  title: string;
  rationale: string;
  executionPlan?: ExecutionPlan | null;
  impact: string;
  difficulty: string;
  timeframe: string;
  carryForwardFrom?: string | null;
  carryForwardStatus?: string | null;
}

export interface NextStep {
  id: string;
  action: string;
  owner: string;
  timeframe: string;
}

export interface ProgressReport {
  improvements: string[];
  persistentGaps: string[];
  achievedMilestones: string[];
}

export interface ComparisonToPrevious {
  previousScore: number | null;
  previousDate: string | null;
  assessmentNumber: number | null;
  keyChanges: string | null;
}

export interface Insight {
  id: number;
  aiOutput: string;
  innovationScore: number | null;
  scoreDelta: number | null;
  opportunities: Opportunity[];
  nextSteps: NextStep[];
  keyWeaknesses: string[];
  progress?: ProgressReport | null;
  comparisonToPrevious?: ComparisonToPrevious | null;
  previousInsightId?: number | null;
  assessmentNumber: number;
  companyName: string;
  sector: string;
  size: string;
  previousAnswers: string;
  modelName: string;
  responseId?: number | null;
  isSelected: boolean;
  variants?: Insight[];
}

export interface AssessmentTimeline {
  id: number;
  assessmentNumber: number;
  periodLabel: string;
  innovationScore: number | null;
  scoreDelta: number | null;
  generatedAt: string;
}

export interface CompanyDetail {
  id: number;
  name: string;
  sector: string;
  size: string;
  latestScore: number | null;
  scoreTrend: string;
  delta: number;
  assessmentCount: number;
  createdAt: string;
  assessments: AssessmentTimeline[];
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  taggedOpportunityId?: string | null;
  taggedNextStepId?: string | null;
  taggedWeakness?: string | null;
  createdAt: string;
}

export interface ChatSession {
  id: number;
  messages: ChatMessage[];
  createdAt: string;
}

export interface MyCompaniesQueryResult {
  myCompanies: CompanySummary[];
}

export interface GetInsightQueryResult {
  getInsight: Insight | null;
}

export interface CompanyDetailQueryResult {
  company: CompanyDetail | null;
}

export interface ChatSessionQueryResult {
  chatSession: ChatSession | null;
}