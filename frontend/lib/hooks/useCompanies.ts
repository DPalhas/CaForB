"use client";

import { useMemo } from "react";
import { useQuery } from "@apollo/client/react";
import { MY_COMPANIES } from "@/lib/graphql/queries";
import type { MyCompaniesQueryResult, CompanySummary } from "@/lib/types";

export function useCompanies(skip = false) {
  const { data, loading, error, refetch } = useQuery<MyCompaniesQueryResult>(
    MY_COMPANIES,
    { skip }
  );
  const companies = useMemo<CompanySummary[]>(
    () => data?.myCompanies ?? [],
    [data]
  );
  return { companies, loading, error, refetch };
}
