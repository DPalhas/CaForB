import { gql } from "@apollo/client";

export const GET_INSIGHT = gql`
  query GetInsight($id: Int!) {
    getInsight(id: $id) {
      id
      innovationScore
      scoreDelta
      assessmentNumber
      previousInsightId
      companyName
      sector
      size
      previousAnswers
      opportunities {
        id
        type
        title
        rationale
        executionPlan {
          firstActions
          resourcesNeeded
          successMetric
          milestones
        }
        impact
        difficulty
        timeframe
        carryForwardFrom
        carryForwardStatus
      }
      nextSteps {
        id
        action
        owner
        timeframe
      }
      keyWeaknesses
      progress {
        improvements
        persistentGaps
        achievedMilestones
      }
      comparisonToPrevious {
        previousScore
        previousDate
        assessmentNumber
        keyChanges
      }
      aiOutput
    }
  }
`;

export const MY_INSIGHTS = gql`
  query MyInsights {
    myInsights {
      id
      companyName
      sector
      innovationScore
      submittedAt
    }
  }
`;

export const MY_COMPANIES = gql`
  query MyCompanies {
    myCompanies {
      id
      name
      sector
      size
      latestScore
      latestInsightId
      assessmentCount
      createdAt
    }
  }
`;

export const COMPANY_DETAIL = gql`
  query CompanyDetail($id: Int!) {
    company(id: $id) {
      id
      name
      sector
      size
      latestScore
      scoreTrend
      delta
      assessmentCount
      createdAt
      assessments {
        id
        assessmentNumber
        periodLabel
        innovationScore
        scoreDelta
        generatedAt
      }
    }
  }
`;
