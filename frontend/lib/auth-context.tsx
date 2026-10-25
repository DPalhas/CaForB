"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { useMutation, useLazyQuery } from "@apollo/client/react";
import { LOGIN, REGISTER, LOGOUT, ME } from "@/lib/graphql/auth";
import type { User } from "@/lib/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const [fetchMe] = useLazyQuery<{ me: User | null }>(ME);
  const [loginMutation] = useMutation<
    { login: User },
    { username: string; password: string }
  >(LOGIN);
  const [registerMutation] = useMutation<
    { register: User },
    { username: string; email: string; password: string }
  >(REGISTER);
  const [logoutMutation] = useMutation<{ logout: boolean }>(LOGOUT);

  useEffect(() => {
    fetchMe()
      .then(({ data }) => {
        if (data?.me) {
          setUser(data.me);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [fetchMe]);

  useEffect(() => {
    const handleSessionExpired = () => {
      setUser(null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    };
    window.addEventListener("auth:session-expired", handleSessionExpired);
    return () =>
      window.removeEventListener("auth:session-expired", handleSessionExpired);
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      const { data } = await loginMutation({ variables: { username, password } });
      setUser(data?.login ?? null);
    },
    [loginMutation]
  );

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      const { data } = await registerMutation({
        variables: { username, email, password },
      });
      setUser(data?.register ?? null);
    },
    [registerMutation]
  );

  const logout = useCallback(async () => {
    await logoutMutation();
    setUser(null);
  }, [logoutMutation]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
