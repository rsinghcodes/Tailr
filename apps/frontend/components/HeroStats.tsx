"use client";

import { ShieldCheck, Target, Zap, FileCheck } from "lucide-react";

export function HeroStats() {
  const stats = [
    { label: "Guardrails Pass Rate", value: "100%", icon: ShieldCheck, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
    { label: "Average ATS Score", value: "92 / 100", icon: Target, color: "text-sky-400", bg: "bg-sky-500/10", border: "border-sky-500/20" },
    { label: "Optimization Speed", value: "< 2.5s", icon: Zap, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20" },
    { label: "Fact Grounding", value: "100%", icon: FileCheck, color: "text-indigo-400", bg: "bg-indigo-500/10", border: "border-indigo-500/20" },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div key={idx} className={`glass-card p-5 rounded-2xl border ${stat.border} transition-all`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400">{stat.label}</span>
              <div className={`p-2 rounded-xl ${stat.bg}`}>
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">{stat.value}</div>
          </div>
        );
      })}
    </div>
  );
}
