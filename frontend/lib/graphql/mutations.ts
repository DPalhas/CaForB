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
        impact
        difficulty
        timeframe
      }
      nextSteps
      keyWeaknesses
    }
  }
`;