"use client";

import { ShieldCheck, Target, Zap, FileCheck } from "lucide-react";

export function HeroStats() {
  const stats = [
    { label: "Guardrails Pass Rate", value: "100%", icon: ShieldCheck },
    { label: "Average ATS Score", value: "92 / 100", icon: Target },
    { label: "Optimization Latency", value: "< 2.5s", icon: Zap },
    { label: "Fact Grounding", value: "100%", icon: FileCheck },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div key={idx} className="min-card p-4 space-y-2">
            <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
              <span>{stat.label}</span>
              <Icon className="w-4 h-4 text-zinc-500" />
            </div>
            <div className="text-xl font-bold text-zinc-100 font-mono tracking-tight">{stat.value}</div>
          </div>
        );
      })}
    </div>
  );
}
