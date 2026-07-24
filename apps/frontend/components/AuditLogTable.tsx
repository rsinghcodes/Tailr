"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchGuardrailEvents, GuardrailEventItem } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import { ShieldCheck, History, Loader2, AlertCircle, RefreshCw, Lock } from "lucide-react";

export function AuditLogTable() {
  const { activeWorkflowResponse } = useUIStore();
  const [filterWorkflowId, setFilterWorkflowId] = useState(
    activeWorkflowResponse?.workflow_id || ""
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["guardrailEvents", filterWorkflowId],
    queryFn: () => fetchGuardrailEvents(filterWorkflowId),
    enabled: !!filterWorkflowId,
  });

  return (
    <div className="min-panel p-6 space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div>
          <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
            <History className="w-5 h-5 text-zinc-400" /> Guardrail Audit Events Log
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Immutable security audit trail recording every validator execution, violation, and repair.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={filterWorkflowId}
            onChange={(e) => setFilterWorkflowId(e.target.value)}
            placeholder="Workflow ID..."
            className="min-input text-xs font-mono w-56"
          />
          <button
            onClick={() => refetch()}
            disabled={isLoading || !filterWorkflowId}
            className="min-button min-button-secondary text-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Audit Log Content */}
      {!filterWorkflowId ? (
        <div className="p-12 text-center space-y-2">
          <Lock className="w-8 h-8 text-zinc-600 mx-auto" />
          <p className="text-xs text-zinc-400">Enter a valid Workflow ID above or run the tailoring wizard to view audit events.</p>
        </div>
      ) : isLoading ? (
        <div className="p-12 text-center space-y-2">
          <Loader2 className="w-6 h-6 text-zinc-400 animate-spin mx-auto" />
          <p className="text-xs text-zinc-500 font-mono">Fetching audit trail from database...</p>
        </div>
      ) : isError ? (
        <div className="p-4 rounded-md bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>Failed to fetch audit events: {error instanceof Error ? error.message : "Database error"}</span>
        </div>
      ) : data?.items.length === 0 ? (
        <div className="p-12 text-center space-y-2">
          <ShieldCheck className="w-8 h-8 text-emerald-500/50 mx-auto" />
          <p className="text-xs font-semibold text-zinc-200">Zero Violations Recorded</p>
          <p className="text-xs text-zinc-500">All AI outputs passed guardrail checks cleanly without requiring repair or rejection.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono text-zinc-300">
            <thead className="bg-zinc-900 text-zinc-400 font-semibold border-b border-zinc-800">
              <tr>
                <th className="p-3">Validator</th>
                <th className="p-3">Severity</th>
                <th className="p-3">Violation Code</th>
                <th className="p-3">Repaired</th>
                <th className="p-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {data?.items.map((item: GuardrailEventItem) => (
                <tr key={item.id} className="hover:bg-zinc-900/50 transition-colors">
                  <td className="p-3 font-semibold text-zinc-100">{item.validator_name}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 text-[11px]">
                      {item.severity}
                    </span>
                  </td>
                  <td className="p-3 text-zinc-400">{item.violation_code || "N/A"}</td>
                  <td className="p-3">{item.repaired ? "YES" : "NO"}</td>
                  <td className="p-3 text-zinc-500">{new Date(item.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
