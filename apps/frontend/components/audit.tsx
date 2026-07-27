"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchGuardrailEvents } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle,
  Wrench,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

export default function Audit() {
  const { activeWorkflowResponse } = useUIStore();
  const [searchId, setSearchId] = useState(
    activeWorkflowResponse?.workflow_id ?? ""
  );
  const [queryId, setQueryId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["guardrail-events", queryId],
    queryFn: () => fetchGuardrailEvents(queryId!),
    enabled: !!queryId,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Audit Trail</h1>
        <p className="mt-1 text-sm text-muted">
          Guardrail events and validation logs for optimization workflows
        </p>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && searchId) setQueryId(searchId);
            }}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2 pl-9 pr-3 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
            placeholder="Enter workflow ID to view audit events…"
          />
        </div>
        <button
          onClick={() => searchId && setQueryId(searchId)}
          disabled={!searchId}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Search className="h-4 w-4" /> Search
        </button>
      </div>

      {activeWorkflowResponse?.guardrail_report && (
        <div className="rounded-xl border border-slate-800 bg-surface p-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-accent" />
            <p className="text-sm font-medium text-white">
              Latest Guardrail Report
            </p>
          </div>
          <div className="mt-2 flex items-center gap-4 text-xs text-muted">
            <span>
              Status:{" "}
              <span
                className={cn(
                  "font-medium",
                  activeWorkflowResponse.guardrail_report.status === "approved"
                    ? "text-success"
                    : "text-warning"
                )}
              >
                {activeWorkflowResponse.guardrail_report.status}
              </span>
            </span>
            <span>
              Violations:{" "}
              {activeWorkflowResponse.guardrail_report.violations.length}
            </span>
            <span>
              Time:{" "}
              {activeWorkflowResponse.guardrail_report.execution_time_ms}ms
            </span>
          </div>
        </div>
      )}

      {queryId && isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="rounded-xl border border-slate-800 bg-surface py-12 text-center">
          <ShieldCheck className="mx-auto mb-3 h-10 w-10 text-slate-600" />
          <p className="text-sm text-muted">
            No guardrail events found for this workflow.
          </p>
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-surface overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50">
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-muted">
                    Validator
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-muted">
                    Severity
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-muted">
                    Code
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-muted">
                    Repaired
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase text-muted">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {data.items.map((event) => (
                  <tr
                    key={event.id}
                    className="transition-colors hover:bg-slate-900/30"
                  >
                    <td className="px-4 py-3">
                      <span className="text-white">{event.validator_name}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={cn(
                          "inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium",
                          event.severity === "critical" &&
                            "bg-danger/15 text-danger",
                          event.severity === "high" &&
                            "bg-danger/15 text-danger",
                          event.severity === "medium" &&
                            "bg-warning/15 text-warning",
                          event.severity === "low" && "bg-muted/15 text-muted"
                        )}
                      >
                        {event.severity === "low" ? (
                          <CheckCircle className="h-3 w-3" />
                        ) : (
                          <AlertTriangle className="h-3 w-3" />
                        )}
                        {event.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-slate-400">
                        {event.violation_code ?? "—"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {event.repair_applied ? (
                        <span className="inline-flex items-center gap-1 text-xs text-success">
                          <Wrench className="h-3 w-3" /> Yes
                        </span>
                      ) : (
                        <span className="text-xs text-slate-600">No</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-muted">
                        {new Date(event.created_at).toLocaleTimeString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
