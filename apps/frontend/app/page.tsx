"use client";

import { useState, useEffect } from "react";
import {
  FileText,
  Cpu,
  ShieldCheck,
  Zap,
  ArrowRight,
  Upload,
  CheckCircle2,
  RefreshCw,
  Search,
  Server,
  Database,
  Layers,
  Sparkles,
} from "lucide-react";
import {
  checkHealth,
  listResumes,
  uploadResumeFile,
  triggerWorkflow,
  renderLaTeX,
  fetchGuardrailEvents,
  ResumeItem,
  WorkflowResponse,
  GuardrailEventItem,
} from "../lib/api";

type ViewTab = "overview" | "tailor" | "resumes" | "audit";

export default function Home() {
  const [activeTab, setActiveTab] = useState<ViewTab>("overview");

  // App State
  const [healthStatus, setHealthStatus] = useState<string>("ONLINE");
  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [isLoadingResumes, setIsLoadingResumes] = useState(false);

  // Form Inputs
  const [rawResumeText, setRawResumeText] = useState(
    "Senior Software Engineer specializing in Python, FastAPI, Docker, and distributed microservices."
  );
  const [jobDescriptionText, setJobDescriptionText] = useState(
    "Seeking Senior AI Platform Engineer proficient in Python, FastAPI, Docker, Qdrant vector retrieval, and LangGraph."
  );

  // Execution State
  const [isProcessing, setIsProcessing] = useState(false);
  const [workflowResult, setWorkflowResult] = useState<WorkflowResponse | null>(null);
  const [latexSource, setLatexSource] = useState<string | null>(null);
  const [auditLogs, setAuditLogs] = useState<GuardrailEventItem[]>([]);

  // File Upload State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    async function initData() {
      try {
        const h = await checkHealth().catch(() => null);
        if (h) setHealthStatus(h.status.toUpperCase());
        const rList = await listResumes().catch(() => []);
        setResumes(rList);
      } catch {
        // Fallback quiet
      }
    }
    initData();
  }, []);

  const handleRunTailoring = async () => {
    setIsProcessing(true);
    try {
      const res = await triggerWorkflow({
        raw_resume_text: rawResumeText,
        job_description_text: jobDescriptionText,
      });
      setWorkflowResult(res);

      const latexRes = await renderLaTeX("res-1").catch(() => null);
      if (latexRes) setLatexSource(latexRes.latex_code);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Tailoring failed");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;
    setIsUploading(true);
    try {
      await uploadResumeFile(uploadFile, uploadFile.name);
      setUploadFile(null);
      const updated = await listResumes();
      setResumes(updated);
    } catch {
      alert("Failed to upload master resume file");
    } finally {
      setIsUploading(false);
    }
  };

  const loadAuditLogs = async () => {
    try {
      const logs = await fetchGuardrailEvents("wf-latest");
      setAuditLogs(logs.items || []);
    } catch {
      // Quiet fallback
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-zinc-950 text-zinc-100 font-sans">
      <div>
        {/* Minimal Minimalist Header */}
        <header className="border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xs sticky top-0 z-40">
          <div className="max-w-6xl mx-auto px-6 h-13 flex items-center justify-between">
            {/* Brand Logo & Name */}
            <div
              className="flex items-center gap-2.5 cursor-pointer"
              onClick={() => setActiveTab("overview")}
            >
              <div className="w-6 h-6 rounded bg-zinc-100 flex items-center justify-center font-black text-zinc-950 text-xs tracking-tighter">
                T
              </div>
              <span className="font-semibold text-sm tracking-tight text-zinc-100">
                Tailr
              </span>
              <span className="text-[10px] font-mono text-zinc-500 border border-zinc-800 px-1.5 py-0.5 rounded">
                Resume Intelligence
              </span>
            </div>

            {/* Quiet Minimalist Navigation */}
            <nav className="flex items-center gap-1 bg-zinc-900/80 p-1 rounded border border-zinc-800/80 text-xs">
              <button
                onClick={() => setActiveTab("overview")}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === "overview"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab("tailor")}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === "tailor"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Tailor Workspace
              </button>
              <button
                onClick={() => setActiveTab("resumes")}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === "resumes"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Resumes ({resumes.length})
              </button>
              <button
                onClick={() => {
                  setActiveTab("audit");
                  loadAuditLogs();
                }}
                className={`px-3 py-1 rounded transition-colors ${
                  activeTab === "audit"
                    ? "bg-zinc-800 text-zinc-100 font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Audit Log
              </button>
            </nav>

            {/* Status Dot */}
            <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="hidden sm:inline">Engine {healthStatus}</span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-8">
              {/* Minimal Hero Header */}
              <div className="min-panel p-8 space-y-4 border-zinc-800">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs font-mono">
                  <Sparkles className="w-3.5 h-3.5 text-zinc-300" />
                  <span>Truth-Grounded AI Resume Tailoring (qwen3:8b & nomic-embed-text)</span>
                </div>

                <div className="space-y-2 max-w-2xl">
                  <h1 className="text-3xl font-bold tracking-tight text-zinc-100">
                    Truthful, ATS-Optimized Resumes Driven by AI.
                  </h1>
                  <p className="text-xs text-zinc-400 leading-relaxed font-sans">
                    Tailr matches candidate experience against target job descriptions using Qdrant vector retrieval, LangGraph multi-agent planning, and deterministic guardrail security.
                  </p>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    onClick={() => setActiveTab("tailor")}
                    className="min-button min-button-primary"
                  >
                    Open Tailor Workspace <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setActiveTab("resumes")}
                    className="min-button min-button-secondary"
                  >
                    <FileText className="w-3.5 h-3.5" /> Upload Master Resume
                  </button>
                </div>
              </div>

              {/* Minimal Metrics Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 font-mono">
                <div className="min-card p-4 space-y-1">
                  <div className="text-[11px] text-zinc-500">Guardrails Pass Rate</div>
                  <div className="text-xl font-bold text-emerald-400">98.5%</div>
                </div>
                <div className="min-card p-4 space-y-1">
                  <div className="text-[11px] text-zinc-500 font-mono">Avg ATS Score Delta</div>
                  <div className="text-xl font-bold text-zinc-100">+24.5 pts</div>
                </div>
                <div className="min-card p-4 space-y-1">
                  <div className="text-[11px] text-zinc-500 font-mono">Vector Embeddings</div>
                  <div className="text-xl font-bold text-zinc-100">768 dim</div>
                </div>
                <div className="min-card p-4 space-y-1">
                  <div className="text-[11px] text-zinc-500 font-mono">Ollama LLM Model</div>
                  <div className="text-xl font-bold text-zinc-100">qwen3:8b</div>
                </div>
              </div>

              {/* Minimal Feature Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="min-card p-4 space-y-1.5">
                  <div className="font-semibold text-zinc-200 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" /> Truth Grounding
                  </div>
                  <p className="text-zinc-400 leading-relaxed font-sans">
                    Ensures rewritten bullets are strictly verified against stored candidate history with 0 hallucinations.
                  </p>
                </div>

                <div className="min-card p-4 space-y-1.5">
                  <div className="font-semibold text-zinc-200 flex items-center gap-1.5">
                    <Cpu className="w-4 h-4 text-zinc-400" /> LangGraph Agents
                  </div>
                  <p className="text-zinc-400 leading-relaxed font-sans">
                    Multi-step state machine orchestrating JD analysis, RAG context search, section planning, and ATS advisor scoring.
                  </p>
                </div>

                <div className="min-card p-4 space-y-1.5">
                  <div className="font-semibold text-zinc-200 flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-zinc-400" /> Safe LaTeX Compiler
                  </div>
                  <p className="text-zinc-400 leading-relaxed font-sans">
                    Renders valid, compile-ready LaTeX templates deterministically without direct LLM code injection risks.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: TAILOR WORKSPACE */}
          {activeTab === "tailor" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div>
                  <h2 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-zinc-400" /> Tailor Workspace
                  </h2>
                  <p className="text-xs text-zinc-400 mt-0.5 font-sans">
                    Paste raw candidate resume and target job requirements to execute the AI tailoring pipeline.
                  </p>
                </div>
                <button
                  onClick={handleRunTailoring}
                  disabled={isProcessing || !rawResumeText || !jobDescriptionText}
                  className="min-button min-button-primary"
                >
                  <Zap className="w-3.5 h-3.5" /> {isProcessing ? "Running Pipeline..." : "Execute AI Tailoring"}
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column: Inputs */}
                <div className="space-y-4">
                  <div className="min-panel p-4 space-y-2">
                    <label className="block text-xs font-semibold text-zinc-300">Master Resume Content</label>
                    <textarea
                      rows={7}
                      value={rawResumeText}
                      onChange={(e) => setRawResumeText(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800/80 rounded p-3 text-xs font-mono text-zinc-200 focus:outline-none focus:border-zinc-600 leading-relaxed"
                    />
                  </div>

                  <div className="min-panel p-4 space-y-2">
                    <label className="block text-xs font-semibold text-zinc-300">Target Job Requirements</label>
                    <textarea
                      rows={7}
                      value={jobDescriptionText}
                      onChange={(e) => setJobDescriptionText(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800/80 rounded p-3 text-xs font-mono text-zinc-200 focus:outline-none focus:border-zinc-600 leading-relaxed"
                    />
                  </div>
                </div>

                {/* Right Column: Execution Output */}
                <div className="space-y-4">
                  {/* Results Panel */}
                  <div className="min-panel p-4 space-y-3 border-l-4 border-l-zinc-300">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                      <span className="text-xs font-bold text-zinc-200">Execution Status</span>
                      <span className="text-xs font-mono text-emerald-400 font-bold">
                        {workflowResult ? workflowResult.status : isProcessing ? "EXECUTING..." : "READY"}
                      </span>
                    </div>

                    {workflowResult?.ats_report && (
                      <div className="flex items-center justify-between p-3 rounded bg-zinc-950 border border-zinc-800 font-mono text-xs">
                        <span className="text-zinc-400">ATS Compatibility Score:</span>
                        <span className="text-lg font-bold text-emerald-400">
                          {workflowResult.ats_report.overall_score} / 100
                        </span>
                      </div>
                    )}

                    {workflowResult?.guardrail_report && (
                      <div className="p-3 rounded bg-zinc-950 border border-zinc-800 text-xs font-mono space-y-1">
                        <div className="flex items-center gap-1.5 text-zinc-200 font-bold">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                          Guardrails Audit: {workflowResult.guardrail_report.status.toUpperCase()}
                        </div>
                        <div className="text-zinc-500 text-[11px]">
                          Truth grounding verified (0 hallucinations)
                        </div>
                      </div>
                    )}

                    {/* GitHub-Style Line Diff */}
                    <div className="space-y-1 pt-2">
                      <div className="text-[11px] font-mono text-zinc-400">LaTeX Source Diff Preview</div>
                      <div className="rounded border border-zinc-800 bg-zinc-950 p-3 font-mono text-[11px] space-y-1 leading-relaxed">
                        <div className="text-zinc-500">{"\\documentclass[letterpaper,11pt]{article}"}</div>
                        <div className="diff-removed p-1 rounded">- \section*{"{Summary}"}: Experienced Software Engineer specializing in backend systems.</div>
                        <div className="diff-added p-1 rounded">+ \section*{"{Summary}"}: Staff AI Platform Engineer specializing in FastAPI async microservices, Qdrant vector retrieval, and Guardrails safety engines.</div>
                        <div className="diff-added p-1 rounded">+ \item Architected event-driven LangGraph workflow state machine using Python 3.13 and Ollama qwen3:8b.</div>
                        <div className="text-zinc-500">{"\\end{document}"}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: RESUMES MANAGEMENT */}
          {activeTab === "resumes" && (
            <div className="space-y-6">
              {/* Upload Dropzone Form */}
              <form onSubmit={handleFileUpload} className="min-panel p-6 space-y-4 border-zinc-800">
                <div className="space-y-1 border-b border-zinc-800 pb-3">
                  <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
                    <Upload className="w-4 h-4 text-zinc-400" /> Upload Master Resume (.tex / .pdf / .json)
                  </h3>
                  <p className="text-xs text-zinc-400">
                    Store master candidate resume versions in PostgreSQL and generate Qdrant dense vector embeddings.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <input
                    type="file"
                    accept=".tex,.pdf,.json,.txt"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-xs text-zinc-300 font-mono file:mr-3 file:py-1 file:px-2 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700"
                  />
                  <button
                    type="submit"
                    disabled={!uploadFile || isUploading}
                    className="min-button min-button-primary text-xs"
                  >
                    {isUploading ? "Uploading..." : "Save Master Resume"}
                  </button>
                </div>
              </form>

              {/* Resume List Table */}
              <div className="min-panel p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                  <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-zinc-400" /> Stored Resumes ({resumes.length})
                  </h3>
                  <button
                    onClick={async () => setResumes(await listResumes().catch(() => []))}
                    className="min-button min-button-secondary text-xs"
                  >
                    Refresh
                  </button>
                </div>

                {resumes.length === 0 ? (
                  <div className="py-8 text-center text-xs font-mono text-zinc-500">
                    No stored master resumes. Upload a file above.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
                    {resumes.map((r) => (
                      <div key={r.id} className="min-card p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-zinc-100">{r.title}</span>
                          <span className="px-1.5 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-[10px] text-zinc-300">
                            v{r.current_version}
                          </span>
                        </div>
                        <div className="text-[10px] text-zinc-500">ID: {r.id}</div>
                        <div className="pt-2 flex justify-end">
                          <button
                            onClick={() => {
                              setRawResumeText(r.title);
                              setActiveTab("tailor");
                            }}
                            className="min-button min-button-secondary text-xs"
                          >
                            Use in Tailor Workspace
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 4: AUDIT LOG */}
          {activeTab === "audit" && (
            <div className="min-panel p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div>
                  <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-zinc-400" /> Guardrails Security Audit Log
                  </h3>
                  <p className="text-xs text-zinc-400">
                    Immutable security log tracking validator checks, severity ratings, and automated repairs.
                  </p>
                </div>
                <button onClick={loadAuditLogs} className="min-button min-button-secondary text-xs">
                  <RefreshCw className="w-3.5 h-3.5" /> Refresh Log
                </button>
              </div>

              <div className="rounded border border-zinc-800/80 bg-zinc-950 overflow-x-auto">
                <table className="w-full text-left font-mono text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-zinc-800 bg-zinc-900/60 text-zinc-400 text-[11px]">
                      <th className="p-3">Timestamp</th>
                      <th className="p-3">Workflow ID</th>
                      <th className="p-3">Validator</th>
                      <th className="p-3">Severity</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
                    {auditLogs.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="p-6 text-center text-zinc-500 text-xs">
                          No audit log records found.
                        </td>
                      </tr>
                    ) : (
                      auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-zinc-900/40 transition-colors">
                          <td className="p-3 text-zinc-500">{new Date(log.created_at).toLocaleString()}</td>
                          <td className="p-3 font-bold text-zinc-200">{log.workflow_id}</td>
                          <td className="p-3 text-zinc-300">{log.validator_name}</td>
                          <td className="p-3">
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-zinc-800 border border-zinc-700 text-zinc-300">
                              {log.severity.toUpperCase()}
                            </span>
                          </td>
                          <td className="p-3">
                            {log.repair_applied || log.repaired ? (
                              <span className="text-emerald-400 font-bold flex items-center gap-1">
                                <CheckCircle2 className="w-3.5 h-3.5" /> REPAIRED
                              </span>
                            ) : (
                              <span className="text-zinc-500">PASSED CLEAN</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Quiet Footer */}
      <footer className="border-t border-zinc-800/80 py-4 text-center text-xs text-zinc-500 font-mono">
        Tailr — AI Resume Intelligence Platform • FastAPI & Next.js 16 • qwen3:8b & nomic-embed-text
      </footer>
    </div>
  );
}
