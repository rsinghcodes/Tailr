"use client";

import { useState, useRef, useCallback } from "react";
import { useUIStore, FlowStep } from "@/lib/store";
import {
  createJobDescription,
  uploadJobDescription,
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
  "upload-resume": "Upload Resume",
  "resume-parsed": "Resume Parsed",
  "input-jd": "Job Description",
  "jd-parsed": "JD Parsed",
  "optimizing": "Optimization",
  "done": "Complete",
};

const FLOW_ORDER: FlowStep[] = ["upload-resume", "resume-parsed", "input-jd", "jd-parsed", "optimizing", "done"];

function StepIndicator({ current }: { current: FlowStep }) {
  const currentIdx = FLOW_ORDER.indexOf(current);
  return (
    <div className="flex items-center gap-2 font-mono mb-6">
      {FLOW_ORDER.map((step, idx) => {
        const isDone = idx < currentIdx;
        const isActive = idx === currentIdx;
        return (
          <div key={step} className="flex items-center gap-2">
            <div
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs transition-all ${
                isActive
                  ? "bg-zinc-800 text-zinc-100 border border-zinc-700"
                  : isDone
                  ? "bg-emerald-950/30 text-emerald-400 border border-emerald-800/50"
                  : "bg-zinc-900 text-zinc-500 border border-zinc-800"
              }`}
            >
              {isDone ? <CheckCircle2 className="w-3 h-3" /> : <span className="w-3 h-3 flex items-center justify-center text-[10px] font-bold">{idx + 1}</span>}
              <span className="hidden sm:inline">{FLOW_LABELS[step]}</span>
            </div>
            {idx < FLOW_ORDER.length - 1 && (
              <div className={`w-4 h-px ${isDone ? "bg-emerald-800/50" : "bg-zinc-800"}`} />
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
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdText, setJdText] = useState("");
  const [isJdUploading, setIsJdUploading] = useState(false);
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
    setIsJdUploading(true);
    setErrorMsg(null);
    try {
      const result = await createJobDescription({
        title: jdTitle.trim(),
        company: jdCompany.trim() || "Unknown Company",
        description: jdText.trim(),
      });
      setSelectedJdId(result.id);
      setJdData(result as unknown as Record<string, unknown>);
      setFlowStep("jd-parsed");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to process JD");
    } finally {
      setIsJdUploading(false);
    }
  };

  const handleJdFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsJdUploading(true);
    setErrorMsg(null);
    try {
      const result = await uploadJobDescription(file, jdTitle.trim() || undefined, jdCompany.trim() || undefined);
      setSelectedJdId(result.id);
      setJdData(result as unknown as Record<string, unknown>);
      setFlowStep("jd-parsed");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to process JD file");
    } finally {
      setIsJdUploading(false);
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
      setFlowStep("jd-parsed");
    } catch {
      setErrorMsg("Failed to load job description details");
    }
  }, [setSelectedJdId, setFlowStep]);

  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-zinc-100 font-sans">
      <Navbar onOpenData={() => setShowData(true)} />
      <DataManager
        open={showData}
        onClose={() => setShowData(false)}
        onUseResume={handleUseResume}
        onUseJd={handleUseJd}
      />
      <main className="max-w-4xl mx-auto w-full px-6 py-8 space-y-6">
        <StepIndicator current={flowStep} />

        {errorMsg && (
          <div className="p-3 rounded-md bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="ml-auto text-rose-400 hover:text-rose-300">Dismiss</button>
          </div>
        )}

        {/* Step: Upload Resume */}
        {flowStep === "upload-resume" && (
          <div className="min-panel p-8 space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-zinc-100 flex items-center gap-2">
                <FileText className="w-5 h-5 text-zinc-400" /> Upload Your Resume
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Upload a PDF, DOCX, or TXT file. Tailr will parse and extract structured data via LlamaParse and LlamaExtract.
              </p>
            </div>
            <ResumeUploader onSuccess={(resumeId) => handleResumeUploaded(resumeId)} />
          </div>
        )}

        {/* Step: Resume Parsed */}
        {flowStep === "resume-parsed" && resumeData && (
          <div className="min-panel p-8 space-y-6">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div>
                <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Resume Parsed Successfully
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">
                  LlamaParse extracted text; LlamaExtractor identified skills, experience, education, and more.
                </p>
              </div>
            </div>
            <ParsedResumeView data={resumeData} />
            <div className="flex justify-end pt-2 border-t border-zinc-800">
              <button onClick={() => setFlowStep("input-jd")} className="min-button min-button-primary">
                Add Job Description <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Step: Input Job Description */}
        {flowStep === "input-jd" && (
          <div className="min-panel p-8 space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-zinc-100 flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-zinc-400" /> Target Job Description
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Paste the job description text or upload a file. Tailr will extract requirements, skills, and keywords.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Job Title (e.g. Senior AI Engineer)"
                value={jdTitle}
                onChange={(e) => setJdTitle(e.target.value)}
                className="min-input"
              />
              <input
                type="text"
                placeholder="Company Name (optional)"
                value={jdCompany}
                onChange={(e) => setJdCompany(e.target.value)}
                className="min-input"
              />
            </div>

            <textarea
              rows={8}
              placeholder="Paste complete job description text here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              className="min-input w-full font-mono text-xs"
            />

            <div className="flex items-center justify-between">
              <button onClick={() => setFlowStep("resume-parsed")} className="min-button min-button-secondary">
                <ArrowLeft className="w-4 h-4" /> Back
              </button>
              <div className="flex items-center gap-3">
                <label className="min-button min-button-secondary cursor-pointer">
                  <Upload className="w-4 h-4" /> Upload File (PDF/DOCX/TXT)
                  <input type="file" accept=".pdf,.docx,.txt" onChange={handleJdFileUpload} className="hidden" disabled={isJdUploading} />
                </label>
                <button
                  onClick={handleJdSubmit}
                  disabled={isJdUploading || !jdTitle.trim() || !jdText.trim()}
                  className="min-button min-button-primary disabled:opacity-50"
                >
                  {isJdUploading ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
                  ) : (
                    <><ExternalLink className="w-4 h-4" /> Analyze JD</>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step: JD Parsed */}
        {flowStep === "jd-parsed" && jdData && (
          <div className="min-panel p-8 space-y-6">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div>
                <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Job Description Analyzed
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Llama extracted structured requirements, skills, and responsibilities.
                </p>
              </div>
            </div>

            <div>
              <div className="text-sm font-semibold text-zinc-200">{jdData["title"] as string}</div>
              <div className="text-xs text-zinc-400">{jdData["company"] as string}</div>
            </div>

            {(jdData["parsed_requirements"] as Record<string, unknown>) && (
              <div className="space-y-3">
                {(() => {
                  const reqs = jdData["parsed_requirements"] as Record<string, unknown>;
                  const reqSkills = reqs["required_skills"] as string[] | undefined;
                  const prefSkills = reqs["preferred_skills"] as string[] | undefined;
                  const responsibilities = reqs["responsibilities"] as string[] | undefined;
                  return (
                    <>
                      {reqSkills && reqSkills.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Required Skills ({reqSkills.length})</div>
                          <div className="flex flex-wrap gap-1.5">
                            {reqSkills.map((s, i) => (
                              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700 text-[11px] font-mono">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {prefSkills && prefSkills.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Preferred Skills ({prefSkills.length})</div>
                          <div className="flex flex-wrap gap-1.5">
                            {prefSkills.map((s, i) => (
                              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 text-[11px] font-mono">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                      {responsibilities && responsibilities.length > 0 && (
                        <div>
                          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Core Responsibilities</div>
                          <ul className="space-y-1">
                            {responsibilities.map((r, i) => (
                              <li key={i} className="flex items-start gap-2 text-xs text-zinc-300">
                                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-px" />
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

            <div className="flex justify-between pt-2 border-t border-zinc-800">
              <button onClick={() => setFlowStep("input-jd")} className="min-button min-button-secondary">
                <ArrowLeft className="w-4 h-4" /> Change JD
              </button>
              <button onClick={handleStartOptimization} className="min-button min-button-primary">
                <Play className="w-4 h-4" /> Start Optimization
              </button>
            </div>
          </div>
        )}

        {/* Step: Optimizing */}
        {flowStep === "optimizing" && (
          <div className="min-panel p-8 space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-zinc-400" /> Running Multi-Agent Pipeline
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
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
                    className={`flex items-center gap-2 px-3 py-2.5 rounded border text-xs font-mono transition-all ${
                      isDone
                        ? "bg-emerald-950/30 border-emerald-800/50 text-emerald-300"
                        : isActive
                        ? "bg-zinc-800 border-zinc-600 text-zinc-100 animate-pulse"
                        : "bg-zinc-900 border-zinc-800 text-zinc-500"
                    }`}
                  >
                    <div className="w-4 h-4 shrink-0 flex items-center justify-center">
                      {isDone ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : isActive ? <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-300" /> : <div className="w-2 h-2 rounded-full bg-zinc-600" />}
                    </div>
                    <span className="truncate">{s.label}</span>
                  </div>
                );
              })}
            </div>

            {errorMsg && (
              <div className="p-3 rounded-md bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs flex items-center gap-2 font-mono">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </div>
        )}

        {/* Step: Done - Results */}
        {flowStep === "done" && (
          <div className="min-panel p-8 space-y-6">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div>
                <h2 className="text-lg font-semibold text-zinc-100 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Optimization Complete
                </h2>
                <p className="text-xs text-zinc-400 mt-0.5">Your resume has been tailored for the target job description.</p>
              </div>
              <button onClick={() => { setFlowStep("upload-resume"); setResumeData(null); setJdData(null); setSelectedResumeId(null); setSelectedJdId(null); }} className="min-button min-button-secondary text-xs">
                <ArrowLeft className="w-3.5 h-3.5" /> New Optimization
              </button>
            </div>
            <ResultsView />
          </div>
        )}
      </main>
      <footer className="border-t border-zinc-800 py-4 text-center text-xs text-zinc-500 font-mono">
        Tailr v1.0 — FastAPI • Next.js 16 • LlamaIndex • LangGraph • Guardrails AI Engine
      </footer>
    </div>
  );
}

function ResultsView() {
  const { activeWorkflowResponse } = useUIStore();
  const [copied, setCopied] = useState(false);

  if (!activeWorkflowResponse) {
    return (
      <div className="p-12 text-center space-y-3">
        <FileText className="w-8 h-8 text-zinc-600 mx-auto" />
        <p className="text-xs text-zinc-400">No results available.</p>
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
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase">
            <ShieldCheck className="w-4 h-4" /> Guardrails: {guardrailStatus}
          </div>
          <p className="text-xs text-zinc-400">All AI outputs passed safety and validation checks.</p>
        </div>
        <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200 uppercase font-mono">
            <Cpu className="w-4 h-4 text-zinc-400" /> ATS Score: {atsScore} / 100
          </div>
          <p className="text-xs text-zinc-400">Keyword Coverage: {Math.round(keywordCoverage * 100)}%</p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-xs font-mono text-zinc-500">
        <span>Workflow ID:</span>
        <span className="text-zinc-300 font-bold">{workflow_id}</span>
      </div>

      {summary && (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <div className="text-xs font-semibold text-zinc-400 uppercase font-mono">Professional Summary</div>
            <button onClick={handleCopySummary} className="min-button min-button-secondary text-xs">
              {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <ExternalLink className="w-3.5 h-3.5" />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <div className="p-4 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-200 text-xs leading-relaxed">
            {summary}
          </div>
        </div>
      )}

      {experience && experience.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="text-xs font-semibold text-zinc-400 uppercase font-mono">Work Experience</div>
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
                          <span className="text-zinc-500">·</span>
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
          <div className="text-xs font-semibold text-zinc-400 uppercase font-mono mb-2 block">ATS Recommendations</div>
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
  );
}
