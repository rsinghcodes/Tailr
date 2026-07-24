"use client";

import { useState } from "react";
import { useUIStore } from "@/lib/store";
import { triggerWorkflow } from "@/lib/api";
import { ResumeUploader } from "./ResumeUploader";
import { ModelArchitectureBadge } from "./ModelArchitectureBadge";
import { Cpu, ArrowRight, CheckCircle2, AlertCircle, Loader2, FileText, Briefcase, ShieldCheck } from "lucide-react";

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
    savedResumes,
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
    <div className="min-panel p-8 space-y-8">
      {/* Stepper Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-6">
        <div>
          <h2 className="text-xl font-semibold text-zinc-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-zinc-400" /> Resume Tailoring Wizard
          </h2>
          <p className="text-xs text-zinc-400 mt-1">Ground your resume in truth with Multi-Agent AI and mandatory Guardrails safety.</p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center gap-2 font-mono">
          {[1, 2, 3].map((step) => (
            <div
              key={step}
              onClick={() => setWizardStep(step)}
              className={`w-7 h-7 rounded-md flex items-center justify-center font-semibold text-xs cursor-pointer transition-all ${
                wizardStep === step
                  ? "bg-zinc-100 text-zinc-950 font-bold"
                  : wizardStep > step
                  ? "bg-zinc-800 text-emerald-400 border border-zinc-700"
                  : "bg-zinc-900 text-zinc-600 border border-zinc-800"
              }`}
            >
              {wizardStep > step ? <CheckCircle2 className="w-4 h-4" /> : step}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      {wizardStep === 1 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-zinc-400" /> Step 1: Master Resume (.tex / .txt File or Raw Text)
            </label>
            <span className="text-xs text-zinc-500 font-mono">Canonical Source of Truth</span>
          </div>

          {/* Option A: Drag & Drop Uploader */}
          <ResumeUploader />

          {/* Option B: Saved Resumes Quick Select */}
          {savedResumes.length > 0 && (
            <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded-md space-y-2">
              <div className="text-xs text-zinc-400 font-medium">Or select from stored master resumes:</div>
              <div className="flex flex-wrap gap-2">
                {savedResumes.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => {
                      setMasterResumeText(`% Master Resume: ${r.title}\n\\documentclass{article}\n\\begin{document}\n\\section{Experience}\nExperience content from stored resume container ${r.id}.\n\\end{document}`);
                    }}
                    className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-xs text-zinc-200 border border-zinc-700 font-mono"
                  >
                    {r.title} (v{r.current_version})
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Option C: Raw LaTeX Editor */}
          <textarea
            value={masterResumeText}
            onChange={(e) => setMasterResumeText(e.target.value)}
            rows={7}
            className="min-input w-full font-mono text-xs"
            placeholder="Paste your master resume LaTeX or plain text..."
          />

          <div className="flex justify-end">
            <button
              onClick={() => setWizardStep(2)}
              className="min-button min-button-primary"
            >
              Next: Job Description <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {wizardStep === 2 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-zinc-400" /> Step 2: Target Job Description
            </label>
            <span className="text-xs text-zinc-500 font-mono">Target Role Requirements</span>
          </div>

          <textarea
            value={jobDescriptionText}
            onChange={(e) => setJobDescriptionText(e.target.value)}
            rows={9}
            className="min-input w-full font-mono text-xs"
            placeholder="Paste the target job description text..."
          />

          <div className="flex justify-between">
            <button
              onClick={() => setWizardStep(1)}
              className="min-button min-button-secondary"
            >
              Back
            </button>
            <button
              onClick={() => setWizardStep(3)}
              className="min-button min-button-primary"
            >
              Next: Review & Execute <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {wizardStep === 3 && (
        <div className="space-y-6">
          {/* Model Architecture Display */}
          <ModelArchitectureBadge />

          <div className="min-card p-6 space-y-4">
            <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" /> Execute Multi-Agent Tailoring Workflow
            </h3>
            <p className="text-xs text-zinc-400">
              LangGraph coordinates JD analysis, context retrieval, planning, rewriting, and mandatory Guardrails safety verification.
            </p>

            {errorMsg && (
              <div className="p-3 rounded-md bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs flex items-center gap-2 font-mono">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Pipeline Stage Visualizer */}
            <div className="pt-2">
              <div className="text-xs font-semibold text-zinc-500 font-mono uppercase mb-2">LangGraph Pipeline Stages</div>
              <div className="flex flex-wrap gap-1.5 font-mono text-[11px]">
                {pipelineSteps.map((step, idx) => (
                  <span
                    key={idx}
                    className={`px-2.5 py-1 rounded border ${
                      isLoading && idx < 7
                        ? "bg-zinc-800 text-zinc-100 border-zinc-600 animate-pulse"
                        : "bg-zinc-900 text-zinc-400 border-zinc-800"
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
              className="min-button min-button-secondary disabled:opacity-50"
            >
              Back
            </button>
            <button
              onClick={handleStartOptimization}
              disabled={isLoading}
              className="min-button min-button-primary disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Orchestrating Agents...
                </>
              ) : (
                <>
                  <Cpu className="w-4 h-4" /> Start AI Tailoring
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
