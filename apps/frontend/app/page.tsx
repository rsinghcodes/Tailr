"use client";

import { useState, useRef, useCallback } from "react";
import { useUIStore, FlowStep } from "@/lib/store";
import {
  createJobDescription,
  uploadJobDescription,
  getResumeDetails,
  getJobDescriptionDetails,
  streamWorkflow,
  refineWorkflow,
  type WorkflowStreamEvent,
  type RefineFeedbackItem,
  type BulletDiff,
  type BulletChange,
  type ExperienceDiff,
} from "@/lib/api";
import { ResumeUploader } from "@/components/ResumeUploader";
import { Navbar } from "@/components/Navbar";
import { DataManager } from "@/components/DataManager";
import { ParsedResumeView } from "@/components/DetailViews";
import { PipelineFlow } from "@/components/PipelineFlow";
import { ResultsDashboard } from "@/components/ResultsDashboard";
import { PipelineSidebar } from "@/components/PipelineSidebar";
import { SavedList } from "@/components/SavedList";
import { FLOW_ORDER, FLOW_LABELS } from "@/lib/flow";
import {
  FileText, Briefcase, Cpu, CheckCircle2, AlertCircle,
  Loader2, ArrowRight, ArrowLeft, Upload, Play,
  ExternalLink, RefreshCw, MessageSquarePlus,
} from "lucide-react";

function StepIndicator({ current }: { current: FlowStep }) {
  const currentIdx = FLOW_ORDER.indexOf(current);
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {FLOW_ORDER.map((step, idx) => {
        const isDone = idx < currentIdx;
        const isActive = idx === currentIdx;
        return (
          <div key={step} className="flex items-center gap-2">
            <div
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-150"
              style={
                isActive
                  ? { background: "var(--md-primary-c)", border: "1px solid var(--md-outline-v)", color: "var(--md-on-bg)" }
                  : isDone
                  ? { background: "var(--md-surface)", border: "1px solid var(--md-outline)", color: "var(--md-tertiary)" }
                  : { color: "var(--md-on-surface-d)" }
              }
            >
              {isDone ? <CheckCircle2 className="w-3.5 h-3.5" /> : <span className="step-dot active" />}
              <span className="hidden sm:inline">{FLOW_LABELS[step]}</span>
            </div>
            {idx < FLOW_ORDER.length - 1 && (
              <div
                className="w-4 h-px rounded-full"
                style={{ background: isDone ? "var(--md-outline-v)" : "var(--md-outline)" }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function Home() {
  const {
    flowStep, setFlowStep,
    selectedResumeId, setSelectedResumeId,
    selectedJdId, setSelectedJdId,
    streamSteps, setStreamSteps,
    setIsStreaming,
    setStreamWorkflowId,
    setWorkflowResponse,
    activeWorkflowResponse,
  } = useUIStore();

  const [resumeData, setResumeData] = useState<Record<string, unknown> | null>(null);
  const [jdData, setJdData] = useState<Record<string, unknown> | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdText, setJdText] = useState("");
  const [isSubmittingJd, setIsSubmittingJd] = useState(false);
  const [showData, setShowData] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const handleResumeUploaded = useCallback(async (resumeId: string) => {
    setSelectedResumeId(resumeId);
    try {
      const details = await getResumeDetails(resumeId);
      setResumeData(details);
      setFlowStep("resume-parsed");
    } catch {
      setErrorMsg("Failed to load parsed resume");
    }
  }, [setSelectedResumeId, setFlowStep]);

  const handleJdSubmit = async () => {
    if (!jdTitle.trim() || !jdText.trim()) return;
    setIsSubmittingJd(true);
    setErrorMsg(null);
    try {
      const result = await createJobDescription({
        title: jdTitle.trim(),
        company: jdCompany.trim() || "Unknown Company",
        description: jdText.trim(),
      });
      setSelectedJdId(result.id);
      setJdData(result as unknown as Record<string, unknown>);
      setFlowStep("jd-ready");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to process JD");
    } finally {
      setIsSubmittingJd(false);
    }
  };

  const handleJdFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsSubmittingJd(true);
    setErrorMsg(null);
    try {
      const result = await uploadJobDescription(file, jdTitle.trim() || undefined, jdCompany.trim() || undefined);
      setSelectedJdId(result.id);
      setJdData(result as unknown as Record<string, unknown>);
      setFlowStep("jd-ready");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to process JD file");
    } finally {
      setIsSubmittingJd(false);
    }
  };

  const runWorkflow = async (events: AsyncGenerator<WorkflowStreamEvent>) => {
    setFlowStep("optimizing");
    setIsStreaming(true);
    setErrorMsg(null);
    setStreamSteps(streamSteps.map((s) => ({ ...s, status: "pending" as const })));

    try {
      abortRef.current = new AbortController();
      const accumulated: Record<string, unknown> = {};
      const stepStartedAt: Record<string, number> = {};
      let finalState: Record<string, unknown> | null = null;
      for await (const event of events) {
        if (event.event === "workflow_start") {
          setStreamWorkflowId(event.data.workflow_id as string);
        } else if (event.event === "step_start") {
          const stepName = event.data.step as string;
          stepStartedAt[stepName] = performance.now();
          setStreamSteps((prev) =>
            prev.map((s) => (s.step === stepName ? { ...s, status: "running" as const } : s))
          );
        } else if (event.event === "step_complete") {
          const stepName = event.data.step as string;
          const start = stepStartedAt[stepName];
          const durationMs = start != null ? Math.round(performance.now() - start) : undefined;
          setStreamSteps((prev) =>
            prev.map((s) =>
              s.step === stepName ? { ...s, status: "done" as const, duration_ms: durationMs } : s
            )
          );
          Object.assign(accumulated, event.data.output as Record<string, unknown>);
        } else if (event.event === "workflow_complete") {
          setStreamWorkflowId(event.data.workflow_id as string);
          finalState = event.data as Record<string, unknown>;
        } else if (event.event === "error") {
          throw new Error((event.data?.message as string) || "Workflow stream failed");
        }
      }

      const workflow_id = (finalState?.workflow_id as string) || (accumulated.workflow_id as string) || "";
      setWorkflowResponse({
        workflow_id,
        status: (finalState?.status as string) || "completed",
        telemetry: (finalState?.telemetry as Record<string, unknown>) || (accumulated.telemetry as Record<string, unknown>) || {},
        guardrail_report: (finalState?.guardrail_report as Record<string, unknown>) || (accumulated.guardrail_report as Record<string, unknown>) || null,
        ats_report: (finalState?.ats_report as Record<string, unknown>) || (accumulated.ats_report as Record<string, unknown>) || null,
        rewritten_resume: (finalState?.rewritten_resume as Record<string, unknown>) || (accumulated.rewritten_resume as Record<string, unknown>) || null,
        bullet_diff: (finalState?.bullet_diff as BulletDiff | null) ?? null,
      });
      setFlowStep("done");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Workflow failed";
      setErrorMsg(msg);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleStartOptimization = () => {
    if (!selectedResumeId || !selectedJdId) return;
    runWorkflow(streamWorkflow({ resume_id: selectedResumeId, job_description_id: selectedJdId }));
  };

  const handleRefine = (feedback: RefineFeedbackItem[], globalComment: string) => {
    const resume = activeWorkflowResponse?.rewritten_resume;
    if (!resume) return;
    runWorkflow(
      refineWorkflow({
        resume,
        job_description_id: selectedJdId,
        feedback,
        global_comment: globalComment.trim() || null,
      })
    );
  };

  const handleUseResume = useCallback(async (id: string) => {
    setSelectedResumeId(id);
    try {
      const details = await getResumeDetails(id);
      setResumeData(details);
      setFlowStep("resume-parsed");
    } catch {
      setErrorMsg("Failed to load resume details");
    }
  }, [setSelectedResumeId, setFlowStep]);

  const handleUseJd = useCallback(async (id: string) => {
    setSelectedJdId(id);
    try {
      const result = await getJobDescriptionDetails(id);
      setJdData(result as unknown as Record<string, unknown>);
      setFlowStep(result.raw_extracted ? "jd-ready" : "input-jd");
    } catch {
      setErrorMsg("Failed to load job description details");
    }
  }, [setSelectedJdId, setFlowStep]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar onOpenData={() => setShowData(true)} />
      <DataManager
        open={showData}
        onClose={() => setShowData(false)}
        onUseResume={handleUseResume}
        onUseJd={handleUseJd}
      />
      <div className="mx-auto w-full max-w-7xl flex-1 px-4 sm:px-6 lg:px-8 pt-8 pb-20">
        <div className="flex flex-col lg:flex-row gap-6 items-start">
          <aside className="w-full lg:w-72 xl:w-80 shrink-0 lg:sticky lg:top-20">
            <PipelineSidebar />
          </aside>

          <div className="flex-1 min-w-0 space-y-6">
            <StepIndicator current={flowStep} />

            {errorMsg && (
              <div className="flex items-center gap-2.5 p-3 rounded-2xl text-sm border" style={{ background: "var(--md-error-c)", borderColor: "rgba(220,38,38,0.2)", color: "var(--md-error)" }}>
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span className="font-medium">{errorMsg}</span>
                <button onClick={() => setErrorMsg(null)} className="ml-auto font-bold opacity-75 hover:opacity-100">Dismiss</button>
              </div>
            )}

        {flowStep === "upload-resume" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3" style={{ color: "var(--md-on-bg)" }}>
                <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{ background: "var(--md-primary-c)", color: "var(--md-on-primary-c)" }}>
                  <FileText className="w-5 h-5" />
                </div>
                Upload Your Resume
              </h2>
              <p className="text-sm mt-1.5" style={{ color: "var(--md-on-surface-v)" }}>
                Upload a PDF, DOCX, or TXT file. Tailr will extract and structure your skills and experiences.
              </p>
            </div>
            <ResumeUploader onSuccess={(resumeId) => handleResumeUploaded(resumeId)} />
            <SavedList variant="resume" onUse={handleUseResume} />
          </div>
        )}

        {flowStep === "resume-parsed" && resumeData && (
          <div className="card-3d p-8 space-y-6">
            <div className="flex items-center justify-between border-b pb-5" style={{ borderColor: "var(--md-outline)" }}>
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2.5" style={{ color: "var(--md-on-bg)" }}>
                  <CheckCircle2 className="w-5 h-5" style={{ color: "var(--md-tertiary)" }} /> Resume Parsed
                </h2>
                <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>Structured data extracted from your resume.</p>
              </div>
            </div>
            <ParsedResumeView data={resumeData} />
            <div className="flex justify-end pt-4 border-t" style={{ borderColor: "var(--md-outline)" }}>
              <button onClick={() => setFlowStep("input-jd")} className="btn btn-primary text-sm px-6 py-2.5">
                Target Job Description <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>
          </div>
        )}

        {flowStep === "input-jd" && (
          <>
            <div className="card-3d p-8 space-y-6">
              <div>
                <h2 className="text-2xl font-bold tracking-tight flex items-center gap-3" style={{ color: "var(--md-on-bg)" }}>
                  <div className="w-10 h-10 rounded-2xl flex items-center justify-center" style={{ background: "var(--md-primary-c)", color: "var(--md-on-primary-c)" }}>
                    <Briefcase className="w-5 h-5" />
                  </div>
                  Target Job Description
                </h2>
                <p className="text-sm mt-1.5" style={{ color: "var(--md-on-surface-v)" }}>
                  Provide the target role details or upload the job posting to analyze required qualifications.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-on-surface-v)" }}>Job Title</label>
                  <input
                    type="text"
                    placeholder="e.g. Senior Machine Learning Engineer"
                    value={jdTitle}
                    onChange={(e) => setJdTitle(e.target.value)}
                    className="input"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-on-surface-v)" }}>Company Name</label>
                  <input
                    type="text"
                    placeholder="e.g. DeepMind"
                    value={jdCompany}
                    onChange={(e) => setJdCompany(e.target.value)}
                    className="input"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-on-surface-v)" }}>Job Description Content</label>
                <textarea
                  rows={8}
                  placeholder="Paste complete job requirements, role responsibilities, and qualifications..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  className="input font-mono text-sm leading-relaxed"
                />
              </div>

              <div className="flex items-center justify-between pt-2">
                <button onClick={() => setFlowStep("resume-parsed")} className="btn btn-secondary">
                  <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <div className="flex items-center gap-3">
                  <label className="btn btn-secondary cursor-pointer">
                    <Upload className="w-4 h-4" /> Upload JD File
                    <input type="file" accept=".pdf,.docx,.txt" onChange={handleJdFileUpload} className="hidden" />
                  </label>
                  <button
                    onClick={handleJdSubmit}
                    disabled={isSubmittingJd || !jdTitle.trim() || !jdText.trim()}
                    className="btn btn-primary"
                  >
                    {isSubmittingJd ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /> Extracting Requirements...</>
                    ) : (
                      <><ExternalLink className="w-4 h-4" /> Extract Requirements</>
                    )}
                  </button>
                </div>
              </div>
            </div>
            <SavedList variant="jd" onUse={handleUseJd} />
          </>
        )}

        {flowStep === "jd-ready" && jdData && (
          <div className="card-3d p-8 space-y-6">
            <div className="flex items-center justify-between border-b pb-5" style={{ borderColor: "var(--md-outline)" }}>
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2.5" style={{ color: "var(--md-on-bg)" }}>
                  <CheckCircle2 className="w-5 h-5" style={{ color: "var(--md-tertiary)" }} /> Job Description Extracted
                </h2>
                <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>AI structured the core competencies and skills.</p>
              </div>
            </div>

            <div className="rounded-2xl p-5 border" style={{ background: "var(--md-surface-c1)", borderColor: "var(--md-outline)" }}>
              <div className="text-lg font-bold" style={{ color: "var(--md-on-bg)" }}>{jdData["title"] as string}</div>
              <div className="text-sm font-medium mt-0.5" style={{ color: "var(--md-primary)" }}>{jdData["company"] as string}</div>
            </div>

            {(() => {
              const raw = jdData["raw_extracted"] as Record<string, unknown> | undefined;
              if (!raw) return <p className="text-sm" style={{ color: "var(--md-on-surface-d)" }}>No extracted data available.</p>;
              const reqSkills = raw["required_skills"] as string[] | undefined;
              const prefSkills = raw["preferred_skills"] as string[] | undefined;
              const responsibilities = raw["responsibilities"] as string[] | undefined;
              const seniority = raw["seniority"] as string | undefined;
              const keywords = raw["keywords"] as string[] | undefined;
              return (
                <div className="space-y-5">
                  {seniority && (
                    <div>
                      <div className="section-label mb-2">Seniority</div>
                      <span className="tag">{seniority}</span>
                    </div>
                  )}
                  {reqSkills && reqSkills.length > 0 && (
                    <div>
                      <div className="section-label mb-2">Required Skills ({reqSkills.length})</div>
                      <div className="flex flex-wrap gap-2">
                        {reqSkills.map((s, i) => <span key={i} className="tag font-medium">{s}</span>)}
                      </div>
                    </div>
                  )}
                  {prefSkills && prefSkills.length > 0 && (
                    <div>
                      <div className="section-label mb-2">Preferred Skills ({prefSkills.length})</div>
                      <div className="flex flex-wrap gap-2">
                        {prefSkills.map((s, i) => <span key={i} className="tag">{s}</span>)}
                      </div>
                    </div>
                  )}
                  {responsibilities && responsibilities.length > 0 && (
                    <div>
                      <div className="section-label mb-2">Key Responsibilities</div>
                      <ul className="space-y-2">
                        {responsibilities.map((r, i) => (
                          <li key={i} className="flex items-start gap-2.5 text-sm leading-relaxed" style={{ color: "var(--md-on-surface-v)" }}>
                            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" style={{ color: "var(--md-tertiary)" }} />
                            <span>{r}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {keywords && keywords.length > 0 && (
                    <div>
                      <div className="section-label mb-2">Keywords ({keywords.length})</div>
                      <div className="flex flex-wrap gap-2">
                        {keywords.map((k, i) => <span key={i} className="tag opacity-75">{k}</span>)}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}

            <div className="flex justify-between pt-4 border-t" style={{ borderColor: "var(--md-outline)" }}>
              <button onClick={() => { setFlowStep("input-jd"); setJdData(null); setSelectedJdId(null); }} className="btn btn-secondary">
                <ArrowLeft className="w-4 h-4" /> Change JD
              </button>
              <button onClick={handleStartOptimization} className="btn btn-primary px-6">
                <Play className="w-4 h-4" /> Start AI Optimization
              </button>
            </div>
          </div>
        )}

        {flowStep === "optimizing" && (
          <div className="card-3d p-8 space-y-6">
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <h2 className="text-xl font-bold flex items-center gap-3" style={{ color: "var(--md-on-bg)" }}>
                  <Cpu className="w-6 h-6" style={{ color: "var(--md-primary)" }} /> Running Multi-Agent Pipeline
                </h2>
                <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>
                  LangGraph orchestrates context retrieval, rewriting, guardrails, and ATS scoring.
                </p>
              </div>
              {(() => {
                const doneCount = streamSteps.filter((s) => s.status === "done").length;
                const running = streamSteps.find((s) => s.status === "running");
                const label = running
                  ? running.label
                  : doneCount === streamSteps.length
                  ? "All steps complete"
                  : "";
                return (
                  <div className="text-right shrink-0">
                    <div className="text-base font-mono font-bold" style={{ color: "var(--md-on-bg)" }}>
                      {Math.min(doneCount + (running ? 1 : 0), streamSteps.length)}
                      <span className="font-normal" style={{ color: "var(--md-on-surface-d)" }}> / {streamSteps.length}</span>
                    </div>
                    <div className="text-xs font-semibold" style={{ color: "var(--md-primary)" }}>{label || "Waiting"}</div>
                  </div>
                );
              })()}
            </div>

            <div className="h-2 rounded-full overflow-hidden" style={{ background: "var(--md-surface-c3)" }}>
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${(streamSteps.filter((s) => s.status !== "pending").length / Math.max(1, streamSteps.length)) * 100}%`,
                  background: "var(--md-primary)",
                  boxShadow: "0 0 12px rgba(187,179,255,0.6)",
                }}
              />
            </div>

            <PipelineFlow steps={streamSteps} />

            {errorMsg && (
              <div className="flex items-center gap-3 p-4 rounded-2xl text-sm" style={{ background: "rgba(255,180,171,0.08)", border: "1px solid rgba(255,180,171,0.25)", color: "var(--md-error)" }}>
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </div>
        )}

        {flowStep === "done" && (
          <div className="card-3d p-8 space-y-6">
            <div className="flex items-center justify-between border-b pb-5" style={{ borderColor: "var(--md-outline)" }}>
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2.5" style={{ color: "var(--md-on-bg)" }}>
                  <CheckCircle2 className="w-6 h-6" style={{ color: "var(--md-tertiary)" }} /> Optimization Complete
                </h2>
                <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>Resume tailored for the target job description.</p>
              </div>
              <button
                onClick={() => { setFlowStep("upload-resume"); setResumeData(null); setJdData(null); setSelectedResumeId(null); setSelectedJdId(null); }}
                className="btn btn-secondary text-sm gap-2"
              >
                <ArrowLeft className="w-4 h-4" /> New Optimization
              </button>
            </div>
            <ResultsDashboard>
              <ResultsView onRefine={handleRefine} />
            </ResultsDashboard>
          </div>
        )}
          </div>
        </div>
      </div>
      <footer className="border-t border-[var(--border-subtle)] py-4 text-center text-[11px] text-[var(--text-muted)]">
        Tailr — FastAPI · Next.js · LlamaIndex · LangGraph · Guardrails AI
      </footer>
    </div>
  );
}

function normalizeText(value: string): string {
  return value.toLowerCase().replace(/\s+/g, " ").trim();
}

function bulletText(value: unknown): string {
  if (typeof value === "string") return value;
  if (value && typeof value === "object") {
    const t = (value as { text?: unknown }).text;
    if (typeof t === "string") return t;
  }
  return "";
}

type BulletRowModel =
  | { kind: "change"; change: BulletChange }
  | { kind: "text"; text: string };

function BulletRow({ change, text, comment, selected, onClick }: {
  change?: BulletChange;
  text?: string;
  comment: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="group cursor-pointer rounded-2xl transition-all p-1"
      style={{
        outline: selected ? "2px solid var(--md-primary)" : "2px solid transparent",
      }}
    >
      <div className="space-y-2.5">
        {change?.change_type === "added" && (
          <div
            className="flex items-start gap-3 p-3.5 rounded-2xl border"
            style={{
              background: "rgba(160,216,212,0.08)",
              borderColor: "rgba(160,216,212,0.25)",
            }}
          >
            <span
              className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 mt-0.5"
              style={{ background: "rgba(160,216,212,0.20)", color: "var(--md-tertiary)" }}
            >
              Added
            </span>
            <span className="text-sm leading-relaxed" style={{ color: "var(--md-tertiary)" }}>
              {change.updated}
            </span>
          </div>
        )}

        {change?.change_type === "removed" && (
          <div
            className="flex items-start gap-3 p-3.5 rounded-2xl border"
            style={{
              background: "rgba(255,180,171,0.06)",
              borderColor: "rgba(255,180,171,0.20)",
            }}
          >
            <span
              className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 mt-0.5"
              style={{ background: "rgba(255,180,171,0.18)", color: "var(--md-error)" }}
            >
              Removed
            </span>
            <span className="text-sm leading-relaxed line-through opacity-75" style={{ color: "var(--md-error)" }}>
              {change.original}
            </span>
          </div>
        )}

        {change?.change_type === "modified" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              className="flex items-start gap-3 p-3.5 rounded-2xl border"
              style={{
                background: "rgba(255,180,171,0.06)",
                borderColor: "rgba(255,180,171,0.20)",
              }}
            >
              <span
                className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 mt-0.5"
                style={{ background: "rgba(255,180,171,0.18)", color: "var(--md-error)" }}
              >
                Before
              </span>
              <span className="text-sm leading-relaxed line-through opacity-75" style={{ color: "var(--md-error)" }}>
                {change.original}
              </span>
            </div>
            <div
              className="flex items-start gap-3 p-3.5 rounded-2xl border"
              style={{
                background: "rgba(160,216,212,0.08)",
                borderColor: "rgba(160,216,212,0.25)",
              }}
            >
              <span
                className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 mt-0.5"
                style={{ background: "rgba(160,216,212,0.20)", color: "var(--md-tertiary)" }}
              >
                After
              </span>
              <span className="text-sm leading-relaxed" style={{ color: "var(--md-tertiary)" }}>
                {change.updated}
              </span>
            </div>
          </div>
        )}

        {!change && text && (
          <div
            className="flex items-start gap-3 p-3.5 rounded-2xl border transition-colors"
            style={{
              background: "var(--md-surface-c1)",
              borderColor: "var(--md-outline)",
            }}
          >
            <span
              className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 mt-0.5"
              style={{ background: "var(--md-surface-c3)", color: "var(--md-on-surface-d)" }}
            >
              Kept
            </span>
            <span className="text-sm leading-relaxed" style={{ color: "var(--md-on-surface-v)" }}>
              {text}
            </span>
          </div>
        )}
      </div>

      {comment && (
        <div
          className="mt-2.5 flex items-start gap-3 px-4 py-3 rounded-2xl border"
          style={{
            background: "rgba(187,179,255,0.08)",
            borderColor: "rgba(187,179,255,0.30)",
          }}
        >
          <MessageSquarePlus className="w-4 h-4 shrink-0 mt-0.5" style={{ color: "var(--md-primary)" }} />
          <span className="text-sm leading-snug" style={{ color: "var(--md-on-bg)" }}>{comment}</span>
        </div>
      )}

      <div className="flex items-center justify-between gap-2 px-1 pt-2">
        <span className="text-xs" style={{ color: "var(--md-on-surface-d)" }}>
          {comment ? "Click to edit specific feedback" : "Click to leave targeted feedback"}
        </span>
        <MessageSquarePlus
          className="w-4 h-4 transition-colors"
          style={{
            color: comment ? "var(--md-primary)" : "var(--md-on-surface-d)",
          }}
        />
      </div>
    </div>
  );
}

function FloatingCommentBox({ value, onChange, onSave, onClose }: {
  value: string;
  onChange: (value: string) => void;
  onSave: () => void;
  onClose: () => void;
}) {
  return (
    <div
      className="absolute left-0 right-0 top-full mt-2 z-30 rounded-2xl border p-4 space-y-3 shadow-2xl"
      style={{
        background: "var(--md-surface-c2)",
        borderColor: "var(--md-outline-v)",
      }}
      onClick={(e) => e.stopPropagation()}
    >
      <textarea
        autoFocus
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        placeholder="Provide guidance for this specific bullet point during re-optimization..."
        className="w-full px-3.5 py-2.5 rounded-xl border bg-transparent text-sm leading-relaxed focus:outline-none"
        style={{
          borderColor: "var(--md-outline)",
          color: "var(--md-on-bg)",
        }}
      />
      <div className="flex items-center justify-end gap-2.5">
        <button onClick={onClose} className="btn btn-secondary text-xs px-3.5 py-1.5">Cancel</button>
        <button onClick={onSave} disabled={!value.trim()} className="btn btn-primary text-xs px-4 py-1.5">Save Comment</button>
      </div>
    </div>
  );
}

function ResultsView({ onRefine }: {
  onRefine: (feedback: RefineFeedbackItem[], globalComment: string) => void;
}) {
  const { activeWorkflowResponse } = useUIStore();
  const [comments, setComments] = useState<Record<string, string>>({});
  const [globalComment, setGlobalComment] = useState("");
  const [activeKey, setActiveKey] = useState<string | null>(null);
  const [draftComment, setDraftComment] = useState("");

  if (!activeWorkflowResponse) {
    return (
      <div className="py-12 text-center space-y-3">
        <FileText className="w-8 h-8 text-[var(--text-muted)] mx-auto" />
        <p className="text-xs text-[var(--text-muted)]">No results available.</p>
      </div>
    );
  }

  const { bullet_diff, workflow_id } = activeWorkflowResponse;
  const summaryChange = bullet_diff?.summary ?? null;
  const experienceChanges = bullet_diff?.experience ?? [];
  const totalChanges =
    (summaryChange ? 1 : 0) +
    experienceChanges.reduce((count, exp) => count + exp.bullets.length, 0);

  const rewrittenResume = activeWorkflowResponse.rewritten_resume;
  const rewrittenExperience: Array<Record<string, unknown>> = Array.isArray(
    rewrittenResume?.experience
  )
    ? (rewrittenResume.experience as Array<Record<string, unknown>>)
    : [];
  const rewrittenSummary =
    typeof rewrittenResume?.summary === "string" ? rewrittenResume.summary : "";

  const expKey = (company: unknown, role: unknown) =>
    `${String(company ?? "").trim().toLowerCase()}|${String(role ?? "").trim().toLowerCase()}`;

  const diffByKey = new Map<string, ExperienceDiff>();
  for (const d of experienceChanges) diffByKey.set(expKey(d.company, d.role), d);

  const rowsFor = (exp: Record<string, unknown>): BulletRowModel[] => {
    const diff = diffByKey.get(expKey(exp.company, exp.role));
    const bullets = Array.isArray(exp.bullets) ? exp.bullets : [];
    const changes = diff?.bullets ?? [];
    const changeByUpdated = new Map<string, BulletChange>();
    for (const c of changes) {
      if (c.updated) changeByUpdated.set(normalizeText(c.updated), c);
    }
    const removed = changes.filter((c) => c.change_type === "removed");
    const rows: BulletRowModel[] = [];
    for (const b of bullets) {
      const text = bulletText(b);
      if (!text) continue;
      const change = changeByUpdated.get(normalizeText(text));
      rows.push(change ? { kind: "change", change } : { kind: "text", text });
    }
    for (const c of removed) rows.push({ kind: "change", change: c });
    return rows;
  };

  const experiences: Array<Record<string, unknown>> =
    rewrittenExperience.length > 0
      ? rewrittenExperience
      : experienceChanges.map((d) => ({
          company: d.company,
          role: d.role,
          bullets: d.bullets.filter((c) => c.updated).map((c) => c.updated as string),
        }));

  const summaryModel: BulletRowModel | null = summaryChange
    ? {
        kind: "change",
        change: {
          change_type: "modified",
          original: summaryChange.original,
          updated: summaryChange.updated,
        },
      }
    : rewrittenSummary
    ? { kind: "text", text: rewrittenSummary }
    : null;

  const openComment = (key: string) => {
    if (activeKey === key) {
      setActiveKey(null);
      return;
    }
    setActiveKey(key);
    setDraftComment(comments[key] ?? "");
  };

  const closeComment = () => {
    setActiveKey(null);
    setDraftComment("");
  };

  const saveComment = (key: string) => {
    setComments((prev) => {
      const next = { ...prev };
      if (draftComment.trim()) next[key] = draftComment.trim();
      else delete next[key];
      return next;
    });
    closeComment();
  };

  const handleSubmit = () => {
    const feedback: RefineFeedbackItem[] = [];
    if (summaryModel && comments["summary"]) {
      feedback.push({
        bullet:
          summaryModel.kind === "change"
            ? summaryModel.change.updated ?? summaryModel.change.original ?? ""
            : summaryModel.text,
        comment: comments["summary"],
      });
    }
    experiences.forEach((exp, expIdx) => {
      rowsFor(exp).forEach((row, rowIdx) => {
        const key = `${expIdx}:${rowIdx}`;
        const comment = comments[key];
        if (!comment) return;
        feedback.push({
          company: typeof exp.company === "string" ? exp.company : null,
          role: typeof exp.role === "string" ? exp.role : null,
          bullet:
            row.kind === "change"
              ? row.change.updated ?? row.change.original ?? ""
              : row.text,
          comment,
        });
      });
    });
    onRefine(feedback, globalComment);
    setComments({});
    setGlobalComment("");
    closeComment();
  };

  const hasFeedback =
    Object.keys(comments).length > 0 || globalComment.trim().length > 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-2 border-b" style={{ borderColor: "var(--md-outline)" }}>
        <div className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-primary)" }}>
          Changes to Apply
        </div>
        <span className="text-sm font-mono font-bold px-3 py-1 rounded-full" style={{ background: "var(--md-surface-c3)", color: "var(--md-on-bg)" }}>
          {totalChanges} {totalChanges === 1 ? "change" : "changes"}
        </span>
      </div>

      <div className="flex items-center gap-2 text-xs font-mono" style={{ color: "var(--md-on-surface-d)" }}>
        <span>Workflow ID:</span>
        <span className="font-semibold" style={{ color: "var(--md-on-surface-v)" }}>{workflow_id}</span>
      </div>

      {totalChanges === 0 && (
        <div
          className="rounded-2xl p-5 border text-sm"
          style={{ background: "var(--md-surface-c1)", borderColor: "var(--md-outline)", color: "var(--md-on-surface-d)" }}
        >
          No changes detected — the optimized resume matches the original content.
        </div>
      )}

      {summaryModel && (
        <div className="space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-primary)" }}>
            Professional Summary
          </div>
          <div className="relative">
            <BulletRow
              change={summaryModel.kind === "change" ? summaryModel.change : undefined}
              text={summaryModel.kind === "text" ? summaryModel.text : undefined}
              comment={comments["summary"] ?? ""}
              selected={activeKey === "summary"}
              onClick={() => openComment("summary")}
            />
            {activeKey === "summary" && (
              <FloatingCommentBox
                value={draftComment}
                onChange={setDraftComment}
                onSave={() => saveComment("summary")}
                onClose={closeComment}
              />
            )}
          </div>
        </div>
      )}

      {experiences.length > 0 && (
        <div className="space-y-4 pt-2">
          <div className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-primary)" }}>
            Work Experience
          </div>
          {experiences.map((exp, expIdx) => (
            <div
              key={expIdx}
              className="rounded-2xl p-5 border space-y-3"
              style={{ background: "var(--md-surface-c1)", borderColor: "var(--md-outline)" }}
            >
              <h4 className="font-bold text-base" style={{ color: "var(--md-on-bg)" }}>
                {typeof exp.role === "string" ? exp.role : ""}
                {typeof exp.company === "string" && exp.company ? (
                  <span className="font-medium text-sm ml-2" style={{ color: "var(--md-primary)" }}>· {exp.company}</span>
                ) : ""}
              </h4>
              <div className="space-y-2">
                {rowsFor(exp).map((row, rowIdx) => {
                  const key = `${expIdx}:${rowIdx}`;
                  return (
                    <div key={rowIdx} className="relative">
                      <BulletRow
                        change={row.kind === "change" ? row.change : undefined}
                        text={row.kind === "text" ? row.text : undefined}
                        comment={comments[key] ?? ""}
                        selected={activeKey === key}
                        onClick={() => openComment(key)}
                      />
                      {activeKey === key && (
                        <FloatingCommentBox
                          value={draftComment}
                          onChange={setDraftComment}
                          onSave={() => saveComment(key)}
                          onClose={closeComment}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-3 pt-4 border-t" style={{ borderColor: "var(--md-outline)" }}>
        <div className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-primary)" }}>
          General Feedback
        </div>
        <textarea
          value={globalComment}
          onChange={(e) => setGlobalComment(e.target.value)}
          rows={3}
          placeholder="Overall direction for next iteration (e.g. keep under one page, emphasize cloud architecture impact)..."
          className="w-full px-4 py-3 rounded-2xl border text-sm leading-relaxed focus:outline-none"
          style={{
            background: "var(--md-surface-c1)",
            borderColor: "var(--md-outline)",
            color: "var(--md-on-bg)",
          }}
        />
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <p className="text-xs" style={{ color: "var(--md-on-surface-d)" }}>
            Click any bullet point to leave comment — only commented items change on re-optimization.
          </p>
          <button
            onClick={handleSubmit}
            disabled={!hasFeedback}
            className="btn btn-primary px-5 py-2.5 text-sm gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Re-optimize with Feedback
          </button>
        </div>
      </div>
    </div>
  );
}
