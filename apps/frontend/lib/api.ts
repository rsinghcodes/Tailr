const API_BASE = "http://localhost:8000/api/v1";

// ──────────────────────────────────────────
// Types
// ──────────────────────────────────────────

export interface ResumeListItem {
  id: string;
  title: string;
  current_version: number;
  status: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResumeVersionItem {
  version_id: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeUploadResponse {
  resume_id: string;
  status: string;
}

export interface JobRequirements {
  title: string | null;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  soft_skills: string[];
  keywords: string[];
  experience_level: string | null;
}

export interface JobDescriptionData {
  id: string;
  title: string;
  company: string | null;
  location: string | null;
  employment_type: string | null;
  description: string;
  parsed_requirements?: JobRequirements;
}

export interface WorkflowResponse {
  workflow_id: string;
  status: string;
  telemetry: Record<string, unknown>;
  guardrail_report: Record<string, unknown> | null;
  ats_report: Record<string, unknown> | null;
  rewritten_resume: Record<string, unknown> | null;
}

export interface WorkflowStreamEvent {
  event: "workflow_start" | "step_start" | "step_complete" | "workflow_complete" | "error" | "done";
  data: Record<string, unknown>;
}

export interface SystemHealthResponse {
  status: string;
  services: Record<string, { status: string; online: boolean; latency_ms: number | null; details: Record<string, unknown> }>;
}

export interface AnalyticsDashboard {
  total_optimizations: number;
  average_ats_improvement: number;
  guardrail_pass_rate: number;
  total_resumes: number;
}

export interface GuardrailEventItem {
  id: string;
  workflow_id: string;
  validator_name: string;
  severity: string;
  violation_code: string | null;
  repaired: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface GuardrailEventsResponse {
  items: GuardrailEventItem[];
}

// ──────────────────────────────────────────
// API Client
// ──────────────────────────────────────────

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message || body?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ─── Health ──────────────────────────────

export async function checkHealth(): Promise<SystemHealthResponse> {
  return request<SystemHealthResponse>("/health");
}

// ─── Analytics ───────────────────────────

export async function getAnalyticsDashboard(): Promise<AnalyticsDashboard> {
  return request<AnalyticsDashboard>("/analytics");
}

// ─── Resumes ─────────────────────────────

export async function uploadResumeFile(file: File, title?: string): Promise<ResumeUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);
  const res = await fetch(`${API_BASE}/resumes`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message || body?.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function listResumes(): Promise<ResumeListItem[]> {
  const res = await request<{ success: boolean; data: ResumeListItem[] }>("/resumes");
  return res.data;
}

export async function deleteResume(id: string): Promise<void> {
  await request(`/resumes/${id}`, { method: "DELETE" });
}

export async function getResumeVersions(id: string): Promise<ResumeVersionItem[]> {
  const res = await request<{ success: boolean; data: ResumeVersionItem[] }>(`/resumes/${id}/versions`);
  return res.data;
}

// ─── Job Descriptions ────────────────────

export async function createJobDescription(data: {
  title: string;
  company: string;
  description: string;
}): Promise<JobDescriptionData> {
  const res = await request<{ success: boolean; data: JobDescriptionData }>("/job-descriptions", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return res.data;
}

export async function listJobDescriptions(): Promise<JobDescriptionData[]> {
  const res = await request<{ success: boolean; data: JobDescriptionData[] }>("/job-descriptions");
  return res.data;
}

export async function uploadJobDescription(
  file: File,
  title?: string,
  company?: string
): Promise<JobDescriptionData> {
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);
  if (company) form.append("company", company);
  const res = await fetch(`${API_BASE}/job-descriptions/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message || body?.detail || `HTTP ${res.status}`);
  }
  const json = await res.json();
  return json.data;
}

export async function deleteJobDescription(id: string): Promise<void> {
  await request(`/job-descriptions/${id}`, { method: "DELETE" });
}

export async function getJobDescription(id: string): Promise<JobDescriptionData> {
  const res = await request<{ success: boolean; data: JobDescriptionData }>(`/job-descriptions/${id}`);
  return res.data;
}

// ─── Workflows ───────────────────────────

export async function triggerWorkflow(requestBody: {
  raw_resume_text?: string;
  job_description_text?: string;
  resume_id?: string;
  job_description_id?: string;
}): Promise<WorkflowResponse> {
  return request<WorkflowResponse>("/workflows", {
    method: "POST",
    body: JSON.stringify(requestBody),
  });
}

export async function* streamWorkflow(requestBody: {
  raw_resume_text?: string;
  job_description_text?: string;
  resume_id?: string;
  job_description_id?: string;
}): AsyncGenerator<WorkflowStreamEvent> {
  const res = await fetch(`${API_BASE}/workflows/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  if (!res.ok) throw new Error(`SSE request failed: ${res.status}`);
  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        const data = JSON.parse(line.slice(6));
        yield { event: currentEvent as WorkflowStreamEvent["event"], data };
        if (currentEvent === "done" || currentEvent === "workflow_complete") return;
      }
    }
  }
}

// ─── Guardrails ──────────────────────────

export async function fetchGuardrailEvents(workflowId: string): Promise<GuardrailEventsResponse> {
  return request<GuardrailEventsResponse>(`/guardrails/events?workflow_id=${encodeURIComponent(workflowId)}`);
}