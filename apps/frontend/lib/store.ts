import { create } from "zustand";
import type { WorkflowResponse, ResumeListItem, JobDescriptionData } from "./api";

export type FlowStep =
  | "upload-resume"
  | "resume-parsed"
  | "input-jd"
  | "jd-parsed"
  | "optimizing"
  | "done";

export interface StreamStepState {
  step: string;
  step_index: number;
  total_steps: number;
  label: string;
  description: string;
  status: "pending" | "running" | "done";
}

interface UIState {
  flowStep: FlowStep;
  setFlowStep: (step: FlowStep) => void;

  selectedResumeId: string | null;
  setSelectedResumeId: (id: string | null) => void;
  selectedJdId: string | null;
  setSelectedJdId: (id: string | null) => void;

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
  { step: "retrieve_context", label: "Context Retrieval", description: "Searching knowledge base for relevant context" },
  { step: "plan", label: "Rewrite Planning", description: "Generating optimization strategy" },
  { step: "rewrite", label: "Resume Rewriting", description: "Applying optimizations to resume content" },
  { step: "guardrails", label: "Guardrail Check", description: "Running safety and quality checks" },
  { step: "validation", label: "Validation", description: "Validating business rules and completeness" },
  { step: "ats_analysis", label: "ATS Analysis", description: "Scoring resume against applicant tracking system" },
  { step: "render", label: "Rendering", description: "Generating final output" },
];

export const useUIStore = create<UIState>((set) => ({
  flowStep: "upload-resume",
  setFlowStep: (step) => set({ flowStep: step }),

  selectedResumeId: null,
  setSelectedResumeId: (id) => set({ selectedResumeId: id }),
  selectedJdId: null,
  setSelectedJdId: (id) => set({ selectedJdId: id }),

  activeWorkflowResponse: null,
  setWorkflowResponse: (response) => set({ activeWorkflowResponse: response }),

  savedResumes: [],
  setSavedResumes: (resumes) => set({ savedResumes: resumes }),

  savedJds: [],
  setSavedJds: (jds) => set({ savedJds: jds }),

  streamSteps: STEPS_MAP.map((s, i) => ({ ...s, step_index: i, total_steps: STEPS_MAP.length, status: "pending" as const })),
  setStreamSteps: (steps) => set((state) => ({
    streamSteps: typeof steps === "function" ? steps(state.streamSteps) : steps,
  })),
  streamWorkflowId: null,
  setStreamWorkflowId: (id) => set({ streamWorkflowId: id }),
  isStreaming: false,
  setIsStreaming: (v) => set({ isStreaming: v }),
}));
