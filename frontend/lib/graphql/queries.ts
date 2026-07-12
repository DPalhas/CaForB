import { gql } from "@apollo/client";

export const GET_INSIGHT = gql`
  query GetInsight($id: Int!) {
    getInsight(id: $id) {
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