import { gql } from "@apollo/client";

export const SELECT_INSIGHT = gql`
  mutation SelectInsight($insightId: Int!) {
    selectInsight(insightId: $insightId) {
      id
      modelName
      isSelected
    }
  }
`;

export const SUBMIT_QUESTIONNAIRE = gql`
  mutation SubmitQuestionnaire(
    $companyName: String!
    $sector: String!
    $size: String!
    $answers: JSON!
    $companyId: Int
    $periodLabel: String
  ) {
    submitQuestionnaire(
      companyName: $companyName
      sector: $sector
      size: $size
      answers: $answers
      companyId: $companyId
      periodLabel: $periodLabel
    ) {
      id
      innovationScore
      scoreDelta
      assessmentNumber
      previousInsightId
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
    }
  }
`;

export const SUBMIT_REASSESSMENT = gql`
  mutation SubmitReassessment(
    $companyId: Int!
    $companyName: String!
    $sector: String!
    $size: String!
    $answers: JSON!
    $previousInsightId: Int!
    $recommendationStatus: JSON
    $changesSinceLast: String
    $periodLabel: String
  ) {
    submitReassessment(
      companyId: $companyId
      companyName: $companyName
      sector: $sector
      size: $size
      answers: $answers
      previousInsightId: $previousInsightId
      recommendationStatus: $recommendationStatus
      changesSinceLast: $changesSinceLast
      periodLabel: $periodLabel
    ) {
      id
      innovationScore
      scoreDelta
      assessmentNumber
      previousInsightId
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
    }
  }
`;
