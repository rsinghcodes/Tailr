"use client";

import type { ReactNode } from "react";
import { Gauge, Clock, Sparkles, TriangleAlert } from "lucide-react";
import { useUIStore } from "@/lib/store";

function formatMs(ms?: number): string {
  if (ms == null) return "";
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${Math.round(ms)}ms`;
}

function ScoreRing({ score }: { score: number | null }) {
  const pct = score == null ? 0 : Math.max(0, Math.min(100, score));
  const r = 26;
  const c = 2 * Math.PI * r;
  const color =
    score == null
      ? "var(--border-mid)"
      : pct >= 75
      ? "var(--green)"
      : pct >= 50
      ? "var(--amber)"
      : "var(--rose)";

  return (
    <svg width="64" height="64" viewBox="0 0 64 64" className="shrink-0">
      <circle cx="32" cy="32" r={r} fill="none" stroke="var(--bg-elevated)" strokeWidth="6" />
      <circle
        cx="32"
        cy="32"
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="6"
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={c * (1 - pct / 100)}
        transform="rotate(-90 32 32)"
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
  const missing = Array.isArray(ats?.missing_keywords)
    ? (ats.missing_keywords as string[])
    : [];

  const measured = streamSteps.filter((s) => s.duration_ms != null);
  const maxMs = Math.max(1, ...measured.map((s) => s.duration_ms ?? 0));

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div
          className="rounded-lg p-4 border border-[var(--border-subtle)]"
          style={{ background: "var(--bg-surface)" }}
        >
          <div className="section-label mb-3 flex items-center gap-1.5">
            <Gauge className="w-3 h-3" /> ATS Score
          </div>
          <div className="flex items-center gap-4">
            <ScoreRing score={score} />
            <div>
              <div className="text-3xl font-bold font-mono text-[var(--text-primary)]">
                {score ?? "—"}
              </div>
              <div className="text-[11px] text-[var(--text-muted)]">out of 100</div>
            </div>
          </div>
          {coverage != null && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-[11px] mb-1.5">
                <span className="text-[var(--text-secondary)]">Keyword coverage</span>
                <span className="font-mono text-[var(--text-primary)]">
                  {Math.round(coverage * 100)}%
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-[var(--bg-elevated)] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: `${coverage * 100}%`, background: "var(--accent)" }}
                />
              </div>
            </div>
          )}
        </div>

        <div
          className="md:col-span-2 rounded-lg p-4 border border-[var(--border-subtle)]"
          style={{ background: "var(--bg-surface)" }}
        >
          <div className="section-label mb-3 flex items-center gap-1.5">
            <Clock className="w-3 h-3" /> Pipeline Timing
          </div>
          <div className="space-y-2">
            {streamSteps.map((s) => (
              <div key={s.step} className="flex items-center gap-3">
                <span className="w-32 shrink-0 truncate text-[11px] text-[var(--text-secondary)]">
                  {s.label}
                </span>
                <div className="flex-1 h-1.5 rounded-full bg-[var(--bg-elevated)] overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${((s.duration_ms ?? 0) / maxMs) * 100}%`,
                      background:
                        s.duration_ms != null ? "var(--green)" : "var(--border-mid)",
                    }}
                  />
                </div>
                <span className="w-14 shrink-0 text-right font-mono text-[11px] text-[var(--text-muted)]">
                  {s.duration_ms != null ? formatMs(s.duration_ms) : "—"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {(strengths.length > 0 || weaknesses.length > 0 || missing.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {strengths.length > 0 && (
            <div
              className="rounded-lg p-4 border border-[var(--border-subtle)]"
              style={{ background: "var(--bg-surface)" }}
            >
              <div className="section-label mb-2 flex items-center gap-1.5 text-emerald-400">
                <Sparkles className="w-3 h-3" /> Strengths
              </div>
              <ul className="space-y-1">
                {strengths.slice(0, 4).map((s, i) => (
                  <li key={i} className="text-[11px] text-[var(--text-secondary)] leading-snug">
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {weaknesses.length > 0 && (
            <div
              className="rounded-lg p-4 border border-[var(--border-subtle)]"
              style={{ background: "var(--bg-surface)" }}
            >
              <div className="section-label mb-2 flex items-center gap-1.5 text-amber-400">
                <TriangleAlert className="w-3 h-3" /> Weaknesses
              </div>
              <ul className="space-y-1">
                {weaknesses.slice(0, 4).map((w, i) => (
                  <li key={i} className="text-[11px] text-[var(--text-secondary)] leading-snug">
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {missing.length > 0 && (
            <div
              className="rounded-lg p-4 border border-[var(--border-subtle)]"
              style={{ background: "var(--bg-surface)" }}
            >
              <div className="section-label mb-2">Missing Keywords</div>
              <div className="flex flex-wrap gap-1.5">
                {missing.slice(0, 8).map((k, i) => (
                  <span key={i} className="tag">{k}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="pt-1 border-t border-[var(--border-subtle)]">{children}</div>
    </div>
  );
}
