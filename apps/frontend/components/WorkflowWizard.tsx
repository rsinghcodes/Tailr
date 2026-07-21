"use client";

import { useState } from "react";
import { useUIStore } from "@/lib/store";
import { triggerWorkflow } from "@/lib/api";
import { Cpu, ArrowRight, CheckCircle2, AlertCircle, Loader2, FileText, Briefcase, Sparkles, ShieldCheck } from "lucide-react";

export function WorkflowWizard() {
  const {
    wizardStep,
    setWizardStep,
    masterResumeText,
    setMasterResumeText,
    jobDescriptionText,
    setJobDescriptionText,
    setWorkflowResponse,
    setActiveTab,
  } = useUIStore();

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const pipelineSteps = [
    "PARSING",
    "JD_ANALYSIS",
    "RETRIEVAL",
    "PLANNING",
    "REWRITING",
    "GUARDRAILS",
    "VALIDATING",
    "ATS_ANALYSIS",
    "COMPLETED",
  ];

  const handleStartOptimization = async () => {
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const response = await triggerWorkflow({
        raw_resume_text: masterResumeText,
        job_description_text: jobDescriptionText,
      });

      setWorkflowResponse(response);
      setIsLoading(false);
      setActiveTab("results");
    } catch (err: unknown) {
      setIsLoading(false);
      const msg = err instanceof Error ? err.message : "Workflow execution failed";
      setErrorMsg(msg);
    }
  };

  return (
    <div className="glass-panel rounded-3xl p-8 border border-slate-800 shadow-2xl space-y-8">
      {/* Stepper Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-sky-400" /> Resume Tailoring Wizard
          </h2>
          <p className="text-sm text-slate-400 mt-1">Ground your resume in truth with Multi-Agent AI and mandatory Guardrails safety.</p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center gap-2">
          {[1, 2, 3].map((step) => (
            <div
              key={step}
              onClick={() => setWizardStep(step)}
              className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm cursor-pointer transition-all ${
                wizardStep === step
                  ? "bg-gradient-to-r from-sky-500 to-indigo-600 text-white ring-4 ring-sky-500/20"
                  : wizardStep > step
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-slate-800 text-slate-500 border border-slate-700"
              }`}
            >
              {wizardStep > step ? <CheckCircle2 className="w-5 h-5" /> : step}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      {wizardStep === 1 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-sky-400" /> Step 1: Master Resume Content (LaTeX or Text)
            </label>
            <span className="text-xs text-slate-400">Canonical Source of Truth</span>
          </div>
          <textarea
            value={masterResumeText}
            onChange={(e) => setMasterResumeText(e.target.value)}
            rows={8}
            className="w-full bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-slate-200 font-mono text-sm focus:outline-none focus:border-sky-500/50 focus:ring-2 focus:ring-sky-500/20 transition-all"
            placeholder="Paste your master resume LaTeX or plain text..."
          />
          <div className="flex justify-end">
            <button
              onClick={() => setWizardStep(2)}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 text-white font-medium shadow-lg shadow-sky-500/20 hover:opacity-95 transition-all"
            >
              Next: Job Description <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {wizardStep === 2 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-indigo-400" /> Step 2: Target Job Description
            </label>
            <span className="text-xs text-slate-400">Target Role Requirements</span>
          </div>
          <textarea
            value={jobDescriptionText}
            onChange={(e) => setJobDescriptionText(e.target.value)}
            rows={8}
            className="w-full bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-slate-200 font-mono text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-2 focus:ring-indigo-500/20 transition-all"
            placeholder="Paste the target job description text..."
          />
          <div className="flex justify-between">
            <button
              onClick={() => setWizardStep(1)}
              className="px-6 py-3 rounded-xl bg-slate-800 text-slate-300 font-medium hover:bg-slate-700 transition-all"
            >
              Back
            </button>
            <button
              onClick={() => setWizardStep(3)}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 text-white font-medium shadow-lg shadow-sky-500/20 hover:opacity-95 transition-all"
            >
              Next: Review & Execute <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {wizardStep === 3 && (
        <div className="space-y-6">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" /> Execute Multi-Agent Tailoring Workflow
            </h3>
            <p className="text-sm text-slate-300">
              LangGraph will orchestrate the JD Analyzer, RAG context retriever, Planning agent, Rewriter, and the Guardrails Engine safety gate.
            </p>

            {errorMsg && (
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-3">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Pipeline Step Visualizer */}
            <div className="pt-2">
              <div className="text-xs font-semibold text-slate-400 mb-3">LANGGRAPH PIPELINE STAGES</div>
              <div className="flex flex-wrap gap-2">
                {pipelineSteps.map((step, idx) => (
                  <span
                    key={idx}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition-all ${
                      isLoading && idx < 7
                        ? "bg-sky-500/20 text-sky-400 border-sky-500/40 animate-pulse"
                        : "bg-slate-800/80 text-slate-400 border-slate-700"
                    }`}
                  >
                    {step}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-between">
            <button
              onClick={() => setWizardStep(2)}
              disabled={isLoading}
              className="px-6 py-3 rounded-xl bg-slate-800 text-slate-300 font-medium hover:bg-slate-700 transition-all disabled:opacity-50"
            >
              Back
            </button>
            <button
              onClick={handleStartOptimization}
              disabled={isLoading}
              className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 via-indigo-600 to-purple-600 text-white font-bold shadow-xl shadow-sky-500/25 hover:opacity-95 transition-all disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" /> Orchestrating Agents...
                </>
              ) : (
                <>
                  <Cpu className="w-5 h-5" /> Start AI Tailoring
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
