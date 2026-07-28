import { create } from "zustand";
import type { WorkflowResponse, ResumeListItem, JobDescriptionData } from "./api";

export type TabType = "dashboard" | "wizard" | "resumes" | "job_descriptions" | "results" | "audit";

export interface StreamStepState {
  step: string;
  step_index: number;
  total_steps: number;
  label: string;
  description: string;
  status: "pending" | "running" | "done";
}

interface UIState {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;

  wizardStep: number;
  setWizardStep: (step: number) => void;

  masterResumeText: string;
  setMasterResumeText: (text: string) => void;

  jobDescriptionText: string;
  setJobDescriptionText: (text: string) => void;

  activeWorkflowResponse: WorkflowResponse | null;
  setWorkflowResponse: (response: WorkflowResponse) => void;

  savedResumes: ResumeListItem[];
  setSavedResumes: (resumes: ResumeListItem[]) => void;

  savedJds: JobDescriptionData[];
  setSavedJds: (jds: JobDescriptionData[]) => void;

  streamSteps: StreamStepState[];
  setStreamSteps: (steps: StreamStepState[] | ((prev: StreamStepState[]) => StreamStepState[])) => void;
  streamWorkflowId: string | null;
  setStreamWorkflowId: (id: string | null) => void;
  isStreaming: boolean;
  setIsStreaming: (v: boolean) => void;
}

const STEPS_MAP: { step: string; label: string; description: string }[] = [
  { step: "parse_resume", label: "Resume Parsing", description: "Extracting structured data from resume" },
  { step: "parse_jd", label: "Job Description Analysis", description: "Analyzing job requirements" },
  { step: "retrieve_context", label: "Context Retrieval", description: "Searching knowledge base for relevant context" },
  { step: "plan", label: "Rewrite Planning", description: "Generating optimization strategy" },
  { step: "rewrite", label: "Resume Rewriting", description: "Applying optimizations to resume content" },
  { step: "guardrails", label: "Guardrail Check", description: "Running safety and quality checks" },
  { step: "validation", label: "Validation", description: "Validating business rules and completeness" },
  { step: "ats_analysis", label: "ATS Analysis", description: "Scoring resume against applicant tracking system" },
  { step: "render", label: "Rendering", description: "Generating final output" },
];

export const useUIStore = create<UIState>((set) => ({
  activeTab: "dashboard",
  setActiveTab: (tab) => set({ activeTab: tab }),

  wizardStep: 1,
  setWizardStep: (step) => set({ wizardStep: step }),

  masterResumeText: "",
  setMasterResumeText: (text) => set({ masterResumeText: text }),

  jobDescriptionText: "",
  setJobDescriptionText: (text) => set({ jobDescriptionText: text }),

  activeWorkflowResponse: null,
  setWorkflowResponse: (response) => set({ activeWorkflowResponse: response }),

  savedResumes: [],
  setSavedResumes: (resumes) => set({ savedResumes: resumes }),

  savedJds: [],
  setSavedJds: (jds) => set({ savedJds: jds }),

  streamSteps: STEPS_MAP.map((s) => ({ ...s, step_index: 0, total_steps: 9, status: "pending" as const })),
  setStreamSteps: (steps) => set((state) => ({
    streamSteps: typeof steps === "function" ? steps(state.streamSteps) : steps,
  })),
  streamWorkflowId: null,
  setStreamWorkflowId: (id) => set({ streamWorkflowId: id }),
  isStreaming: false,
  setIsStreaming: (v) => set({ isStreaming: v }),
}));