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

  return (
    <div
      className={`flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 transition-all sm:w-36 sm:flex-col sm:gap-2 sm:px-2 sm:py-3 sm:text-center ${
        isDone
          ? "border-emerald-800/40 bg-emerald-950/10"
          : isActive
          ? "border-[var(--accent)]/40 bg-[var(--accent)]/5"
          : "border-[var(--border-subtle)] bg-[var(--bg-surface)]"
      }`}
    >
      <div
        className={`flex items-center justify-center w-9 h-9 shrink-0 rounded-full border transition-all ${
          isDone
            ? "border-emerald-700/50 bg-emerald-900/30 text-emerald-400"
            : isActive
            ? "border-[var(--accent)]/60 bg-[var(--accent)]/10 text-[var(--accent)]"
            : "border-[var(--border-subtle)] text-[var(--text-muted)]"
        }`}
      >
        {isActive ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : isDone ? (
          <Check className="w-4 h-4" />
        ) : (
          <Icon className="w-4 h-4" />
        )}
      </div>
      <div className="min-w-0">
        <div
          className={`text-[11px] font-medium leading-tight ${
            isDone
              ? "text-emerald-300"
              : isActive
              ? "text-[var(--text-primary)]"
              : "text-[var(--text-muted)]"
          }`}
        >
          {step.label}
        </div>
        {step.duration_ms != null && (
          <div className="text-[10px] font-mono text-[var(--text-muted)] mt-0.5">
            {formatMs(step.duration_ms)}
          </div>
        )}
      </div>
    </div>
  );
}

function Connector({ active }: { active: boolean }) {
  return (
    <div
      className={`ml-5 h-3 w-px shrink-0 sm:ml-0 sm:h-px sm:w-5 ${
        active ? "bg-[var(--accent)]/50" : "bg-[var(--border-subtle)]"
      }`}
    />
  );
}

export function PipelineFlow({ steps }: { steps: StreamStepState[] }) {
  const activeIndex = steps.findIndex((s) => s.status === "running");

  return (
    <div className="sm:overflow-x-auto sm:pb-1">
      <div className="flex flex-col sm:flex-row sm:items-center sm:gap-2 sm:min-w-max">
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
