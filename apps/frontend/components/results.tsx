"use client";

import { useQuery } from "@tanstack/react-query";
import { getWorkflowHistory } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import {
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle,
  ArrowUpRight,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Results() {
  const { setActiveTab } = useUIStore();
  const { data, isLoading } = useQuery({
    queryKey: ["workflow-history"],
    queryFn: getWorkflowHistory,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Results</h1>
        <p className="mt-1 text-sm text-muted">
          History of all optimization runs and their outcomes
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        </div>
      ) : !data || data.workflows.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-surface py-12 text-center">
          <BarChart3 className="mx-auto mb-3 h-10 w-10 text-slate-600" />
          <p className="text-sm text-muted">
            No optimization results yet. Run the wizard to optimize a resume.
          </p>
          <button
            onClick={() => setActiveTab("wizard")}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            Start Optimization <ArrowUpRight className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="rounded-xl border border-slate-800 bg-surface p-4">
            <p className="text-xs font-medium uppercase text-muted">
              Total: {data.total} workflows
            </p>
          </div>

          {data.workflows.map((wf) => (
            <div
              key={wf.workflow_id}
              className="flex items-center justify-between rounded-xl border border-slate-800 bg-surface p-4 transition-colors hover:border-slate-700"
            >
              <div className="flex items-center gap-4">
                <div
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-lg",
                    wf.status === "COMPLETED"
                      ? "bg-success/15 text-success"
                      : wf.status === "FAILED"
                        ? "bg-danger/15 text-danger"
                        : "bg-warning/15 text-warning"
                  )}
                >
                  {wf.status === "COMPLETED" ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : wf.status === "FAILED" ? (
                    <AlertCircle className="h-5 w-5" />
                  ) : (
                    <Clock className="h-5 w-5" />
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-white">
                    {wf.resume_title} → {wf.job_title}
                  </p>
                  <p className="text-xs text-muted">
                    {new Date(wf.created_at).toLocaleString()} · {wf.status}
                  </p>
                </div>
              </div>

              {wf.ats_score > 0 && (
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-success" />
                  <span className="text-lg font-bold text-success">
                    {wf.ats_score.toFixed(0)}
                  </span>
                  <span className="text-xs text-muted">ATS</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
