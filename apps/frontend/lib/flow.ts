import {
  Upload, FileSearch, Briefcase, CheckCheck, Cpu, Flag,
  type LucideIcon,
} from "lucide-react";
import type { FlowStep } from "./store";

export interface FlowStepMeta {
  id: FlowStep;
  label: string;
  description: string;
  icon: LucideIcon;
}

export const FLOW_STEPS: FlowStepMeta[] = [
  { id: "upload-resume", label: "Upload Resume", description: "Upload your resume file", icon: Upload },
  { id: "resume-parsed", label: "Resume Parsed", description: "Structured data extracted", icon: FileSearch },
  { id: "input-jd", label: "Job Description", description: "Add target job description", icon: Briefcase },
  { id: "jd-ready", label: "JD Ready", description: "Requirements & skills extracted", icon: CheckCheck },
  { id: "optimizing", label: "Optimizing", description: "Running optimization pipeline", icon: Cpu },
  { id: "done", label: "Results", description: "ATS analysis & rewritten resume", icon: Flag },
];

export const FLOW_ORDER: FlowStep[] = FLOW_STEPS.map((s) => s.id);

export const FLOW_LABELS: Record<FlowStep, string> = Object.fromEntries(
  FLOW_STEPS.map((s) => [s.id, s.label]),
) as Record<FlowStep, string>;
