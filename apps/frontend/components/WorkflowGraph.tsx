"use client";

import { CheckCircle2, Clock, PlayCircle } from "lucide-react";

interface WorkflowGraphProps {
  currentStep?: string;
  stepHistory?: string[];
}

export function WorkflowGraph({ currentStep = "IDLE", stepHistory = [] }: WorkflowGraphProps) {
  const steps = [
    { id: "PARSING", label: "Parse Resume", desc: "Canonical model conversion" },
    { id: "JD_ANALYSIS", label: "JD Analysis", desc: "qwen3:8b requirement extraction" },
    { id: "RETRIEVAL", label: "Vector Search", desc: "Qdrant nomic-embed-text RAG" },
    { id: "PLANNING", label: "Planner Agent", desc: "Section rewrite strategy" },
    { id: "REWRITING", label: "Rewriter Agent", desc: "Truth-grounded LaTeX rewrites" },
    { id: "GUARDRAILS", label: "Guardrails Safety", desc: "9 security validator pipeline" },
    { id: "VALIDATING", label: "Schema Validation", desc: "LaTeX AST verification" },
    { id: "ATS_ANALYSIS", label: "ATS Advisor", desc: "Keyword density & scoring" },
  ];

  return (
    <div className="space-y-3">
      <div className="text-xs font-semibold text-zinc-300 font-mono flex items-center justify-between">
        <span>LangGraph State Machine Pipeline Execution</span>
        <span className="text-zinc-500">Current Step: {currentStep}</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {steps.map((s, idx) => {
          const isDone = stepHistory.includes(s.id);
          const isCurrent = currentStep === s.id;

          return (
            <div
              key={s.id}
              className={`p-3 rounded border text-xs font-mono transition-all ${
                isCurrent
                  ? "bg-zinc-800 border-zinc-500 text-zinc-100 shadow-md ring-1 ring-zinc-400"
                  : isDone
                  ? "bg-zinc-900/90 border-emerald-800/80 text-zinc-300"
                  : "bg-zinc-950 border-zinc-800/60 text-zinc-500"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-zinc-500">Step 0{idx + 1}</span>
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : isCurrent ? (
                  <PlayCircle className="w-3.5 h-3.5 text-zinc-200 animate-pulse" />
                ) : (
                  <Clock className="w-3.5 h-3.5 text-zinc-600" />
                )}
              </div>
              <div className="font-bold text-zinc-200">{s.label}</div>
              <div className="text-[10px] text-zinc-400 truncate mt-0.5">{s.desc}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
