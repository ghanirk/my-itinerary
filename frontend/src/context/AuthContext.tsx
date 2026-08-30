import { useMemo, useState, type ReactNode } from "react";
import type { Token, UserOut } from "../types/auth";
import { clearToken, getStoredUser, getToken, setStoredUser, setToken } from "../lib/authStorage";
import { AuthContext, type AuthContextValue } from "./auth-context";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(() => getStoredUser<UserOut>());

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user && getToken()),
      login: (token: Token) => {
        setToken(token.access_token);
        setStoredUser(token.user);
        setUser(token.user);
      },
      logout: () => {
        clearToken();
        setUser(null);
      },
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
