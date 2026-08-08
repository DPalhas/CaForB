import { ApolloClient, InMemoryCache, HttpLink, from } from "@apollo/client";
import { onError } from "@apollo/client/link/error";
import { CombinedGraphQLErrors } from "@apollo/client/errors";

const errorLink = onError(({ error }) => {
  if (CombinedGraphQLErrors.is(error)) {
    for (const err of error.errors) {
      if (err.message === "Authentication required") {
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("auth:session-expired"));
        }
      }
    }
  }
});

const httpLink = new HttpLink({
  uri: "http://localhost:8000/graphql/",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
  },
});

const client = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: new InMemoryCache(),
});

export default client;