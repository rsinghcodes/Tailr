"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";
import { API_BASE } from "@/lib/api";
import { Loader2, AlertCircle, Sparkles } from "lucide-react";

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
      const body =
        mode === "login"
          ? { email, password }
          : { email, password, full_name: fullName };

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || "Request failed");

      setAuth(data.access_token, data.user);
      router.push("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{
        background:
          "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(79,70,229,0.06) 0%, transparent 60%)",
      }}
    >
      <div className="w-full max-w-sm space-y-8">
        {/* Hero lockup */}
        <div className="text-center space-y-4">
          <div
            className="w-16 h-16 rounded-3xl mx-auto flex items-center justify-center font-bold text-2xl shadow-md"
            style={{
              background: "linear-gradient(135deg, var(--md-primary) 0%, #6366f1 100%)",
              color: "#ffffff",
            }}
          >
            T
          </div>
          <div>
            <h1
              className="text-3xl font-bold tracking-tight"
              style={{ color: "var(--md-on-bg)", letterSpacing: "-0.03em" }}
            >
              Tailr
            </h1>
            <p className="text-base mt-1" style={{ color: "var(--md-on-surface-v)" }}>
              AI-Powered Resume Intelligence
            </p>
          </div>
        </div>

        {/* Card */}
        <div
          className="rounded-3xl p-8 space-y-6 border shadow-sm"
          style={{
            background: "var(--md-surface)",
            borderColor: "var(--md-outline)",
          }}
        >
          {/* Mode toggle */}
          <div
            className="flex rounded-2xl overflow-hidden p-1 gap-1"
            style={{ background: "var(--md-surface-c3)" }}
          >
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(null); }}
                className="flex-1 py-2.5 text-sm font-semibold rounded-xl transition-all duration-200"
                style={
                  mode === m
                    ? {
                        background: "var(--md-primary-c)",
                        color: "var(--md-on-primary-c)",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.25)",
                      }
                    : { color: "var(--md-on-surface-v)" }
                }
              >
                {m === "login" ? "Sign In" : "Register"}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "register" && (
              <div className="space-y-1.5">
                <label className="text-sm font-medium" style={{ color: "var(--md-on-surface-v)" }}>
                  Full Name
                </label>
                <input
                  type="text"
                  placeholder="Jane Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  className="input"
                />
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-sm font-medium" style={{ color: "var(--md-on-surface-v)" }}>
                Email
              </label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium" style={{ color: "var(--md-on-surface-v)" }}>
                Password
              </label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="input"
              />
            </div>

            {error && (
              <div
                className="flex items-start gap-3 p-4 rounded-2xl text-sm"
                style={{
                  background: "rgba(255,180,171,0.08)",
                  border: "1px solid rgba(255,180,171,0.25)",
                  color: "var(--md-error)",
                }}
              >
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {mode === "login" ? "Signing in…" : "Creating account…"}
                </>
              ) : mode === "login" ? (
                "Sign In"
              ) : (
                "Create Account"
              )}
            </button>
          </form>
        </div>

        {/* Footer hint */}
        <p className="text-center text-sm" style={{ color: "var(--md-on-surface-d)" }}>
          FastAPI · Next.js · LangGraph · LlamaIndex
        </p>
      </div>
    </div>
  );
}
