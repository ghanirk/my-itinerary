import { createContext } from "react";
import type { Token, UserOut } from "../types/auth";

export interface AuthContextValue {
  user: UserOut | null;
  isAuthenticated: boolean;
  login: (token: Token) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
