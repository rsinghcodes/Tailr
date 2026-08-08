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
    <div className="flex items-center gap-1.5">
      {FLOW_ORDER.map((step, idx) => {
        const isDone = idx < currentIdx;
        const isActive = idx === currentIdx;
        return (
          <div key={step} className="flex items-center gap-1.5">
            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-mono transition-all ${
              isActive
                ? "bg-[var(--accent)]/10 border border-[var(--accent)]/20 text-[var(--accent)]"
                : isDone
                ? "bg-emerald-950/20 border border-emerald-800/30 text-emerald-400"
                : "text-[var(--text-muted)]"
            }`}>
              {isDone ? <CheckCircle2 className="w-3 h-3" /> : <span className="step-dot active" />}
              <span className="hidden sm:inline">{FLOW_LABELS[step]}</span>
            </div>
            {idx < FLOW_ORDER.length - 1 && (
              <div className={`w-3 h-px ${isDone ? "bg-emerald-800/40" : "bg-[var(--border-subtle)]"}`} />
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
      <div className="mx-auto w-full max-w-7xl flex-1 px-4 sm:px-6 lg:px-8 pt-6 pb-16">
        <div className="flex flex-col lg:flex-row gap-6">
          <aside className="w-full lg:w-72 shrink-0 lg:self-start lg:sticky lg:top-6">
            <PipelineSidebar />
          </aside>

          <div className="flex-1 min-w-0 space-y-5">
            <StepIndicator current={flowStep} />

            {errorMsg && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-rose-950/20 border border-rose-900/30 text-rose-400 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
                <button onClick={() => setErrorMsg(null)} className="ml-auto hover:text-rose-300">Dismiss</button>
              </div>
            )}

        {flowStep === "upload-resume" && (
          <div className="space-y-5">
            <div>
              <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
                <FileText className="w-5 h-5 text-[var(--text-muted)]" /> Upload Your Resume
              </h2>
              <p className="text-xs text-[var(--text-muted)] mt-1">
                Upload a PDF, DOCX, or TXT file. Tailr will parse and extract structured data.
              </p>
            </div>
            <ResumeUploader onSuccess={(resumeId) => handleResumeUploaded(resumeId)} />
            <SavedList variant="resume" onUse={handleUseResume} />
          </div>
        )}

        {flowStep === "resume-parsed" && resumeData && (
          <div className="card-3d p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
              <div>
                <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Resume Parsed
                </h2>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">Structured data extracted from your resume.</p>
              </div>
            </div>
            <ParsedResumeView data={resumeData} />
            <div className="flex justify-end pt-3 border-t border-[var(--border-subtle)]">
              <button onClick={() => setFlowStep("input-jd")} className="btn btn-primary">
                Add Job Description <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {flowStep === "input-jd" && (
          <>
            <div className="card-3d p-6 space-y-5">
              <div>
                <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <Briefcase className="w-5 h-5 text-[var(--text-muted)]" /> Target Job Description
                </h2>
                <p className="text-xs text-[var(--text-muted)] mt-1">
                  Paste the job description or upload a file. Tailr will extract requirements and skills.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Job Title (e.g. Senior AI Engineer)"
                  value={jdTitle}
                  onChange={(e) => setJdTitle(e.target.value)}
                  className="input"
                />
                <input
                  type="text"
                  placeholder="Company Name (optional)"
                  value={jdCompany}
                  onChange={(e) => setJdCompany(e.target.value)}
                  className="input"
                />
              </div>

              <textarea
                rows={8}
                placeholder="Paste complete job description text here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                className="input font-mono text-xs"
              />

              <div className="flex items-center justify-between">
                <button onClick={() => setFlowStep("resume-parsed")} className="btn btn-secondary">
                  <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <div className="flex items-center gap-3">
                  <label className="btn btn-secondary cursor-pointer">
                    <Upload className="w-4 h-4" /> Upload File
                    <input type="file" accept=".pdf,.docx,.txt" onChange={handleJdFileUpload} className="hidden" />
                  </label>
                  <button
                    onClick={handleJdSubmit}
                    disabled={isSubmittingJd || !jdTitle.trim() || !jdText.trim()}
                    className="btn btn-primary disabled:opacity-40"
                  >
                    {isSubmittingJd ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /> Extracting...</>
                    ) : (
                      <><ExternalLink className="w-4 h-4" /> Extract JD</>
                    )}
                  </button>
                </div>
              </div>
            </div>
            <SavedList variant="jd" onUse={handleUseJd} />
          </>
        )}

        {flowStep === "jd-ready" && jdData && (
          <div className="card-3d p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
              <div>
                <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Job Description Extracted
                </h2>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">LlamaExtract extracted structure from the job description.</p>
              </div>
            </div>

            <div>
              <div className="text-sm font-medium text-[var(--text-primary)]">{jdData["title"] as string}</div>
              <div className="text-xs text-[var(--text-muted)]">{jdData["company"] as string}</div>
            </div>

            {(() => {
              const raw = jdData["raw_extracted"] as Record<string, unknown> | undefined;
              if (!raw) return <p className="text-xs text-[var(--text-muted)]">No extracted data available.</p>;
              const reqSkills = raw["required_skills"] as string[] | undefined;
              const prefSkills = raw["preferred_skills"] as string[] | undefined;
              const responsibilities = raw["responsibilities"] as string[] | undefined;
              const seniority = raw["seniority"] as string | undefined;
              const keywords = raw["keywords"] as string[] | undefined;
              return (
                <div className="space-y-4">
                  {seniority && (
                    <div>
                      <div className="section-label mb-1.5">Seniority</div>
                      <span className="tag">{seniority}</span>
                    </div>
                  )}
                  {reqSkills && reqSkills.length > 0 && (
                    <div>
                      <div className="section-label mb-1.5">Required Skills ({reqSkills.length})</div>
                      <div className="flex flex-wrap gap-1.5">
                        {reqSkills.map((s, i) => <span key={i} className="tag">{s}</span>)}
                      </div>
                    </div>
                  )}
                  {prefSkills && prefSkills.length > 0 && (
                    <div>
                      <div className="section-label mb-1.5">Preferred Skills ({prefSkills.length})</div>
                      <div className="flex flex-wrap gap-1.5">
                        {prefSkills.map((s, i) => <span key={i} className="tag">{s}</span>)}
                      </div>
                    </div>
                  )}
                  {responsibilities && responsibilities.length > 0 && (
                    <div>
                      <div className="section-label mb-1.5">Responsibilities</div>
                      <ul className="space-y-1">
                        {responsibilities.map((r, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-[var(--text-secondary)]">
                            <CheckCircle2 className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0 mt-px" />
                            <span>{r}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {keywords && keywords.length > 0 && (
                    <div>
                      <div className="section-label mb-1.5">Keywords ({keywords.length})</div>
                      <div className="flex flex-wrap gap-1.5">
                        {keywords.map((k, i) => <span key={i} className="tag">{k}</span>)}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}

            <div className="flex justify-between pt-3 border-t border-[var(--border-subtle)]">
              <button onClick={() => { setFlowStep("input-jd"); setJdData(null); setSelectedJdId(null); }} className="btn btn-secondary">
                <ArrowLeft className="w-4 h-4" /> Change JD
              </button>
              <button onClick={handleStartOptimization} className="btn btn-primary">
                <Play className="w-4 h-4" /> Start Optimization
              </button>
            </div>
          </div>
        )}

        {flowStep === "optimizing" && (
          <div className="card-3d p-6 space-y-5">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-[var(--accent)]" /> Running Multi-Agent Pipeline
                </h2>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">
                  LangGraph orchestrates context retrieval, rewriting, guardrail validation, and ATS scoring.
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
                    <div className="text-sm font-mono font-bold text-[var(--text-primary)]">
                      {Math.min(doneCount + (running ? 1 : 0), streamSteps.length)}
                      <span className="text-[var(--text-muted)] font-normal"> / {streamSteps.length}</span>
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)]">{label || "Waiting"}</div>
                  </div>
                );
              })()}
            </div>

            <div className="h-1 rounded-full bg-[var(--bg-elevated)] overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${(streamSteps.filter((s) => s.status !== "pending").length / Math.max(1, streamSteps.length)) * 100}%`,
                  background: "var(--accent)",
                }}
              />
            </div>

            <PipelineFlow steps={streamSteps} />

            {errorMsg && (
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-rose-950/20 border border-rose-900/30 text-rose-400 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </div>
        )}

        {flowStep === "done" && (
          <div className="card-3d p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
              <div>
                <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Optimization Complete
                </h2>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">Resume tailored for the target job description.</p>
              </div>
              <button onClick={() => { setFlowStep("upload-resume"); setResumeData(null); setJdData(null); setSelectedResumeId(null); setSelectedJdId(null); }} className="btn btn-secondary text-xs">
                <ArrowLeft className="w-3.5 h-3.5" /> New
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
      className={`group cursor-pointer rounded-lg transition-colors ${
        selected
          ? "ring-1 ring-[var(--accent)]/60"
          : "ring-1 ring-transparent hover:ring-[var(--border-mid)]"
      }`}
    >
      <div className="space-y-2">
        {change?.change_type === "added" && (
          <div className="flex items-start gap-2 p-2.5 rounded-lg border border-emerald-800/30 bg-emerald-950/20">
            <span className="text-[10px] font-semibold uppercase text-emerald-400 px-1.5 py-0.5 rounded bg-emerald-900/40 shrink-0 mt-0.5">New</span>
            <span className="text-xs text-emerald-300">{change.updated}</span>
          </div>
        )}

        {change?.change_type === "removed" && (
          <div className="flex items-start gap-2 p-2.5 rounded-lg border border-rose-800/30 bg-rose-950/20">
            <span className="text-[10px] font-semibold uppercase text-rose-400 px-1.5 py-0.5 rounded bg-rose-900/40 shrink-0 mt-0.5">Removed</span>
            <span className="text-xs text-rose-300 line-through">{change.original}</span>
          </div>
        )}

        {change?.change_type === "modified" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            <div className="flex items-start gap-2 p-2.5 rounded-lg border border-rose-800/30 bg-rose-950/20">
              <span className="text-[10px] font-semibold uppercase text-rose-400 shrink-0 mt-0.5">Before</span>
              <span className="text-xs text-rose-300 line-through">{change.original}</span>
            </div>
            <div className="flex items-start gap-2 p-2.5 rounded-lg border border-emerald-800/30 bg-emerald-950/20">
              <span className="text-[10px] font-semibold uppercase text-emerald-400 shrink-0 mt-0.5">After</span>
              <span className="text-xs text-emerald-300">{change.updated}</span>
            </div>
          </div>
        )}

        {!change && text && (
          <div className="flex items-start gap-2 p-2.5 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-elevated)]">
            <span className="text-[10px] font-semibold uppercase text-[var(--text-muted)] px-1.5 py-0.5 rounded bg-[var(--bg-card)] shrink-0 mt-0.5">Kept</span>
            <span className="text-xs text-[var(--text-secondary)]">{text}</span>
          </div>
        )}
      </div>

      {comment && (
        <div
          className="mt-1.5 flex items-start gap-2 px-2.5 py-2 rounded-lg border"
          style={{ background: "var(--accent-glow)", borderColor: "rgba(108, 108, 240, 0.35)" }}
        >
          <MessageSquarePlus className="w-3.5 h-3.5 text-[var(--accent)] shrink-0 mt-0.5" />
          <span className="text-xs text-[var(--text-secondary)]">{comment}</span>
        </div>
      )}

      <div className="flex items-center justify-between gap-2 pt-1.5">
        <span className="text-[11px] text-[var(--text-muted)]">
          {comment ? "Click to edit comment" : "Click to add a comment"}
        </span>
        <MessageSquarePlus
          className={`w-3.5 h-3.5 ${
            comment
              ? "text-[var(--accent)]"
              : "text-[var(--text-muted)] group-hover:text-[var(--text-secondary)]"
          }`}
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
      className="absolute left-0 right-0 top-full mt-1 z-20 rounded-lg border border-[var(--border-mid)] p-2.5 space-y-2 shadow-2xl"
      style={{ background: "var(--bg-surface)" }}
      onClick={(e) => e.stopPropagation()}
    >
      <textarea
        autoFocus
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={2}
        placeholder="Comment for this bullet — only this bullet will change on re-optimization..."
        className="w-full px-2.5 py-1.5 rounded-lg border border-[var(--border-subtle)] bg-transparent text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]/50 placeholder:text-[var(--text-muted)]/60"
      />
      <div className="flex items-center justify-end gap-2">
        <button onClick={onClose} className="btn btn-secondary text-xs">Cancel</button>
        <button onClick={onSave} disabled={!value.trim()} className="btn btn-primary text-xs">Save comment</button>
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
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="section-label">Changes to Apply</div>
        <span className="text-xs font-mono text-[var(--text-secondary)] font-bold">
          {totalChanges} change{totalChanges === 1 ? "" : "s"}
        </span>
      </div>

      <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
        <span>Workflow ID:</span>
        <span className="text-[var(--text-secondary)] font-bold">{workflow_id}</span>
      </div>

      {totalChanges === 0 && (
        <div
          className="rounded-lg p-4 border border-[var(--border-subtle)] text-xs text-[var(--text-muted)]"
          style={{ background: "var(--bg-surface)" }}
        >
          No changes detected — the optimized resume matches the original content.
        </div>
      )}

      {summaryModel && (
        <div className="space-y-2">
          <div className="section-label">Professional Summary</div>
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
        <div className="space-y-3 pt-1">
          <div className="section-label">Work Experience</div>
          {experiences.map((exp, expIdx) => (
            <div
              key={expIdx}
              className="rounded-lg p-4 border border-[var(--border-subtle)] space-y-2"
              style={{ background: "var(--bg-surface)" }}
            >
              <h4 className="font-medium text-[var(--text-primary)] text-xs">
                {typeof exp.role === "string" ? exp.role : ""}
                {typeof exp.company === "string" && exp.company ? ` · ${exp.company}` : ""}
              </h4>
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
          ))}
        </div>
      )}

      <div className="space-y-2 pt-3 border-t border-[var(--border-subtle)]">
        <div className="section-label">General Feedback</div>
        <textarea
          value={globalComment}
          onChange={(e) => setGlobalComment(e.target.value)}
          rows={2}
          placeholder="Overall direction for the next optimization (e.g. keep it under one page, add more quantified impact)..."
          className="w-full px-2.5 py-1.5 rounded-lg border border-[var(--border-subtle)] bg-transparent text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]/50 placeholder:text-[var(--text-muted)]/60"
        />
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
          <p className="text-[11px] text-[var(--text-muted)]">
            Click any bullet to comment on it — only commented bullets change when re-optimizing.
          </p>
          <button
            onClick={handleSubmit}
            disabled={!hasFeedback}
            className="btn btn-primary text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Re-optimize with feedback
          </button>
        </div>
      </div>
    </div>
  );
}
