"use client";

import { Check, Loader2, Workflow, type LucideIcon } from "lucide-react";
import { useUIStore } from "@/lib/store";
import { FLOW_STEPS } from "@/lib/flow";

export function PipelineSidebar() {
  const { flowStep } = useUIStore();
  const currentIdx = FLOW_STEPS.findIndex((s) => s.id === flowStep);

  const phase =
    flowStep === "optimizing"
      ? { label: "RUNNING", color: "var(--md-primary)" }
      : flowStep === "done"
      ? { label: "DONE", color: "var(--md-tertiary)" }
      : { label: "IDLE", color: "var(--md-on-surface-d)" };

  const progress = Math.max(0, currentIdx) / FLOW_STEPS.length;

  return (
    <div className="card-3d p-5 flex flex-col max-h-[calc(100vh-6rem)] overflow-hidden shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 shrink-0 border-b" style={{ borderColor: "var(--md-outline)" }}>
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
            style={{ background: "var(--md-primary-c)" }}
          >
            <Workflow className="w-4 h-4" style={{ color: "var(--md-primary)" }} />
          </div>
          <span className="text-sm font-bold tracking-tight" style={{ color: "var(--md-on-bg)" }}>
            Workflow
          </span>
        </div>
        <span
          className="text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full"
          style={{
            color: phase.color,
            background: `${phase.color}15`,
            border: `1px solid ${phase.color}30`,
          }}
        >
          {phase.label}
        </span>
      </div>

      {/* Steps List (Scrollable if viewport is small) */}
      <div className="flex-1 overflow-y-auto py-3 pr-1 space-y-0.5">
        {FLOW_STEPS.map((step, idx) => {
          const isDone = idx < currentIdx;
          const isActive = idx === currentIdx;
          const Icon: LucideIcon = step.icon;

          const iconBg = isDone
            ? "rgba(22,101,52,0.08)"
            : isActive
            ? "#18181b"
            : "transparent";
          const iconColor = isDone
            ? "var(--md-tertiary)"
            : isActive
            ? "#ffffff"
            : "var(--md-on-surface-d)";
          const iconBorder = isDone
            ? "rgba(22,101,52,0.25)"
            : isActive
            ? "#18181b"
            : "var(--md-outline)";

          return (
            <div key={step.id} className="flex gap-3">
              {/* Timeline column */}
              <div className="flex flex-col items-center">
                <div
                  className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 transition-all duration-300"
                  style={{
                    background: iconBg,
                    border: `1.5px solid ${iconBorder}`,
                    color: iconColor,
                  }}
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
                    className="w-px my-1 flex-1 min-h-[14px] transition-all duration-300"
                    style={{
                      background: isDone
                        ? "rgba(5,150,105,0.35)"
                        : "var(--md-outline)",
                    }}
                  />
                )}
              </div>

              {/* Content */}
              <div className={`min-w-0 flex-1 ${idx < FLOW_STEPS.length - 1 ? "pb-2" : ""}`}>
                <div
                  className="text-xs sm:text-sm font-semibold leading-tight transition-colors duration-200 mt-1"
                  style={{
                    color: isDone
                      ? "var(--md-tertiary)"
                      : isActive
                      ? "var(--md-on-bg)"
                      : "var(--md-on-surface-d)",
                  }}
                >
                  {step.label}
                </div>
                <div
                  className="text-[11px] mt-0.5 leading-snug line-clamp-2"
                  style={{ color: "var(--md-on-surface-v)" }}
                >
                  {isActive && flowStep === "optimizing"
                    ? "running…"
                    : step.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Progress bar footer */}
      <div
        className="rounded-xl p-3 shrink-0 space-y-2 border"
        style={{ background: "var(--md-surface-c1)", borderColor: "var(--md-outline)" }}
      >
        <div className="flex items-center justify-between text-xs font-semibold">
          <span style={{ color: "var(--md-on-surface-v)" }}>Progress</span>
          <span style={{ color: "var(--md-on-bg)" }}>
            {Math.max(0, currentIdx)}/{FLOW_STEPS.length}
          </span>
        </div>
        <div
          className="h-2 rounded-full overflow-hidden"
          style={{ background: "var(--md-surface-c3)" }}
        >
          <div
            className="h-full rounded-full transition-all duration-500 ease-out"
            style={{
              width: `${progress * 100}%`,
              background:
                flowStep === "done"
                  ? "var(--md-tertiary)"
                  : "var(--md-primary)",
            }}
          />
        </div>
      </div>
    </div>
  );
}
