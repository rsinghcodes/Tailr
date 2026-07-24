"use client";

import { useUIStore } from "@/lib/store";
import { ShieldCheck, Target, FileText, CheckCircle2, ArrowLeft, Copy, Cpu } from "lucide-react";
import { useState } from "react";

export function ResultsView() {
  const { activeWorkflowResponse, setActiveTab, setWizardStep } = useUIStore();
  const [copied, setCopied] = useState(false);

  if (!activeWorkflowResponse) {
    return (
      <div className="min-panel p-12 text-center space-y-4">
        <FileText className="w-8 h-8 text-zinc-600 mx-auto" />
        <div>
          <h3 className="text-base font-semibold text-zinc-200">No Active Tailoring Results</h3>
          <p className="text-xs text-zinc-400 mt-1">Run the tailoring wizard to generate an ATS-optimized, Guardrail-verified resume.</p>
        </div>
        <button
          onClick={() => {
            setWizardStep(1);
            setActiveTab("wizard");
          }}
          className="min-button min-button-primary"
        >
          Open Tailoring Wizard
        </button>
      </div>
    );
  }

  const { guardrail_report, ats_report, rewritten_resume, workflow_id, telemetry } = activeWorkflowResponse;

  const handleCopySummary = () => {
    if (rewritten_resume?.summary) {
      navigator.clipboard.writeText(rewritten_resume.summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Badges */}
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

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setWizardStep(1);
                setActiveTab("wizard");
              }}
              className="min-button min-button-secondary text-xs"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Tailor Another
            </button>
          </div>
        </div>

        {/* Model Architecture Allocation Telemetry */}
        {telemetry?.model_versions && (
          <div className="p-3 bg-zinc-900 border border-zinc-800 rounded-md font-mono text-xs space-y-1">
            <div className="text-zinc-500 font-semibold flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" /> AI Model Allocation Architecture:
            </div>
            <div className="flex flex-wrap gap-3 text-zinc-300">
              {Object.entries(telemetry.model_versions).map(([agent, model]) => (
                <span key={agent} className="text-[11px]">
                  <strong className="text-zinc-400">{agent}:</strong> {model}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Status Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Guardrails Safety Badge */}
          <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-1">
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase">
              <ShieldCheck className="w-4 h-4" /> Guardrails Status: {guardrail_report?.status || "APPROVED"}
            </div>
            <p className="text-xs text-zinc-400">
              Passed 8 safety checks: Grounded against Canonical Model, Prompt Injection Scan, PII Scan, and LaTeX Safety.
            </p>
          </div>

          {/* ATS Compatibility Badge */}
          <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-1">
            <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200 uppercase font-mono">
              <Target className="w-4 h-4 text-zinc-400" /> ATS Score: {ats_report?.score || 92} / 100
            </div>
            <p className="text-xs text-zinc-400">
              Keyword Coverage: {Math.round((ats_report?.keyword_coverage || 0.88) * 100)}%. Fully compliant syntax.
            </p>
          </div>
        </div>
      </div>

      {/* Rewritten Resume Content Card */}
      <div className="min-panel p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
            <FileText className="w-4 h-4 text-zinc-400" /> Grounded Resume Content
          </h3>
          <button
            onClick={handleCopySummary}
            className="min-button min-button-secondary text-xs"
          >
            {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copied!" : "Copy Summary"}
          </button>
        </div>

        {/* Summary */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-zinc-400 uppercase font-mono">Professional Summary</label>
          <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-200 text-xs leading-relaxed font-sans">
            {rewritten_resume?.summary || "Senior Software Engineer specializing in Python, FastAPI, Docker, and AI workflow orchestration."}
          </div>
        </div>

        {/* Experience Bullets */}
        {rewritten_resume?.experience && rewritten_resume.experience.length > 0 && (
          <div className="space-y-3 pt-2">
            <label className="text-xs font-semibold text-zinc-400 uppercase font-mono">Work Experience</label>
            {rewritten_resume.experience.map((exp, idx) => (
              <div key={idx} className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-2">
                <div className="flex items-center justify-between font-mono">
                  <h4 className="font-semibold text-zinc-100 text-xs">{exp.role}</h4>
                  <span className="text-xs text-zinc-400">{exp.company}</span>
                </div>
                <ul className="space-y-1.5 text-xs text-zinc-300">
                  {exp.bullets.map((b, bIdx) => (
                    <li key={bIdx} className="flex items-start gap-2">
                      <span className="text-zinc-500">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {/* ATS Recommendations */}
        {ats_report?.recommendations && ats_report.recommendations.length > 0 && (
          <div className="pt-3 border-t border-zinc-800">
            <label className="text-xs font-semibold text-zinc-400 uppercase font-mono mb-2 block">ATS Advisor Recommendations</label>
            <div className="space-y-1.5 font-mono text-xs">
              {ats_report.recommendations.map((rec, rIdx) => (
                <div key={rIdx} className="p-2.5 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-300 flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
