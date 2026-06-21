export type CompanySize = "SME" | "Mid" | "Large";

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

  // Section 5 — Pain Points
  mainBarrier: string;
  additionalContext: string;
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
  mainBarrier: "",
  additionalContext: "",
};