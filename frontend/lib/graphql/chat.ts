import { gql } from "@apollo/client";

export const ASK_INSIGHT = gql`
  mutation AskInsight(
    $insightId: Int!
    $message: String!
    $taggedOpportunityId: String
    $taggedNextStepId: String
    $taggedWeakness: String
    $sessionId: Int
  ) {
    askInsight(
      insightId: $insightId
      message: $message
      taggedOpportunityId: $taggedOpportunityId
      taggedNextStepId: $taggedNextStepId
      taggedWeakness: $taggedWeakness
      sessionId: $sessionId
    ) {
      id
      role
      content
      taggedOpportunityId
      taggedNextStepId
      taggedWeakness
      createdAt
    }
  }
`;

export const CHAT_SESSION = gql`
  query ChatSession($insightId: Int!) {
    chatSession(insightId: $insightId) {
      id
      createdAt
      messages {
        id
        role
        content
        taggedOpportunityId
        taggedNextStepId
        taggedWeakness
        createdAt
      }
    }
  }
`;
