"use client";

import { useState, useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useUIStore } from "@/lib/store";
import {
  uploadResumeFile,
  listResumes,
  createJobDescription,
  triggerWorkflow,
  getWorkflowStatus,
  approveWorkflow,
  renderLaTeX,
  compilePDF,
} from "@/lib/api";
import {
  Upload,
  FileText,
  Briefcase,
  Play,
  CheckCircle,
  Loader2,
  ArrowRight,
  ArrowLeft,
  Download,
  Eye,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";

const WORKFLOW_STEPS = [
  "PARSING",
  "INDEXING",
  "JD_ANALYSIS",
  "RETRIEVAL",
  "PLANNING",
  "REWRITING",
  "GUARDRAILS",
  "VALIDATING",
  "ATS_ANALYSIS",
  "COMPLETED",
];

const STEP_LABELS: Record<string, string> = {
  PARSING: "Parsing Resume",
  INDEXING: "Indexing Knowledge",
  JD_ANALYSIS: "Analyzing Job Description",
  RETRIEVAL: "Retrieving Relevant Content",
  PLANNING: "Generating Rewrite Plan",
  REWRITING: "Rewriting Resume",
  GUARDRAILS: "Running Guardrails",
  VALIDATING: "Validating Output",
  ATS_ANALYSIS: "Analyzing ATS Score",
  COMPLETED: "Completed",
};

export default function Wizard() {
  const {
    wizardStep,
    setWizardStep,
    masterResumeText,
    setMasterResumeText,
    jobDescriptionText,
    setJobDescriptionText,
    selectedResumeId,
    setSelectedResume,
    selectedJdId,
    setSelectedJD,
    activeWorkflowResponse,
    setWorkflowResponse,
    resetWizard,
  } = useUIStore();

  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadTitle] = useState("");
  const [jdTitle, setJdTitle] = useState("");
  const [jdCompany, setJdCompany] = useState("");
  const [jdLocation, setJdLocation] = useState("");
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [latexCode, setLatexCode] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  const { data: resumes } = useQuery({
    queryKey: ["resumes"],
    queryFn: listResumes,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadResumeFile(file, uploadTitle || undefined),
    onSuccess: (data) => {
      setSelectedResume(data.resume_id, uploadTitle || "Uploaded Resume");
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });

  const createJdMutation = useMutation({
    mutationFn: () =>
      createJobDescription({
        title: jdTitle || "Untitled Position",
        company: jdCompany || "Unknown Company",
        description: jobDescriptionText,
        location: jdLocation || undefined,
      }),
    onSuccess: (data) => {
      setSelectedJD(data.id, data.title);
    },
  });

  const workflowMutation = useMutation({
    mutationFn: () =>
      triggerWorkflow({
        resume_id: selectedResumeId ?? undefined,
        raw_resume_text: !selectedResumeId ? masterResumeText : undefined,
        job_description_id: selectedJdId ?? undefined,
        job_description_text: !selectedJdId ? jobDescriptionText : undefined,
      }),
    onSuccess: (data) => {
      setWorkflowId(data.workflow_id);
      setWorkflowResponse(data);
    },
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => approveWorkflow(id),
    onSuccess: (data) => setWorkflowResponse(data),
  });

  const renderMutation = useMutation({
    mutationFn: () => renderLaTeX(selectedResumeId!),
    onSuccess: (data) => setLatexCode(data.latex_code),
  });

  const pdfMutation = useMutation({
    mutationFn: (code: string) => compilePDF(code),
    onSuccess: (data) => setPdfUrl(data.pdf_url),
  });

  const { data: pollData } = useQuery({
    queryKey: ["workflow", workflowId],
    queryFn: () => getWorkflowStatus(workflowId!),
    enabled: !!workflowId && activeWorkflowResponse?.status !== "COMPLETED",
    refetchInterval: 2000,
  });

  if (pollData) {
    setWorkflowResponse(pollData);
  }

  const currentStepIndex = activeWorkflowResponse?.telemetry?.current_step
    ? WORKFLOW_STEPS.indexOf(activeWorkflowResponse.telemetry.current_step)
    : -1;

  const steps = [
    {
      label: "Resume",
      icon: FileText,
      done: !!selectedResumeId || !!masterResumeText,
    },
    {
      label: "Job Description",
      icon: Briefcase,
      done: !!selectedJdId || !!jobDescriptionText,
    },
    {
      label: "Optimize",
      icon: Play,
      done: activeWorkflowResponse?.status === "COMPLETED",
    },
    {
      label: "Results",
      icon: Eye,
      done: false,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Optimization Wizard</h1>
        <p className="mt-1 text-sm text-muted">
          Upload your resume, provide a job description, and let AI optimize it
        </p>
      </div>

      <div className="flex items-center gap-2">
        {steps.map((step, i) => {
          const Icon = step.icon;
          const isCurrent = wizardStep === i + 1;
          return (
            <div key={step.label} className="flex items-center">
              <button
                onClick={() => setWizardStep(i + 1)}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isCurrent
                    ? "bg-accent/15 text-accent"
                    : step.done
                      ? "text-success"
                      : "text-slate-500 hover:text-slate-300"
                )}
              >
                {step.done && !isCurrent ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
                {step.label}
              </button>
              {i < steps.length - 1 && (
                <ArrowRight className="mx-1 h-3 w-3 text-slate-600" />
              )}
            </div>
          );
        })}
      </div>

      <div className="rounded-xl border border-slate-800 bg-surface p-6">
        {wizardStep === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">
              Select Resume
            </h2>

            <div
              onClick={() => fileInputRef.current?.click()}
              className="flex cursor-pointer flex-col items-center rounded-lg border-2 border-dashed border-slate-700 p-8 transition-colors hover:border-accent/50 hover:bg-accent/5"
            >
              <Upload className="mb-3 h-8 w-8 text-muted" />
              <p className="text-sm text-muted">
                Click to upload a LaTeX resume (.tex)
              </p>
              {uploadMutation.isPending && (
                <Loader2 className="mt-2 h-4 w-4 animate-spin text-accent" />
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".tex,.txt"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) uploadMutation.mutate(file);
              }}
            />

            {uploadMutation.isError && (
              <p className="flex items-center gap-1 text-sm text-danger">
                <AlertCircle className="h-4 w-4" />{" "}
                {uploadMutation.error.message}
              </p>
            )}

            <div>
              <label className="mb-1 block text-sm text-muted">
                Or paste resume text directly
              </label>
              <textarea
                value={masterResumeText}
                onChange={(e) => setMasterResumeText(e.target.value)}
                rows={6}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                placeholder="Paste your resume content here…"
              />
            </div>

            {resumes && resumes.length > 0 && (
              <div>
                <p className="mb-2 text-sm font-medium text-white">
                  Previously uploaded
                </p>
                <div className="space-y-2">
                  {resumes.map((r) => (
                    <button
                      key={r.id}
                      onClick={() => setSelectedResume(r.id, r.title)}
                      className={cn(
                        "flex w-full items-center justify-between rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                        selectedResumeId === r.id
                          ? "border-accent bg-accent/10 text-accent"
                          : "border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-600"
                      )}
                    >
                      <div>
                        <p className="font-medium">{r.title}</p>
                        <p className="text-xs text-muted">
                          v{r.current_version} · {r.status}
                        </p>
                      </div>
                      {selectedResumeId === r.id && (
                        <CheckCircle className="h-4 w-4 text-accent" />
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <button
                onClick={() => setWizardStep(2)}
                disabled={!selectedResumeId && !masterResumeText}
                className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
              >
                Next <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {wizardStep === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">
              Job Description
            </h2>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm text-muted">
                  Job Title
                </label>
                <input
                  value={jdTitle}
                  onChange={(e) => setJdTitle(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                  placeholder="e.g. Senior AI Engineer"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm text-muted">
                  Company
                </label>
                <input
                  value={jdCompany}
                  onChange={(e) => setJdCompany(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                  placeholder="e.g. Acme Corp"
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm text-muted">Location</label>
              <input
                value={jdLocation}
                onChange={(e) => setJdLocation(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                placeholder="e.g. San Francisco, CA (Remote)"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm text-muted">
                Full Job Description
              </label>
              <textarea
                value={jobDescriptionText}
                onChange={(e) => setJobDescriptionText(e.target.value)}
                rows={10}
                className="w-full rounded-lg border border-slate-600 bg-slate-900 p-3 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                placeholder="Paste the full job description here…"
              />
              {jobDescriptionText.length === 0 && (
                <p className="mt-1 text-xs text-warning">
                  Job description is required to proceed
                </p>
              )}
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setWizardStep(1)}
                className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
              >
                <ArrowLeft className="h-4 w-4" /> Back
              </button>
              <button
                onClick={async () => {
                  if (!jobDescriptionText) return;
                  if (!selectedJdId) {
                    try {
                      await createJdMutation.mutateAsync();
                    } catch {
                      // proceed even if backend JD creation fails
                    }
                  }
                  setWizardStep(3);
                }}
                className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
              >
                Next <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {wizardStep === 3 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">
              Run Optimization
            </h2>

            {!workflowId ? (
              <div className="space-y-4">
                <div className="rounded-lg bg-slate-900 p-4 text-sm">
                  <p className="text-muted">
                    <span className="font-medium text-white">Resume:</span>{" "}
                    {selectedResumeId ? `Selected (${selectedResumeId.slice(0, 8)}…)` : "Inline text"}
                  </p>
                  <p className="text-muted">
                    <span className="font-medium text-white">Job Description:</span>{" "}
                    {jdTitle || "Untitled Position"}
                    {jdCompany ? ` at ${jdCompany}` : ""}
                  </p>
                </div>

                <div className="flex justify-between">
                  <button
                    onClick={() => setWizardStep(2)}
                    className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
                  >
                    <ArrowLeft className="h-4 w-4" /> Back
                  </button>
                  <button
                    onClick={() => workflowMutation.mutate()}
                    disabled={workflowMutation.isPending}
                    className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {workflowMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                    Start Optimization
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="space-y-2">
                  {WORKFLOW_STEPS.map((step, i) => {
                    const isCompleted = i < currentStepIndex;
                    const isCurrent = i === currentStepIndex;
                    const isPending = i > currentStepIndex;
                    return (
                      <div
                        key={step}
                        className={cn(
                          "flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm",
                          isCurrent && "bg-accent/10 text-accent",
                          isCompleted && "text-success",
                          isPending && "text-slate-600"
                        )}
                      >
                        {isCompleted ? (
                          <CheckCircle className="h-4 w-4 shrink-0" />
                        ) : isCurrent ? (
                          <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
                        ) : (
                          <div className="h-4 w-4 shrink-0 rounded-full border border-slate-600" />
                        )}
                        {STEP_LABELS[step] || step}
                      </div>
                    );
                  })}
                </div>

                {workflowMutation.isError && (
                  <p className="flex items-center gap-1 text-sm text-danger">
                    <AlertCircle className="h-4 w-4" />{" "}
                    {workflowMutation.error.message}
                  </p>
                )}

                {activeWorkflowResponse?.status === "COMPLETED" && (
                  <div className="space-y-3 rounded-lg bg-success/10 p-4">
                    <p className="flex items-center gap-2 text-sm font-medium text-success">
                      <CheckCircle className="h-4 w-4" /> Workflow completed
                      successfully
                    </p>
                    {activeWorkflowResponse.guardrail_report && (
                      <p className="text-xs text-muted">
                        Guardrail:{" "}
                        {activeWorkflowResponse.guardrail_report.status} ·{" "}
                        {activeWorkflowResponse.guardrail_report.violations.length} violations
                      </p>
                    )}
                    {activeWorkflowResponse.ats_report && (
                      <p className="text-xs text-muted">
                        ATS Score:{" "}
                        {activeWorkflowResponse.ats_report.overall_score.toFixed(1)}
                      </p>
                    )}
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          if (selectedResumeId) renderMutation.mutate();
                          setWizardStep(4);
                        }}
                        className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
                      >
                        View Results <ArrowRight className="h-4 w-4" />
                      </button>
                      {activeWorkflowResponse.guardrail_report?.status ===
                        "rejected" && (
                        <button
                          onClick={() =>
                            approveMutation.mutate(workflowId)
                          }
                          disabled={approveMutation.isPending}
                          className="flex items-center gap-2 rounded-lg border border-warning px-4 py-2 text-sm font-medium text-warning transition-colors hover:bg-warning/10"
                        >
                          Force Approve
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {wizardStep === 4 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white">
              Optimization Results
            </h2>

            {activeWorkflowResponse?.rewritten_resume && (
              <div className="space-y-3">
                {activeWorkflowResponse.rewritten_resume.summary && (
                  <div className="rounded-lg bg-slate-900 p-4">
                    <p className="mb-1 text-xs font-medium uppercase text-muted">
                      Summary
                    </p>
                    <p className="text-sm text-slate-300">
                      {activeWorkflowResponse.rewritten_resume.summary}
                    </p>
                  </div>
                )}

                {activeWorkflowResponse.rewritten_resume.experience?.map(
                  (exp, i) => (
                    <div key={i} className="rounded-lg bg-slate-900 p-4">
                      <p className="text-sm font-medium text-white">
                        {exp.role} — {exp.company}
                      </p>
                      <ul className="mt-2 space-y-1">
                        {exp.bullets.map((b, j) => (
                          <li
                            key={j}
                            className="text-xs text-slate-400"
                          >
                            • {b}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )
                )}
              </div>
            )}

            {activeWorkflowResponse?.ats_report && (
              <div className="rounded-lg bg-slate-900 p-4">
                <p className="mb-3 text-xs font-medium uppercase text-muted">
                  ATS Report
                </p>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <div>
                    <p className="text-2xl font-bold text-accent">
                      {activeWorkflowResponse.ats_report.overall_score.toFixed(
                        0
                      )}
                    </p>
                    <p className="text-xs text-muted">Overall</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-success">
                      {activeWorkflowResponse.ats_report.keyword_score.toFixed(
                        0
                      )}
                    </p>
                    <p className="text-xs text-muted">Keywords</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-accent">
                      {activeWorkflowResponse.ats_report.semantic_score.toFixed(
                        0
                      )}
                    </p>
                    <p className="text-xs text-muted">Semantic</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-success">
                      {activeWorkflowResponse.ats_report.skills_score.toFixed(
                        0
                      )}
                    </p>
                    <p className="text-xs text-muted">Skills</p>
                  </div>
                </div>

                {activeWorkflowResponse.ats_report.missing_keywords.length >
                  0 && (
                  <div className="mt-3">
                    <p className="mb-1 text-xs text-muted">Missing Keywords</p>
                    <div className="flex flex-wrap gap-1">
                      {activeWorkflowResponse.ats_report.missing_keywords.map(
                        (kw, i) => (
                          <span
                            key={i}
                            className="rounded bg-warning/15 px-2 py-0.5 text-xs text-warning"
                          >
                            {kw}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                )}

                {activeWorkflowResponse.ats_report.recommendations.length >
                  0 && (
                  <div className="mt-3">
                    <p className="mb-1 text-xs text-muted">Recommendations</p>
                    <ul className="space-y-1">
                      {activeWorkflowResponse.ats_report.recommendations.map(
                        (rec, i) => (
                          <li key={i} className="text-xs text-slate-400">
                            • {rec}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {activeWorkflowResponse?.guardrail_report && (
              <div className="rounded-lg bg-slate-900 p-4">
                <p className="mb-3 text-xs font-medium uppercase text-muted">
                  Guardrail Report
                </p>
                <p className="text-sm text-slate-300">
                  Status:{" "}
                  <span
                    className={
                      activeWorkflowResponse.guardrail_report.status ===
                      "approved"
                        ? "text-success"
                        : "text-warning"
                    }
                  >
                    {activeWorkflowResponse.guardrail_report.status}
                  </span>
                </p>
                {activeWorkflowResponse.guardrail_report.violations.length >
                  0 && (
                  <div className="mt-2 space-y-1">
                    {activeWorkflowResponse.guardrail_report.violations.map(
                      (v, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 text-xs"
                        >
                          <span
                            className={cn(
                              "mt-0.5 rounded px-1.5 py-0.5 font-medium",
                              v.severity === "critical" &&
                                "bg-danger/15 text-danger",
                              v.severity === "high" &&
                                "bg-danger/15 text-danger",
                              v.severity === "medium" &&
                                "bg-warning/15 text-warning",
                              v.severity === "low" &&
                                "bg-muted/15 text-muted"
                            )}
                          >
                            {v.severity}
                          </span>
                          <span className="text-slate-400">{v.message}</span>
                        </div>
                      )
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-2">
              <button
                onClick={() => {
                  if (selectedResumeId) renderMutation.mutate();
                }}
                disabled={!selectedResumeId || renderMutation.isPending}
                className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {renderMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileText className="h-4 w-4" />
                )}
                Generate LaTeX
              </button>

              {latexCode && (
                <button
                  onClick={() => pdfMutation.mutate(latexCode)}
                  disabled={pdfMutation.isPending}
                  className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {pdfMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                  Compile PDF
                </button>
              )}

              <button
                onClick={resetWizard}
                className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
              >
                <RefreshCw className="h-4 w-4" /> New Optimization
              </button>
            </div>

            {latexCode && (
              <div className="rounded-lg bg-slate-900 p-4">
                <p className="mb-2 text-xs font-medium uppercase text-muted">
                  Generated LaTeX
                </p>
                <pre className="max-h-64 overflow-auto rounded border border-slate-700 bg-slate-950 p-3 text-xs text-slate-300">
                  {latexCode}
                </pre>
              </div>
            )}

            {pdfUrl && (
              <div className="rounded-lg bg-slate-900 p-4">
                <p className="mb-2 text-xs font-medium uppercase text-muted">
                  Compiled PDF
                </p>
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-accent hover:underline"
                >
                  <Download className="h-4 w-4" /> Download PDF
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
