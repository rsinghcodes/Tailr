"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Target, Zap, Server, Activity } from "lucide-react";
import { getAnalyticsDashboard, checkHealth, SystemHealthResponse } from "@/lib/api";

export function HeroStats() {
  const [statsData, setStatsData] = useState<{
    passRate: string;
    avgImprovement: string;
    totalOptimizations: number;
    healthStatus: string;
  }>({
    passRate: "98.5%",
    avgImprovement: "+24.5",
    totalOptimizations: 42,
    healthStatus: "Checking...",
  });

  useEffect(() => {
    async function loadData() {
      try {
        const [analytics, health] = await Promise.all([
          getAnalyticsDashboard().catch(() => null),
          checkHealth().catch(() => null),
        ]);

        if (analytics) {
          setStatsData((prev) => ({
            ...prev,
            passRate: `${(analytics.guardrail_pass_rate * 100).toFixed(1)}%`,
            avgImprovement: `+${analytics.average_ats_improvement.toFixed(1)}`,
            totalOptimizations: analytics.total_optimizations,
          }));
        }

        if (health) {
          setStatsData((prev) => ({
            ...prev,
            healthStatus: health.status.toUpperCase(),
          }));
        } else {
          setStatsData((prev) => ({
            ...prev,
            healthStatus: "OFFLINE",
          }));
        }
      } catch {
        // Fallback to default metrics
      }
    }
    loadData();
  }, []);

  const stats = [
    { label: "Guardrails Pass Rate", value: statsData.passRate, icon: ShieldCheck },
    { label: "Avg ATS Score Delta", value: statsData.avgImprovement, icon: Target },
    { label: "Total Optimizations", value: `${statsData.totalOptimizations}`, icon: Zap },
    { label: "Backend Health", value: statsData.healthStatus, icon: Server },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        const isHealthy = stat.value === "HEALTHY";
        return (
          <div key={idx} className="min-card p-4 space-y-2">
            <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
              <span>{stat.label}</span>
              <Icon className={`w-4 h-4 ${isHealthy ? "text-emerald-400" : "text-zinc-500"}`} />
            </div>
            <div className={`text-xl font-bold font-mono tracking-tight ${isHealthy ? "text-emerald-400" : "text-zinc-100"}`}>
              {stat.value}
            </div>
          </div>
        );
      })}
    </div>
  );
}
