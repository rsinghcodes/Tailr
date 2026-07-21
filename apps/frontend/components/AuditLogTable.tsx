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
    <div className="glass-panel rounded-3xl p-8 border border-slate-800 space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <History className="w-6 h-6 text-sky-400" /> Guardrail Audit Events Log
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Immutable security audit trail recording every validator execution, violation, and repair.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={filterWorkflowId}
            onChange={(e) => setFilterWorkflowId(e.target.value)}
            placeholder="Enter Workflow ID..."
            className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white font-mono focus:outline-none focus:border-sky-500/50 w-64"
          />
          <button
            onClick={() => refetch()}
            disabled={isLoading || !filterWorkflowId}
            className="p-2.5 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Audit Log Content */}
      {!filterWorkflowId ? (
        <div className="p-12 text-center space-y-4">
          <Lock className="w-10 h-10 text-slate-600 mx-auto" />
          <p className="text-sm text-slate-400">Enter a valid Workflow ID above or run the tailoring wizard to view audit events.</p>
        </div>
      ) : isLoading ? (
        <div className="p-12 text-center space-y-3">
          <Loader2 className="w-8 h-8 text-sky-400 animate-spin mx-auto" />
          <p className="text-xs text-slate-400 font-mono">Fetching audit trail from database...</p>
        </div>
      ) : isError ? (
        <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>Failed to fetch audit events: {error instanceof Error ? error.message : "Database error"}</span>
        </div>
      ) : data?.items.length === 0 ? (
        <div className="p-12 text-center space-y-2">
          <ShieldCheck className="w-10 h-10 text-emerald-500/50 mx-auto" />
          <p className="text-sm font-semibold text-white">Zero Violations Recorded</p>
          <p className="text-xs text-slate-400">All AI outputs passed guardrail checks cleanly without requiring repair or rejection.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 font-mono uppercase tracking-wider">
              <tr>
                <th className="p-3.5 rounded-l-xl">Validator</th>
                <th className="p-3.5">Severity</th>
                <th className="p-3.5">Violation Code</th>
                <th className="p-3.5">Repaired</th>
                <th className="p-3.5 rounded-r-xl">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono">
              {data?.items.map((item: GuardrailEventItem) => (
                <tr key={item.id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="p-3.5 font-bold text-white">{item.validator_name}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs">
                      {item.severity}
                    </span>
                  </td>
                  <td className="p-3.5 text-sky-400">{item.violation_code || "N/A"}</td>
                  <td className="p-3.5">{item.repaired ? "YES" : "NO"}</td>
                  <td className="p-3.5 text-slate-500">{new Date(item.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
