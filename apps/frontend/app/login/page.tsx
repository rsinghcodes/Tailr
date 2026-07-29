"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";
import { Loader2, AlertCircle, Cpu } from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1";

export default function LoginPage() {
  const router = useRouter();
  const { setAuth, isAuthenticated } = useAuthStore();

  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    useAuthStore.getState().hydrate();
    if (useAuthStore.getState().isAuthenticated) {
      router.push("/");
    }
  }, [router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/signup";
      const body = mode === "login"
        ? { email, password }
        : { email, password, full_name: fullName };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || data.message || "Request failed");
      }

      setAuth(data.access_token, data.user);
      router.push("/");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-100">
      <div className="w-full max-w-sm space-y-6 p-8">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-md bg-zinc-100 text-zinc-950 font-bold text-sm mx-auto mb-2">
            T
          </div>
          <h1 className="text-xl font-semibold">Tailr</h1>
          <p className="text-xs text-zinc-400">AI-Powered Resume Optimization</p>
        </div>

        <div className="min-panel p-6 space-y-4">
          <div className="flex border border-zinc-800 rounded-md overflow-hidden text-xs font-medium">
            <button
              onClick={() => { setMode("login"); setError(null); }}
              className={`flex-1 py-2 text-center transition-colors ${
                mode === "login" ? "bg-zinc-800 text-zinc-100" : "bg-zinc-900 text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setMode("register"); setError(null); }}
              className={`flex-1 py-2 text-center transition-colors ${
                mode === "register" ? "bg-zinc-800 text-zinc-100" : "bg-zinc-900 text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === "register" && (
              <input
                type="text"
                placeholder="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="min-input w-full"
              />
            )}
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="min-input w-full"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="min-input w-full"
            />

            {error && (
              <div className="flex items-center gap-2 p-2.5 rounded bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="min-button min-button-primary w-full justify-center disabled:opacity-50"
            >
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> {mode === "login" ? "Signing in..." : "Creating account..."}</>
              ) : (
                mode === "login" ? "Sign In" : "Create Account"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
