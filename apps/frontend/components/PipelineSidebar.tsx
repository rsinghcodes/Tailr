"use client";

import { Check, Loader2, Workflow, type LucideIcon } from "lucide-react";
import { useUIStore } from "@/lib/store";
import { FLOW_STEPS } from "@/lib/flow";

export function PipelineSidebar() {
  const { flowStep } = useUIStore();
  const currentIdx = FLOW_STEPS.findIndex((s) => s.id === flowStep);

  const phase =
    flowStep === "optimizing"
      ? { label: "RUNNING", className: "text-[var(--accent)]" }
      : flowStep === "done"
      ? { label: "COMPLETED", className: "text-emerald-400" }
      : { label: "IDLE", className: "text-[var(--text-muted)]" };

  return (
    <div className="card-3d p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
          <Workflow className="w-4 h-4 text-[var(--accent)]" /> Workflow
        </div>
        <span className={`text-[10px] font-mono font-semibold ${phase.className}`}>
          {phase.label}
        </span>
      </div>

      <div>
        {FLOW_STEPS.map((step, idx) => {
          const isDone = idx < currentIdx;
          const isActive = idx === currentIdx;
          const Icon: LucideIcon = step.icon;
          return (
            <div key={step.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div
                  className={`flex items-center justify-center w-7 h-7 rounded-full border transition-all ${
                    isDone
                      ? "border-emerald-700/50 bg-emerald-900/30 text-emerald-400"
                      : isActive
                      ? "border-[var(--accent)]/60 bg-[var(--accent)]/10 text-[var(--accent)]"
                      : "border-[var(--border-subtle)] text-[var(--text-muted)]"
                  }`}
                >
                  {isActive && flowStep === "optimizing" ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : isDone ? (
                    <Check className="w-3.5 h-3.5" />
                  ) : (
                    <Icon className="w-3.5 h-3.5" />
                  )}
                </div>
                {idx < FLOW_STEPS.length - 1 && (
                  <div
                    className={`w-px flex-1 min-h-3 ${
                      isDone ? "bg-emerald-800/40" : "bg-[var(--border-subtle)]"
                    }`}
                  />
                )}
              </div>
              <div className={`min-w-0 flex-1 ${idx < FLOW_STEPS.length - 1 ? "pb-3.5" : ""}`}>
                <div
                  className={`text-xs font-medium leading-tight ${
                    isDone
                      ? "text-emerald-300"
                      : isActive
                      ? "text-[var(--text-primary)]"
                      : "text-[var(--text-muted)]"
                  }`}
                >
                  {step.label}
                </div>
                <div className="text-[10px] font-mono text-[var(--text-muted)] mt-0.5 leading-snug">
                  {isActive
                    ? flowStep === "optimizing"
                      ? "running…"
                      : step.description
                    : step.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="border-t border-[var(--border-subtle)] pt-3">
        <div className="flex items-center justify-between text-[11px] mb-1.5">
          <span className="text-[var(--text-secondary)]">Progress</span>
          <span className="font-mono text-[var(--text-primary)]">
            {Math.max(0, currentIdx)}/{FLOW_STEPS.length}
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-[var(--bg-elevated)] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${(Math.max(0, currentIdx) / FLOW_STEPS.length) * 100}%`,
              background: "var(--accent)",
            }}
          />
        </div>
      </div>
    </div>
  );
}
