"use client";

import { useQuery } from "@tanstack/react-query";
import { getAnalyticsDashboard, checkHealth } from "@/lib/api";
import {
  BarChart3,
  TrendingUp,
  ShieldCheck,
  FileText,
  Activity,
  CheckCircle,
  AlertTriangle,
  XCircle,
} from "lucide-react";

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: string | number;
  icon: typeof BarChart3;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-surface p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted">{label}</p>
        <Icon className={`h-5 w-5 ${color}`} />
      </div>
      <p className="mt-2 text-2xl font-bold text-white">{value}</p>
    </div>
  );
}

function HealthBadge({ status }: { status: string }) {
  if (status === "healthy" || status === "online")
    return (
      <span className="inline-flex items-center gap-1 text-xs text-success">
        <CheckCircle className="h-3 w-3" /> Healthy
      </span>
    );
  if (status === "degraded")
    return (
      <span className="inline-flex items-center gap-1 text-xs text-warning">
        <AlertTriangle className="h-3 w-3" /> Degraded
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1 text-xs text-danger">
      <XCircle className="h-3 w-3" /> Down
    </span>
  );
}

export default function Dashboard() {
  const { data: analytics } = useQuery({
    queryKey: ["analytics"],
    queryFn: getAnalyticsDashboard,
  });

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: checkHealth,
    refetchInterval: 30000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-muted">
          Overview of your resume optimization pipeline
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Optimizations"
          value={analytics?.total_optimizations ?? "—"}
          icon={BarChart3}
          color="text-accent"
        />
        <StatCard
          label="Avg ATS Improvement"
          value={
            analytics?.average_ats_improvement != null
              ? `+${analytics.average_ats_improvement.toFixed(1)}%`
              : "—"
          }
          icon={TrendingUp}
          color="text-success"
        />
        <StatCard
          label="Guardrail Pass Rate"
          value={
            analytics?.guardrail_pass_rate != null
              ? `${(analytics.guardrail_pass_rate * 100).toFixed(0)}%`
              : "—"
          }
          icon={ShieldCheck}
          color="text-accent"
        />
        <StatCard
          label="Total Resumes"
          value={analytics?.total_resumes ?? "—"}
          icon={FileText}
          color="text-muted"
        />
      </div>

      <div className="rounded-xl border border-slate-800 bg-surface p-5">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
          <Activity className="h-5 w-5 text-accent" />
          System Health
        </h2>
        {health ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(health.services).map(([name, svc]) => (
              <div
                key={name}
                className="flex items-center justify-between rounded-lg bg-slate-800/50 px-4 py-3"
              >
                <div>
                  <p className="text-sm font-medium capitalize text-white">
                    {name.replace(/_/g, " ")}
                  </p>
                  {svc.latency_ms != null && (
                    <p className="text-xs text-muted">{svc.latency_ms}ms</p>
                  )}
                </div>
                <HealthBadge status={svc.status} />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted">Loading health status…</p>
        )}
      </div>
    </div>
  );
}
