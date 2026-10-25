"use client";

import { useQuery } from "@apollo/client/react";
import type { WatchQueryFetchPolicy } from "@apollo/client";
import { GET_INSIGHT } from "@/lib/graphql/queries";
import type { GetInsightQueryResult } from "@/lib/types";

export function useInsight(
  id: number | null,
  fetchPolicy: WatchQueryFetchPolicy = "cache-first"
) {
  const { data, loading, error, refetch } = useQuery<GetInsightQueryResult>(
    GET_INSIGHT,
    {
      variables: { id: id! },
      skip: id === null,
      fetchPolicy,
    }
  );
  return { insight: data?.getInsight ?? null, loading, error, refetch };
}
