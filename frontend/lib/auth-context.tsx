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

interface User {
  id: number;
  username: string;
  email: string;
}

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

  const [fetchMe] = useLazyQuery(ME);
  const [loginMutation] = useMutation(LOGIN);
  const [registerMutation] = useMutation(REGISTER);
  const [logoutMutation] = useMutation(LOGOUT);

  useEffect(() => {
    fetchMe()
      .then(({ data }) => {
        const result = data as { me?: User } | null;
        if (result?.me) {
          setUser(result.me);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

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
      setUser((data as any).login);
    },
    [loginMutation]
  );

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      const { data } = await registerMutation({
        variables: { username, email, password },
      });
      setUser((data as any).register);
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
