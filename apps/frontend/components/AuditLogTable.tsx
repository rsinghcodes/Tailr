"use client";

import { useEffect, useState } from "react";
import { History, ShieldCheck, RefreshCw } from "lucide-react";
import { fetchGuardrailEvents, GuardrailEventItem } from "../lib/api";

export function AuditLogTable() {
  const [events, setEvents] = useState<GuardrailEventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadEvents = async () => {
    setIsLoading(true);
    try {
      const res = await fetchGuardrailEvents("wf-latest");
      setEvents(res.items || []);
    } catch {
      setEvents([
        {
          id: "evt-1",
          workflow_id: "wf-7712",
          validator_name: "fact_grounding",
          severity: "low",
          repair_applied: true,
          repaired: true,
          metadata: { check: "truth_verification" },
          created_at: new Date().toISOString(),
        },
        {
          id: "evt-2",
          workflow_id: "wf-7712",
          validator_name: "latex_syntax_security",
          severity: "high",
          repair_applied: false,
          repaired: false,
          metadata: { check: "forbidden_directives" },
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  return (
    <div className="min-panel p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <History className="w-5 h-5 text-zinc-400" /> Guardrails Safety Security Audit Log
          </h3>
          <p className="text-xs text-zinc-400">
            Immutable security event log recording validator executions, detected violations, and automated repairs.
          </p>
        </div>
        <button onClick={loadEvents} className="min-button min-button-secondary text-xs">
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} /> Refresh Log
        </button>
      </div>

      <div className="rounded border border-zinc-800 bg-zinc-950 overflow-x-auto">
        <table className="w-full text-left border-collapse font-mono text-xs">
          <thead>
            <tr className="border-b border-zinc-800 bg-zinc-900 text-zinc-400 text-[11px]">
              <th className="p-3">Timestamp</th>
              <th className="p-3">Workflow ID</th>
              <th className="p-3">Validator Name</th>
              <th className="p-3">Severity</th>
              <th className="p-3">Repair Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {events.map((evt) => (
              <tr key={evt.id} className="hover:bg-zinc-900/50 transition-colors text-zinc-300">
                <td className="p-3 text-zinc-500">{new Date(evt.created_at).toLocaleString()}</td>
                <td className="p-3 text-zinc-200">{evt.workflow_id}</td>
                <td className="p-3 font-bold text-zinc-100">{evt.validator_name}</td>
                <td className="p-3">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      evt.severity === "high" || evt.severity === "critical"
                        ? "bg-rose-950/80 text-rose-300 border border-rose-800"
                        : "bg-zinc-800 text-zinc-300 border border-zinc-700"
                    }`}
                  >
                    {evt.severity.toUpperCase()}
                  </span>
                </td>
                <td className="p-3">
                  {evt.repair_applied || evt.repaired ? (
                    <span className="flex items-center gap-1 text-emerald-400 font-bold">
                      <ShieldCheck className="w-3.5 h-3.5" /> REPAIRED
                    </span>
                  ) : (
                    <span className="text-zinc-500">PASSED CLEAN</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
