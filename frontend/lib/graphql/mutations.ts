import { gql } from "@apollo/client";

export const SUBMIT_QUESTIONNAIRE = gql`
  mutation SubmitQuestionnaire(
    $companyName: String!
    $sector: String!
    $size: String!
    $answers: JSON!
  ) {
    submitQuestionnaire(
      companyName: $companyName
      sector: $sector
      size: $size
      answers: $answers
    ) {
      id
      innovationScore
      opportunities {
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
      }
      nextSteps {
        action
        owner
        timeframe
      }
      keyWeaknesses
    }
  }
`;