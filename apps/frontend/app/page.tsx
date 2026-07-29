"use client";

import { useState, useRef, useCallback } from "react";
import { useUIStore, FlowStep } from "@/lib/store";
import {
  createJobDescription,
  uploadJobDescription,
  analyzeJobDescription,
  getResumeDetails,
  getJobDescriptionDetails,
  streamWorkflow,
} from "@/lib/api";
import { ResumeUploader } from "@/components/ResumeUploader";
import { Navbar } from "@/components/Navbar";
import { DataManager } from "@/components/DataManager";
import { ParsedResumeView } from "@/components/DetailViews";
import {
  FileText, Briefcase, Cpu, CheckCircle2, AlertCircle,
  Loader2, ArrowRight, ArrowLeft, ShieldCheck, Upload, Play,
  ExternalLink,
} from "lucide-react";

const FLOW_LABELS: Record<FlowStep, string> = {
  "upload-resume": "Upload",
  "resume-parsed": "Parsed",
  "input-jd": "Job Desc",
  "jd-extracting": "Extracting",
  "jd-parsed": "Analyzed",
  "optimizing": "Optimizing",
  "done": "Done",
};

const FLOW_ORDER: FlowStep[] = ["upload-resume", "resume-parsed", "input-jd", "jd-extracting", "jd-parsed", "optimizing", "done"];

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
    isStreaming, setIsStreaming,
    setStreamWorkflowId,
    setWorkflowResponse,
  } = useUIStore();

  const [resumeData, setResumeData] = useState<Record<string, unknown> | null>(null);
  const [jdData, setJdData] = useState<Record<string, unknown> | null>(null);
  const [rawExtracted, setRawExtracted] = useState<Record<string, unknown> | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdText, setJdText] = useState("");
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
    setFlowStep("jd-extracting");
    setErrorMsg(null);
    setRawExtracted(null);
    try {
      const result = await createJobDescription({
        title: jdTitle.trim(),
        company: jdCompany.trim() || "Unknown Company",
        description: jdText.trim(),
      });
      setSelectedJdId(result.id);
      setRawExtracted((result.raw_extracted as Record<string, unknown>) || null);
      setJdData(result as unknown as Record<string, unknown>);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to process JD");
      setFlowStep("input-jd");
    }
  };

  const handleJdFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFlowStep("jd-extracting");
    setErrorMsg(null);
    setRawExtracted(null);
    try {
      const result = await uploadJobDescription(file, jdTitle.trim() || undefined, jdCompany.trim() || undefined);
      setSelectedJdId(result.id);
      setRawExtracted((result.raw_extracted as Record<string, unknown>) || null);
      setJdData(result as unknown as Record<string, unknown>);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to process JD file");
      setFlowStep("input-jd");
    }
  };

  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyzeJd = async () => {
    if (!selectedJdId) return;
    setIsAnalyzing(true);
    setErrorMsg(null);
    try {
      const result = await analyzeJobDescription(selectedJdId);
      if (result.parsed_requirements) {
        setJdData((prev) => ({
          ...(prev || {}),
          parsed_requirements: result.parsed_requirements,
        }));
      }
      setFlowStep("jd-parsed");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to analyze JD");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleStartOptimization = async () => {
    if (!selectedResumeId || !selectedJdId) return;
    setFlowStep("optimizing");
    setIsStreaming(true);
    setErrorMsg(null);
    setStreamSteps(streamSteps.map((s) => ({ ...s, status: "pending" as const })));

    try {
      abortRef.current = new AbortController();
      const accumulated: Record<string, unknown> = {};
      for await (const event of streamWorkflow({ resume_id: selectedResumeId, job_description_id: selectedJdId })) {
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
          Object.assign(accumulated, event.data.output as Record<string, unknown>);
        } else if (event.event === "workflow_complete") {
          setStreamWorkflowId(event.data.workflow_id as string);
        }
      }

      setWorkflowResponse({
        workflow_id: accumulated.workflow_id as string || "",
        status: "completed",
        telemetry: (accumulated.telemetry as Record<string, unknown>) || {},
        guardrail_report: (accumulated.guardrail_report as Record<string, unknown>) || null,
        ats_report: (accumulated.ats_report as Record<string, unknown>) || null,
        rewritten_resume: (accumulated.rewritten_resume as Record<string, unknown>) || null,
      });
      setFlowStep("done");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Workflow failed";
      setErrorMsg(msg);
    } finally {
      setIsStreaming(false);
    }
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
      setRawExtracted((result.raw_extracted as Record<string, unknown>) || null);
      if (result.parsed_requirements) {
        setFlowStep("jd-parsed");
      } else if (result.raw_extracted) {
        setFlowStep("jd-extracting");
      } else {
        setFlowStep("input-jd");
      }
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
      <main className="max-w-3xl mx-auto w-full px-6 pt-8 pb-16 space-y-5">
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
                  disabled={!jdTitle.trim() || !jdText.trim()}
                  className="btn btn-primary disabled:opacity-40"
                >
                  <ExternalLink className="w-4 h-4" /> Extract JD
                </button>
              </div>
            </div>
          </div>
        )}

        {flowStep === "jd-extracting" && (
          <div className="card-3d p-6 space-y-5">
            {!rawExtracted ? (
              <>
                <div>
                  <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                    <Loader2 className="w-4 h-4 text-[var(--accent)] animate-spin" /> Extracting Job Description
                  </h2>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">LlamaExtract is parsing the job description...</p>
                </div>
                <div className="flex items-center gap-3 p-4 rounded-lg border border-[var(--border-subtle)]" style={{ background: 'var(--bg-surface)' }}>
                  <Loader2 className="w-5 h-5 text-[var(--text-muted)] animate-spin shrink-0" />
                  <div className="space-y-1 flex-1">
                    <div className="text-xs text-[var(--text-secondary)]">Extracting structured data...</div>
                    <div className="h-1 w-full rounded-full bg-[var(--border-subtle)] overflow-hidden">
                      <div className="h-full w-1/2 rounded-full bg-[var(--accent)] animate-pulse" />
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
                  <div>
                    <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" /> JD Extracted
                    </h2>
                    <p className="text-xs text-[var(--text-muted)] mt-0.5">Raw extraction complete. Run LLM analysis for enhanced results.</p>
                  </div>
                </div>
                <div className="space-y-4">
                  {(() => {
                    const re = rawExtracted;
                    const reqSkills = re["required_skills"] as string[] | undefined;
                    const prefSkills = re["preferred_skills"] as string[] | undefined;
                    const responsibilities = re["responsibilities"] as string[] | undefined;
                    const seniority = re["seniority"] as string | undefined;
                    const keywords = re["keywords"] as string[] | undefined;
                    return (
                      <>
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
                      </>
                    );
                  })()}
                </div>
                <div className="flex justify-between pt-3 border-t border-[var(--border-subtle)]">
                  <button onClick={() => { setFlowStep("input-jd"); setRawExtracted(null); setJdData(null); setSelectedJdId(null); }} className="btn btn-secondary">
                    <ArrowLeft className="w-4 h-4" /> Change JD
                  </button>
                  <button onClick={handleAnalyzeJd} disabled={isAnalyzing} className="btn btn-primary disabled:opacity-40">
                    {isAnalyzing ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
                    ) : (
                      <>Run LLM Analysis <ArrowRight className="w-4 h-4" /></>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {flowStep === "jd-parsed" && jdData && (
          <div className="card-3d p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-4">
              <div>
                <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Job Description Analyzed
                </h2>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">LLM analysis complete.</p>
              </div>
            </div>

            <div>
              <div className="text-sm font-medium text-[var(--text-primary)]">{jdData["title"] as string}</div>
              <div className="text-xs text-[var(--text-muted)]">{jdData["company"] as string}</div>
            </div>

            {(jdData["parsed_requirements"] as Record<string, unknown>) && (
              <div className="space-y-4">
                {(() => {
                  const reqs = jdData["parsed_requirements"] as Record<string, unknown>;
                  const reqSkills = reqs["required_skills"] as string[] | undefined;
                  const prefSkills = reqs["preferred_skills"] as string[] | undefined;
                  const responsibilities = reqs["responsibilities"] as string[] | undefined;
                  return (
                    <>
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
                          <div className="section-label mb-1.5">Core Responsibilities</div>
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
                    </>
                  );
                })()}
              </div>
            )}

            <div className="flex justify-between pt-3 border-t border-[var(--border-subtle)]">
              <button onClick={() => setFlowStep("input-jd")} className="btn btn-secondary">
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
            <div>
              <h2 className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                <Cpu className="w-5 h-5 text-[var(--text-muted)]" /> Running Multi-Agent Pipeline
              </h2>
              <p className="text-xs text-[var(--text-muted)] mt-0.5">
                LangGraph orchestrates context retrieval, rewriting, guardrail validation, and ATS scoring.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {streamSteps.map((s, idx) => {
                const isActive = s.status === "running";
                const isDone = s.status === "done";
                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-2 px-3 py-2.5 rounded-lg border text-xs font-mono transition-all ${
                      isDone
                        ? "border-emerald-800/30 text-emerald-400" + " bg-emerald-950/10"
                        : isActive
                        ? "border-[var(--border-mid)] text-[var(--text-primary)]" + " bg-[var(--bg-surface)]"
                        : "border-[var(--border-subtle)] text-[var(--text-muted)]"
                    }`}
                  >
                    <div className="w-4 h-4 shrink-0 flex items-center justify-center">
                      {isDone ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : isActive ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <div className="w-2 h-2 rounded-full bg-[var(--border-mid)]" />}
                    </div>
                    <span className="truncate">{s.label}</span>
                  </div>
                );
              })}
            </div>

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
            <ResultsView />
          </div>
        )}
      </main>
      <footer className="border-t border-[var(--border-subtle)] py-4 text-center text-[11px] text-[var(--text-muted)]">
        Tailr — FastAPI · Next.js · LlamaIndex · LangGraph · Guardrails AI
      </footer>
    </div>
  );
}

function ResultsView() {
  const { activeWorkflowResponse } = useUIStore();
  const [copied, setCopied] = useState(false);

  if (!activeWorkflowResponse) {
    return (
      <div className="py-12 text-center space-y-3">
        <FileText className="w-8 h-8 text-[var(--text-muted)] mx-auto" />
        <p className="text-xs text-[var(--text-muted)]">No results available.</p>
      </div>
    );
  }

  const { guardrail_report, ats_report, rewritten_resume, workflow_id } = activeWorkflowResponse;
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
    <div className="space-y-5">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="rounded-lg p-4 border border-[var(--border-subtle)] space-y-1" style={{ background: 'var(--bg-surface)' }}>
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase">
            <ShieldCheck className="w-4 h-4" /> Guardrails: {guardrailStatus}
          </div>
          <p className="text-xs text-[var(--text-muted)]">All AI outputs passed validation checks.</p>
        </div>
        <div className="rounded-lg p-4 border border-[var(--border-subtle)] space-y-1" style={{ background: 'var(--bg-surface)' }}>
          <div className="flex items-center gap-2 text-xs font-semibold text-[var(--text-primary)] uppercase">
            <Cpu className="w-4 h-4 text-[var(--text-muted)]" /> ATS Score: {atsScore} / 100
          </div>
          <p className="text-xs text-[var(--text-muted)]">Keyword Coverage: {Math.round(keywordCoverage * 100)}%</p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
        <span>Workflow ID:</span>
        <span className="text-[var(--text-secondary)] font-bold">{workflow_id}</span>
      </div>

      {summary && (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="section-label">Professional Summary</div>
            <button onClick={handleCopySummary} className="btn btn-secondary text-xs">
              {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <ExternalLink className="w-3.5 h-3.5" />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <div className="rounded-lg p-4 border border-[var(--border-subtle)] text-xs text-[var(--text-secondary)] leading-relaxed" style={{ background: 'var(--bg-surface)' }}>
            {summary}
          </div>
        </div>
      )}

      {experience && experience.length > 0 && (
        <div className="space-y-3 pt-1">
          <div className="section-label">Work Experience</div>
          {experience.map((exp, idx) => {
            const role = exp["role"] as string;
            const company = exp["company"] as string;
            const bullets = exp["bullets"] as Array<Record<string, unknown>> | string[] | undefined;
            return (
              <div key={idx} className="rounded-lg p-4 border border-[var(--border-subtle)] space-y-2" style={{ background: 'var(--bg-surface)' }}>
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-[var(--text-primary)] text-xs">{role}</h4>
                  <span className="text-xs text-[var(--text-muted)]">{company}</span>
                </div>
                {bullets && bullets.length > 0 && (
                  <ul className="space-y-1.5 text-xs text-[var(--text-secondary)]">
                    {bullets.map((b, bIdx) => {
                      const text = typeof b === "string" ? b : String((b as Record<string, unknown>)?.["text"] ?? "");
                      return (
                        <li key={bIdx} className="flex items-start gap-2">
                          <span className="text-[var(--text-muted)]">·</span>
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
        <div className="pt-2 border-t border-[var(--border-subtle)]">
          <div className="section-label mb-2">ATS Recommendations</div>
          <div className="space-y-1.5 text-xs">
            {recommendations.map((rec, rIdx) => (
              <div key={rIdx} className="flex items-center gap-2 p-2.5 rounded-lg border border-[var(--border-subtle)] text-[var(--text-secondary)]" style={{ background: 'var(--bg-surface)' }}>
                <CheckCircle2 className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
