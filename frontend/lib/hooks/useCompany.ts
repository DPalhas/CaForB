"use client";

import { useQuery } from "@apollo/client/react";
import { COMPANY_DETAIL } from "@/lib/graphql/queries";
import type { CompanyDetailQueryResult } from "@/lib/types";

export function useCompany(id: number) {
  const { data, loading, error } = useQuery<CompanyDetailQueryResult>(
    COMPANY_DETAIL,
    {
      variables: { id },
      skip: isNaN(id),
    }
  );
  return { company: data?.company ?? null, loading, error };
}
