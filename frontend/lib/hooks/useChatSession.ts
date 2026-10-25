"use client";

import { useQuery } from "@apollo/client/react";
import { CHAT_SESSION } from "@/lib/graphql/chat";
import type { ChatSessionQueryResult } from "@/lib/types";

export function useChatSession(insightId: number, open: boolean) {
  const { data, refetch } = useQuery<ChatSessionQueryResult>(CHAT_SESSION, {
    variables: { insightId },
    skip: !open,
    fetchPolicy: "network-only",
  });
  return { session: data?.chatSession ?? null, refetch };
}
