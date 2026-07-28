"use client";

import { useState, useRef } from "react";
import { useUIStore } from "@/lib/store";
import { streamWorkflow, triggerWorkflow } from "@/lib/api";
import { ResumeUploader } from "./ResumeUploader";
import { ModelArchitectureBadge } from "./ModelArchitectureBadge";
import { Cpu, ArrowRight, CheckCircle2, AlertCircle, Loader2, FileText, Briefcase, ShieldCheck, Play } from "lucide-react";

export function WorkflowWizard() {
  const {
    wizardStep, setWizardStep,
    selectedResumeId, setSelectedResumeId,
    selectedJdId, setSelectedJdId,
    savedResumes,
    savedJds,
    setWorkflowResponse, setActiveTab,
    streamSteps, setStreamSteps,
    isStreaming, setIsStreaming,
    setStreamWorkflowId,
  } = useUIStore();

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const handleStartOptimization = async () => {
    setIsStreaming(true);
    setErrorMsg(null);
    setStreamSteps(streamSteps.map((s) => ({ ...s, status: "pending" as const })));

    try {
      const requestBody: { resume_id?: string; job_description_id?: string } = {};
      if (selectedResumeId) requestBody.resume_id = selectedResumeId;
      if (selectedJdId) requestBody.job_description_id = selectedJdId;

      abortRef.current = new AbortController();

      for await (const event of streamWorkflow(requestBody)) {
        if (event.event === "workflow_start") {
          setStreamWorkflowId(event.data.workflow_id as string);
        } else if (event.event === "step_start") {
          const stepName = event.data.step as string;
          setStreamSteps((prev) =>
            prev.map((s) => (s.step === stepName ? { ...s, status: "running" as const } : s))
          );
        } else if (event.event === "step_complete") {
          const stepName = event.data.step as string;
          setStreamSteps((prev) =>
            prev.map((s) => (s.step === stepName ? { ...s, status: "done" as const } : s))
          );
        } else if (event.event === "workflow_complete") {
          setStreamWorkflowId(event.data.workflow_id as string);
        }
      }

      setIsStreaming(false);

      const response = await triggerWorkflow(requestBody);
      setWorkflowResponse(response);
      setActiveTab("results");
    } catch (err: unknown) {
      setIsStreaming(false);
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
          <p className="text-xs text-zinc-400 mt-1">Optimize your resume for any job description using AI-powered multi-agent workflow.</p>
        </div>
        <div className="flex items-center gap-2 font-mono">
          {[1, 2, 3].map((step) => (
            <div
              key={step}
              onClick={() => !isStreaming && setWizardStep(step)}
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

      {/* Step 1: Resume Selection */}
      {wizardStep === 1 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <FileText className="w-4 h-4 text-zinc-400" /> Step 1: Master Resume
            </label>
            <span className="text-xs text-zinc-500 font-mono">Select a stored resume</span>
          </div>

          <ResumeUploader />

          {savedResumes.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs text-zinc-400 font-medium">Select from stored resumes:</div>
              <div className="flex flex-wrap gap-2">
                {savedResumes.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => setSelectedResumeId(r.id)}
                    className={`px-2.5 py-1 rounded text-xs font-mono border transition-all ${
                      selectedResumeId === r.id
                        ? "bg-zinc-200 text-zinc-950 border-zinc-400"
                        : "bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-zinc-700"
                    }`}
                  >
                    {r.title} (v{r.current_version})
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={() => setWizardStep(2)}
              disabled={!selectedResumeId}
              className="min-button min-button-primary disabled:opacity-50"
            >
              Next: Job Description <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 2: JD Selection */}
      {wizardStep === 2 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-zinc-400" /> Step 2: Target Job Description
            </label>
            <span className="text-xs text-zinc-500 font-mono">Select a stored job description</span>
          </div>

          {savedJds.length > 0 ? (
            <div className="space-y-2">
              <div className="text-xs text-zinc-400 font-medium">Select from analyzed job descriptions:</div>
              {savedJds.map((jd) => (
                <button
                  key={jd.id}
                  onClick={() => setSelectedJdId(jd.id)}
                  className={`w-full text-left px-3 py-2 rounded text-xs font-mono border transition-all ${
                    selectedJdId === jd.id
                      ? "bg-zinc-200 text-zinc-950 border-zinc-400"
                      : "bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-zinc-700"
                  }`}
                >
                  <span className="font-semibold">{jd.title}</span>
                  {jd.company && <span className="text-zinc-400 ml-2">{jd.company}</span>}
                </button>
              ))}
            </div>
          ) : (
            <p className="text-xs text-zinc-500">No job descriptions available. Upload one in the Job Descriptions tab first.</p>
          )}

          <div className="flex justify-between">
            <button onClick={() => setWizardStep(1)} className="min-button min-button-secondary">Back</button>
            <button
              onClick={() => setWizardStep(3)}
              disabled={!selectedJdId}
              className="min-button min-button-primary disabled:opacity-50"
            >
              Next: Review & Execute <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Execute */}
      {wizardStep === 3 && (
        <div className="space-y-6">
          <ModelArchitectureBadge />

          <div className="min-card p-6 space-y-4">
            <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" /> Execute Multi-Agent Tailoring Workflow
            </h3>
            <p className="text-xs text-zinc-400">
              LangGraph orchestrates resume parsing, JD analysis, context retrieval, rewriting, guardrail validation, and ATS scoring.
            </p>

            {errorMsg && (
              <div className="p-3 rounded-md bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs flex items-center gap-2 font-mono">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Live Pipeline Visualizer */}
            <div className="pt-2">
              <div className="text-xs font-semibold text-zinc-500 font-mono uppercase mb-3">Pipeline Stages</div>
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
          </div>

          <div className="flex justify-between">
            <button onClick={() => setWizardStep(2)} disabled={isStreaming} className="min-button min-button-secondary disabled:opacity-50">
              Back
            </button>
            <button onClick={handleStartOptimization} disabled={isStreaming || !selectedResumeId || !selectedJdId} className="min-button min-button-primary disabled:opacity-50">
              {isStreaming ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Running Pipeline...</>
              ) : (
                <><Play className="w-4 h-4" /> Start AI Tailoring</>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
