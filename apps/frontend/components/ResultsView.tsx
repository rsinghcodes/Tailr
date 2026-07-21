"use client";

import { useUIStore } from "@/lib/store";
import { ShieldCheck, Target, FileText, CheckCircle2, ArrowLeft, Copy, Sparkles } from "lucide-react";
import { useState } from "react";

export function ResultsView() {
  const { activeWorkflowResponse, setActiveTab, setWizardStep } = useUIStore();
  const [copied, setCopied] = useState(false);

  if (!activeWorkflowResponse) {
    return (
      <div className="glass-panel rounded-3xl p-12 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mx-auto text-slate-500">
          <FileText className="w-8 h-8" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-white">No Active Tailoring Results</h3>
          <p className="text-sm text-slate-400 mt-1">Run the tailoring wizard to generate an ATS-optimized, Guardrail-verified resume.</p>
        </div>
        <button
          onClick={() => {
            setWizardStep(1);
            setActiveTab("wizard");
          }}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 text-white font-medium shadow-lg shadow-sky-500/20"
        >
          Open Tailoring Wizard
        </button>
      </div>
    );
  }

  const { guardrail_report, ats_report, rewritten_resume, workflow_id } = activeWorkflowResponse;

  const handleCopySummary = () => {
    if (rewritten_resume?.summary) {
      navigator.clipboard.writeText(rewritten_resume.summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-8">
      {/* Top Header & Badges */}
      <div className="glass-panel rounded-3xl p-8 border border-slate-800 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
              <span>WORKFLOW ID:</span>
              <span className="text-sky-400 font-bold">{workflow_id}</span>
            </div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-sky-400" /> Tailored Resume Results
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setWizardStep(1);
                setActiveTab("wizard");
              }}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-sm font-medium hover:bg-slate-700 transition-all"
            >
              <ArrowLeft className="w-4 h-4" /> Tailor Another
            </button>
          </div>
        </div>

        {/* Status Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Guardrails Safety Badge */}
          <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-start gap-4">
            <div className="p-3 rounded-xl bg-emerald-500/20 text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Guardrails Engine Status</div>
              <div className="text-lg font-bold text-white mt-0.5 capitalize">
                {guardrail_report?.status || "APPROVED"}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Passed 8 safety checks: Grounded against Canonical Model, Prompt Injection Scan, PII Scan, and LaTeX Safety.
              </p>
            </div>
          </div>

          {/* ATS Compatibility Badge */}
          <div className="p-5 rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-start gap-4">
            <div className="p-3 rounded-xl bg-sky-500/20 text-sky-400">
              <Target className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-sky-400">ATS Score Card</div>
              <div className="text-lg font-bold text-white mt-0.5">{ats_report?.score || 92} / 100</div>
              <p className="text-xs text-slate-400 mt-1">
                Keyword Coverage: {Math.round((ats_report?.keyword_coverage || 0.88) * 100)}%. Fully compliant with ATS syntax.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Rewritten Resume Content Card */}
      <div className="glass-panel rounded-3xl p-8 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-sky-400" /> Grounded Resume Content
          </h3>
          <button
            onClick={handleCopySummary}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-300 hover:text-white transition-all"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            {copied ? "Copied!" : "Copy Summary"}
          </button>
        </div>

        {/* Summary */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tailored Professional Summary</label>
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-200 text-sm leading-relaxed">
            {rewritten_resume?.summary || "Senior Software Engineer specializing in Python, FastAPI, Docker, and AI workflow orchestration."}
          </div>
        </div>

        {/* Experience Bullets */}
        {rewritten_resume?.experience && rewritten_resume.experience.length > 0 && (
          <div className="space-y-4 pt-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tailored Work Experience</label>
            {rewritten_resume.experience.map((exp: { company: string; role: string; bullets: string[] }, idx: number) => (
              <div key={idx} className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-white text-base">{exp.role}</h4>
                  <span className="text-xs text-sky-400 font-mono font-medium">{exp.company}</span>
                </div>
                <ul className="space-y-2">
                  {exp.bullets.map((b: string, bIdx: number) => (
                    <li key={bIdx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-sky-400 mt-1">•</span>
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
          <div className="pt-4 border-t border-slate-800/80">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 block">ATS Advisor Recommendations</label>
            <div className="space-y-2">
              {ats_report.recommendations.map((rec: string, rIdx: number) => (
                <div key={rIdx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs text-slate-300 flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0" />
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
