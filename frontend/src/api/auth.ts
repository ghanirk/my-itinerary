import { apiFetch } from "./client";
import type { Token, UserLoginRequest, UserRegisterRequest } from "../types/auth";

export async function registerUser(payload: UserRegisterRequest): Promise<Token> {
  return apiFetch<Token>("/auth/register", {
    method: "POST",
    body: payload,
    auth: false,
  });
}

export async function loginUser(payload: UserLoginRequest): Promise<Token> {
  return apiFetch<Token>("/auth/login", {
    method: "POST",
    body: payload,
    auth: false,
  });
}
