"use client";

import { useState } from "react";
import { useUIStore } from "../lib/store";
import { Cpu, ArrowRight, CheckCircle2, ShieldCheck, AlertCircle, FileText } from "lucide-react";
import { triggerWorkflow, approveWorkflow, WorkflowResponse } from "../lib/api";
import { WorkflowGraph } from "./WorkflowGraph";

export function WorkflowWizard() {
  const {
    wizardStep,
    setWizardStep,
    selectedResumeId,
    selectedResumeTitle,
    selectedJDId,
    selectedJDTitle,
    rawResumeText,
    setRawResumeText,
    jobDescriptionText,
    setJobDescriptionText,
    setCurrentWorkflow,
    setActiveTab,
  } = useUIStore();

  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WorkflowResponse | null>(null);
  const [isApproving, setIsApproving] = useState(false);

  const handleStartOptimization = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const response = await triggerWorkflow({
        resume_id: selectedResumeId || undefined,
        job_description_id: selectedJDId || undefined,
        raw_resume_text: rawResumeText || undefined,
        job_description_text: jobDescriptionText || undefined,
      });

      setResult(response);
      setCurrentWorkflow(response);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Workflow execution failed");
    } finally {
      setIsRunning(false);
    }
  };

  const handleApprove = async () => {
    if (!result?.workflow_id) return;
    setIsApproving(true);
    try {
      const approved = await approveWorkflow(result.workflow_id);
      setResult(approved);
      setCurrentWorkflow(approved);
      setActiveTab("results");
    } catch {
      alert("Workflow approval failed");
    } finally {
      setIsApproving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Wizard Header Progress */}
      <div className="min-panel p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div>
            <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-zinc-400" /> AI Resume Optimization Pipeline
            </h3>
            <p className="text-xs text-zinc-400">
              Step-by-step multi-agent LangGraph workflow execution with human approval gate.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className={wizardStep === 1 ? "text-zinc-100 font-bold" : "text-zinc-500"}>Step 1: Resume</span>
            <span className="text-zinc-600">→</span>
            <span className={wizardStep === 2 ? "text-zinc-100 font-bold" : "text-zinc-500"}>Step 2: Target Role</span>
            <span className="text-zinc-600">→</span>
            <span className={wizardStep === 3 ? "text-zinc-100 font-bold" : "text-zinc-500"}>Step 3: Execute</span>
          </div>
        </div>

        {/* Step 1: Select or Paste Master Resume */}
        {wizardStep === 1 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-zinc-200">Select Master Resume Source</span>
              {selectedResumeTitle && (
                <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2 py-0.5 rounded">
                  Selected: {selectedResumeTitle}
                </span>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Paste Raw Master Resume Text (or select stored resume in Resumes tab)
              </label>
              <textarea
                rows={6}
                placeholder="Paste your raw LaTeX or plain text resume content..."
                value={rawResumeText}
                onChange={(e) => setRawResumeText(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded p-3 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 font-mono leading-relaxed"
              />
            </div>

            <div className="flex justify-between items-center pt-2">
              <button onClick={() => setActiveTab("resumes")} className="min-button min-button-secondary text-xs">
                <FileText className="w-3.5 h-3.5" /> Select from Stored Resumes
              </button>
              <button
                onClick={() => setWizardStep(2)}
                disabled={!selectedResumeId && !rawResumeText}
                className="min-button min-button-primary"
              >
                Continue to Step 2 <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Target Job Description */}
        {wizardStep === 2 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-zinc-200">Select Target Job Description</span>
              {selectedJDTitle && (
                <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2 py-0.5 rounded">
                  Selected: {selectedJDTitle}
                </span>
              )}
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Paste Target Job Description Text (or select stored JD in Job Descriptions tab)
              </label>
              <textarea
                rows={6}
                placeholder="Paste the target job requirements, responsibilities, and qualifications..."
                value={jobDescriptionText}
                onChange={(e) => setJobDescriptionText(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded p-3 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 font-mono leading-relaxed"
              />
            </div>

            <div className="flex justify-between items-center pt-2">
              <button onClick={() => setWizardStep(1)} className="min-button min-button-secondary text-xs">
                Back to Step 1
              </button>
              <button
                onClick={() => setWizardStep(3)}
                disabled={!selectedJDId && !jobDescriptionText}
                className="min-button min-button-primary"
              >
                Proceed to Pipeline Execution <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Pipeline Execution & Approval Gate */}
        {wizardStep === 3 && (
          <div className="space-y-6">
            <WorkflowGraph
              currentStep={result?.telemetry?.current_step || (isRunning ? "EXECUTING" : "IDLE")}
              stepHistory={result?.telemetry?.step_history || []}
            />

            {error && (
              <div className="p-3 rounded bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center gap-2 font-mono">
                <AlertCircle className="w-4 h-4 shrink-0" /> {error}
              </div>
            )}

            {!result && (
              <div className="pt-2 flex justify-between items-center border-t border-zinc-800">
                <button onClick={() => setWizardStep(2)} className="min-button min-button-secondary text-xs">
                  Back to Step 2
                </button>
                <button
                  onClick={handleStartOptimization}
                  disabled={isRunning}
                  className="min-button min-button-primary"
                >
                  <Cpu className="w-4 h-4" /> {isRunning ? "Running AI Agents..." : "Run Optimization Pipeline"}
                </button>
              </div>
            )}

            {/* Results Preview & Human Approval Gate */}
            {result && (
              <div className="min-card p-6 space-y-4 border-l-4 border-l-zinc-100">
                <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                  <div className="space-y-1">
                    <div className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Pipeline Execution Completed!
                    </div>
                    <div className="text-[10px] font-mono text-zinc-500">Workflow ID: {result.workflow_id}</div>
                  </div>
                  {result.ats_report && (
                    <div className="text-right">
                      <div className="text-xs text-zinc-400 font-mono">ATS Score</div>
                      <div className="text-xl font-bold font-mono text-emerald-400">
                        {result.ats_report.overall_score} / 100
                      </div>
                    </div>
                  )}
                </div>

                {result.guardrail_report && (
                  <div className="p-3 rounded bg-zinc-900 border border-zinc-800 space-y-1 text-xs font-mono">
                    <div className="flex items-center gap-2 text-zinc-200 font-bold">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" /> Guardrails Safety Status: {result.guardrail_report.status.toUpperCase()}
                    </div>
                    <div className="text-zinc-400 text-[11px]">
                      Violations found: {result.guardrail_report.violations.length} | Repaired: {result.guardrail_report.repair_applied ? "Yes" : "No"}
                    </div>
                  </div>
                )}

                <div className="flex justify-end gap-3 pt-2">
                  <button
                    onClick={handleApprove}
                    disabled={isApproving}
                    className="min-button min-button-primary"
                  >
                    <CheckCircle2 className="w-4 h-4" /> {isApproving ? "Approving..." : "Approve & View LaTeX Diff"}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
