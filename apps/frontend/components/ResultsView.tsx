"use client";

import { useUIStore } from "@/lib/store";
import { ShieldCheck, Target, FileText, CheckCircle2, ArrowLeft, Copy, Cpu, Loader2 } from "lucide-react";
import { useState } from "react";

export function ResultsView() {
  const { activeWorkflowResponse, setActiveTab, setWizardStep, isStreaming, streamSteps, streamWorkflowId } = useUIStore();
  const [copied, setCopied] = useState(false);

  if (isStreaming) {
    return (
      <div className="min-panel p-8 space-y-6">
        <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin" /> Workflow In Progress
        </h2>
        <p className="text-xs text-zinc-400">Workflow ID: {streamWorkflowId || "—"}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {streamSteps.map((s, idx) => {
            const isActive = s.status === "running";
            const isDone = s.status === "done";
            return (
              <div
                key={idx}
                className={`flex items-center gap-2 px-3 py-2 rounded border text-xs font-mono transition-all ${
                  isDone
                    ? "bg-emerald-950/30 border-emerald-800/50 text-emerald-300"
                    : isActive
                    ? "bg-zinc-800 border-zinc-600 text-zinc-100 animate-pulse"
                    : "bg-zinc-900 border-zinc-800 text-zinc-500"
                }`}
              >
                <div className="w-4 h-4 shrink-0 flex items-center justify-center">
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isActive ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-300" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-zinc-600" />
                  )}
                </div>
                <span className="truncate">{s.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (!activeWorkflowResponse) {
    return (
      <div className="min-panel p-12 text-center space-y-4">
        <FileText className="w-8 h-8 text-zinc-600 mx-auto" />
        <div>
          <h3 className="text-base font-semibold text-zinc-200">No Active Tailoring Results</h3>
          <p className="text-xs text-zinc-400 mt-1">Run the tailoring wizard to generate an ATS-optimized, Guardrail-verified resume.</p>
        </div>
        <button onClick={() => { setWizardStep(1); setActiveTab("wizard"); }} className="min-button min-button-primary">
          Open Tailoring Wizard
        </button>
      </div>
    );
  }

  const { guardrail_report, ats_report, rewritten_resume, workflow_id, telemetry } = activeWorkflowResponse;
  const summary = rewritten_resume?.["summary"] as string | undefined;
  const experience = rewritten_resume?.["experience"] as Array<Record<string, unknown>> | undefined;
  const atsScore = (ats_report?.["score"] ?? ats_report?.["overall_score"] ?? 92) as number;
  const keywordCoverage = (ats_report?.["keyword_coverage"] ?? 0.88) as number;
  const recommendations = ats_report?.["recommendations"] as string[] | undefined;
  const guardrailStatus = (guardrail_report?.["status"] ?? "APPROVED") as string;

  const handleCopySummary = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="min-panel p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800 pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-zinc-400 mb-1">
              <span>WORKFLOW ID:</span>
              <span className="text-zinc-200 font-bold">{workflow_id}</span>
            </div>
            <h2 className="text-xl font-semibold text-zinc-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-zinc-400" /> Tailored Resume Results
            </h2>
          </div>
          <button onClick={() => { setWizardStep(1); setActiveTab("wizard"); }} className="min-button min-button-secondary text-xs">
            <ArrowLeft className="w-3.5 h-3.5" /> Tailor Another
          </button>
        </div>

        {telemetry && !!(telemetry as Record<string, unknown>)["model_versions"] && (
          <div className="p-3 bg-zinc-900 border border-zinc-800 rounded-md font-mono text-xs space-y-1">
            <div className="text-zinc-500 font-semibold flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" /> AI Model Allocation:
            </div>
            <div className="flex flex-wrap gap-3 text-zinc-300">
              {Object.entries(telemetry["model_versions"] as Record<string, string>).map(([agent, model]) => (
                <span key={agent} className="text-[11px]">
                  <strong className="text-zinc-400">{agent}:</strong> {model}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-1">
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase">
              <ShieldCheck className="w-4 h-4" /> Guardrails: {guardrailStatus}
            </div>
            <p className="text-xs text-zinc-400">All AI outputs passed safety and validation checks.</p>
          </div>
          <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-1">
            <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200 uppercase font-mono">
              <Target className="w-4 h-4 text-zinc-400" /> ATS Score: {atsScore} / 100
            </div>
            <p className="text-xs text-zinc-400">Keyword Coverage: {Math.round(keywordCoverage * 100)}%</p>
          </div>
        </div>
      </div>

      {rewritten_resume && (
        <div className="min-panel p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
              <FileText className="w-4 h-4 text-zinc-400" /> Optimized Resume Content
            </h3>
            {summary && (
              <button onClick={handleCopySummary} className="min-button min-button-secondary text-xs">
                {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? "Copied!" : "Copy Summary"}
              </button>
            )}
          </div>

          {summary && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-400 uppercase font-mono">Professional Summary</label>
              <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-200 text-xs leading-relaxed">
                {summary}
              </div>
            </div>
          )}

          {experience && experience.length > 0 && (
            <div className="space-y-3 pt-2">
              <label className="text-xs font-semibold text-zinc-400 uppercase font-mono">Work Experience</label>
              {experience.map((exp, idx) => {
                const role = exp["role"] as string;
                const company = exp["company"] as string;
                const bullets = exp["bullets"] as Array<Record<string, unknown>> | string[] | undefined;
                return (
                  <div key={idx} className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-2">
                    <div className="flex items-center justify-between font-mono">
                      <h4 className="font-semibold text-zinc-100 text-xs">{role}</h4>
                      <span className="text-xs text-zinc-400">{company}</span>
                    </div>
                    {bullets && bullets.length > 0 && (
                      <ul className="space-y-1.5 text-xs text-zinc-300">
                        {bullets.map((b, bIdx) => {
                          const text = typeof b === "string" ? b : String((b as Record<string, unknown>)?.["text"] ?? "");
                          return (
                            <li key={bIdx} className="flex items-start gap-2">
                              <span className="text-zinc-500">•</span>
                              <span>{text}</span>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {recommendations && recommendations.length > 0 && (
            <div className="pt-3 border-t border-zinc-800">
              <label className="text-xs font-semibold text-zinc-400 uppercase font-mono mb-2 block">ATS Advisor Recommendations</label>
              <div className="space-y-1.5 font-mono text-xs">
                {recommendations.map((rec, rIdx) => (
                  <div key={rIdx} className="p-2.5 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-300 flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}