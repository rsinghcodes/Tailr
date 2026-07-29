"use client";

import { create } from "zustand";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: AuthUser) => void;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  setAuth: (token, user) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("tailr_token", token);
      localStorage.setItem("tailr_user", JSON.stringify(user));
    }
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("tailr_token");
      localStorage.removeItem("tailr_user");
    }
    set({ token: null, user: null, isAuthenticated: false });
  },

  hydrate: () => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("tailr_token");
      const userStr = localStorage.getItem("tailr_user");
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr) as AuthUser;
          set({ token, user, isAuthenticated: true });
        } catch {
          localStorage.removeItem("tailr_token");
          localStorage.removeItem("tailr_user");
        }
      }
    }
  },
}));
