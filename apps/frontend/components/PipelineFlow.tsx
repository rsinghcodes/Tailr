"use client";

import { Fragment } from "react";
import {
  Search, Map, PenTool, ShieldCheck, BadgeCheck, Gauge,
  FileCheck2, Check, Loader2, type LucideIcon,
} from "lucide-react";
import type { StreamStepState } from "@/lib/store";

const STEP_ICONS: Record<string, LucideIcon> = {
  retrieve_context: Search,
  plan: Map,
  rewrite: PenTool,
  guardrails: ShieldCheck,
  validation: BadgeCheck,
  ats_analysis: Gauge,
  render: FileCheck2,
};

function formatMs(ms?: number): string {
  if (ms == null) return "";
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${Math.round(ms)}ms`;
}

function FlowNode({ step }: { step: StreamStepState }) {
  const Icon = STEP_ICONS[step.step] ?? Gauge;
  const isDone = step.status === "done";
  const isActive = step.status === "running";
  const isPending = step.status === "pending";

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

  const cardBg = isDone
    ? "#ffffff"
    : isActive
    ? "var(--md-surface-c1)"
    : "var(--md-surface)";

  const cardBorder = isDone
    ? "rgba(22,101,52,0.20)"
    : isActive
    ? "var(--md-outline-v)"
    : "var(--md-outline)";

  return (
    <div
      className="flex items-center gap-3 rounded-2xl px-4 py-3 transition-all duration-300 sm:w-36 sm:flex-col sm:gap-2 sm:px-3 sm:py-4 sm:text-center w-full"
      style={{ background: cardBg, border: `1px solid ${cardBorder}` }}
    >
      <div
        className="flex items-center justify-center w-10 h-10 shrink-0 rounded-2xl transition-all duration-300"
        style={{ background: iconBg, border: `1.5px solid ${iconBorder}`, color: iconColor }}
      >
        {isActive ? (
          <Loader2 className="w-4.5 h-4.5 animate-spin" />
        ) : isDone ? (
          <Check className="w-4.5 h-4.5" />
        ) : (
          <Icon className="w-4.5 h-4.5" />
        )}
      </div>

      <div className="min-w-0">
        <div
          className="text-xs font-semibold leading-tight"
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
        {step.duration_ms != null && (
          <div
            className="text-[11px] mt-0.5 font-mono"
            style={{ color: "var(--md-on-surface-d)" }}
          >
            {formatMs(step.duration_ms)}
          </div>
        )}
        {isActive && (
          <div className="text-[10px] mt-0.5" style={{ color: "var(--md-primary)" }}>
            running…
          </div>
        )}
      </div>
    </div>
  );
}

function Connector({ active }: { active: boolean }) {
  return (
    <div
      className="ml-5 h-3 w-px shrink-0 sm:ml-0 sm:h-px sm:w-4 rounded-full transition-all duration-300"
      style={{
        background: active
          ? "rgba(187,179,255,0.40)"
          : "var(--md-outline)",
      }}
    />
  );
}

export function PipelineFlow({ steps }: { steps: StreamStepState[] }) {
  const activeIndex = steps.findIndex((s) => s.status === "running");

  return (
    <div className="sm:overflow-x-auto sm:pb-2">
      <div className="flex flex-col sm:flex-row sm:items-center sm:gap-2 sm:min-w-max gap-2">
        {steps.map((s, idx) => (
          <Fragment key={s.step}>
            <FlowNode step={s} />
            {idx < steps.length - 1 && <Connector active={idx < activeIndex} />}
          </Fragment>
        ))}
      </div>
    </div>
  );
}
