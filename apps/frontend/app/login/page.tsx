"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";
import { API_BASE } from "@/lib/api";
import { Loader2, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();

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
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-sm space-y-6 p-8">
        <div className="text-center space-y-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center font-bold text-white text-sm mx-auto shadow-lg shadow-indigo-500/20">
            T
          </div>
          <h1 className="text-lg font-semibold text-zinc-100">Tailr</h1>
          <p className="text-xs text-zinc-500">AI-Powered Resume Optimization</p>
        </div>

        <div className="card-3d p-6 space-y-4">
          <div className="flex rounded-lg overflow-hidden text-xs font-medium border border-[var(--border-subtle)]">
            <button
              onClick={() => { setMode("login"); setError(null); }}
              className={`flex-1 py-2 text-center transition-all ${
                mode === "login" ? "bg-[var(--accent)] text-white" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setMode("register"); setError(null); }}
              className={`flex-1 py-2 text-center transition-all ${
                mode === "register" ? "bg-[var(--accent)] text-white" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
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
                className="input"
              />
            )}
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="input"
            />

            {error && (
              <div className="flex items-center gap-2 p-2.5 rounded-lg bg-rose-950/30 border border-rose-900/50 text-rose-400 text-xs">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full"
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
