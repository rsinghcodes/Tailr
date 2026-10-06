"use client";

import type { ReactNode } from "react";
import { Gauge, Clock, Sparkles, TriangleAlert, Target } from "lucide-react";
import { useUIStore } from "@/lib/store";

function formatMs(ms?: number): string {
  if (ms == null) return "";
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${Math.round(ms)}ms`;
}

function ScoreRing({ score }: { score: number | null }) {
  const pct = score == null ? 0 : Math.max(0, Math.min(100, score));
  const r = 34;
  const c = 2 * Math.PI * r;
  const color =
    score == null
      ? "var(--md-outline)"
      : pct >= 75
      ? "var(--md-tertiary)"
      : pct >= 50
      ? "var(--amber)"
      : "var(--md-error)";

  const glowColor =
    score == null
      ? "transparent"
      : pct >= 75
      ? "rgba(5,150,105,0.25)"
      : pct >= 50
      ? "rgba(217,119,6,0.25)"
      : "rgba(220,38,38,0.25)";

  return (
    <svg width="84" height="84" viewBox="0 0 84 84" className="shrink-0">
      {/* Track */}
      <circle cx="42" cy="42" r={r} fill="none" stroke="var(--md-surface-c3)" strokeWidth="7" />
      {/* Progress */}
      <circle
        cx="42"
        cy="42"
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="7"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={c * (1 - pct / 100)}
        transform="rotate(-90 42 42)"
        style={{ filter: pct > 0 ? `drop-shadow(0 0 6px ${glowColor})` : undefined }}
      />
    </svg>
  );
}

export function ResultsDashboard({ children }: { children: ReactNode }) {
  const { activeWorkflowResponse, streamSteps } = useUIStore();

  const ats = activeWorkflowResponse?.ats_report;
  const score = typeof ats?.score === "number" ? (ats.score as number) : null;
  const coverage =
    typeof ats?.keyword_coverage === "number" ? (ats.keyword_coverage as number) : null;
  const strengths = Array.isArray(ats?.strengths) ? (ats.strengths as string[]) : [];
  const weaknesses = Array.isArray(ats?.weaknesses) ? (ats.weaknesses as string[]) : [];
  const missing = Array.isArray(ats?.missing_keywords) ? (ats.missing_keywords as string[]) : [];

  const measured = streamSteps.filter((s) => s.duration_ms != null);
  const maxMs = Math.max(1, ...measured.map((s) => s.duration_ms ?? 0));

  const scoreColor =
    score == null
      ? "var(--md-on-bg)"
      : score >= 75
      ? "var(--md-tertiary)"
      : score >= 50
      ? "var(--amber)"
      : "var(--md-error)";

  return (
    <div className="space-y-5">
      {/* Top metrics row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* ATS Score card */}
        <div
          className="rounded-2xl p-5 border"
          style={{ background: "var(--md-surface)", borderColor: "var(--md-outline)" }}
        >
          <div className="section-label mb-4 flex items-center gap-2">
            <Gauge className="w-3.5 h-3.5" style={{ color: "var(--md-primary)" }} />
            ATS Score
          </div>

          <div className="flex items-center gap-5">
            <ScoreRing score={score} />
            <div>
              <div
                className="text-5xl font-bold font-mono leading-none"
                style={{ color: scoreColor, letterSpacing: "-0.03em" }}
              >
                {score ?? "—"}
              </div>
              <div className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>
                out of 100
              </div>
            </div>
          </div>

          {coverage != null && (
            <div className="mt-5 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span style={{ color: "var(--md-on-surface-v)" }}>Keyword coverage</span>
                <span className="font-bold font-mono" style={{ color: "var(--md-on-bg)" }}>
                  {Math.round(coverage * 100)}%
                </span>
              </div>
              <div
                className="h-2 rounded-full overflow-hidden"
                style={{ background: "var(--md-surface-c1)" }}
              >
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${coverage * 100}%`,
                    background: "var(--md-primary)",
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Pipeline Timing */}
        <div
          className="md:col-span-2 rounded-2xl p-5 border"
          style={{ background: "var(--md-surface)", borderColor: "var(--md-outline)" }}
        >
          <div className="section-label mb-4 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" style={{ color: "var(--md-primary)" }} />
            Pipeline Timing
          </div>
          <div className="space-y-3">
            {streamSteps.map((s) => (
              <div key={s.step} className="flex items-center gap-3">
                <span
                  className="w-36 shrink-0 text-sm font-medium truncate"
                  style={{ color: "var(--md-on-surface-v)" }}
                >
                  {s.label}
                </span>
                <div
                  className="flex-1 h-2 rounded-full overflow-hidden"
                  style={{ background: "var(--md-surface-c3)" }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${((s.duration_ms ?? 0) / maxMs) * 100}%`,
                      background: s.duration_ms != null
                        ? "var(--md-tertiary)"
                        : "var(--md-outline)",
                      boxShadow: s.duration_ms != null
                        ? "0 0 8px rgba(160,216,212,0.4)"
                        : undefined,
                    }}
                  />
                </div>
                <span
                  className="w-14 shrink-0 text-right text-sm font-mono"
                  style={{ color: "var(--md-on-surface-d)" }}
                >
                  {s.duration_ms != null ? formatMs(s.duration_ms) : "—"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Insights row */}
      {(strengths.length > 0 || weaknesses.length > 0 || missing.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {strengths.length > 0 && (
            <div
              className="rounded-2xl p-5 border"
              style={{ background: "var(--md-surface)", borderColor: "rgba(5,150,105,0.25)" }}
            >
              <div className="section-label mb-3 flex items-center gap-2" style={{ color: "var(--md-tertiary)" }}>
                <Sparkles className="w-3.5 h-3.5" /> Strengths
              </div>
              <ul className="space-y-2">
                {strengths.slice(0, 4).map((s, i) => (
                  <li key={i} className="text-sm leading-snug" style={{ color: "var(--md-on-surface-v)" }}>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {weaknesses.length > 0 && (
            <div
              className="rounded-2xl p-5 border"
              style={{ background: "var(--md-surface)", borderColor: "rgba(217,119,6,0.25)" }}
            >
              <div className="section-label mb-3 flex items-center gap-2" style={{ color: "var(--amber)" }}>
                <TriangleAlert className="w-3.5 h-3.5" /> Weaknesses
              </div>
              <ul className="space-y-2">
                {weaknesses.slice(0, 4).map((w, i) => (
                  <li key={i} className="text-sm leading-snug" style={{ color: "var(--md-on-surface-v)" }}>
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {missing.length > 0 && (
            <div
              className="rounded-2xl p-5 border"
              style={{ background: "var(--md-surface)", borderColor: "rgba(220,38,38,0.2)" }}
            >
              <div className="section-label mb-3 flex items-center gap-2" style={{ color: "var(--md-error)" }}>
                <Target className="w-3.5 h-3.5" /> Missing Keywords
              </div>
              <div className="flex flex-wrap gap-2">
                {missing.slice(0, 8).map((k, i) => (
                  <span
                    key={i}
                    className="px-3 py-1 rounded-full text-xs font-semibold"
                    style={{
                      background: "var(--md-error-c)",
                      border: "1px solid rgba(220,38,38,0.2)",
                      color: "var(--md-error)",
                    }}
                  >
                    {k}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Children (changes view) */}
      <div className="pt-2 border-t" style={{ borderColor: "var(--md-outline)" }}>
        {children}
      </div>
    </div>
  );
}
