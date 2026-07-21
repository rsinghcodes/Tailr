"use client";

import { useUIStore } from "@/lib/store";
import { Navbar } from "@/components/Navbar";
import { HeroStats } from "@/components/HeroStats";
import { WorkflowWizard } from "@/components/WorkflowWizard";
import { ResumeManager } from "@/components/ResumeManager";
import { JobDescriptionManager } from "@/components/JobDescriptionManager";
import { ResultsView } from "@/components/ResultsView";
import { AuditLogTable } from "@/components/AuditLogTable";
import { Cpu, ArrowRight, ShieldCheck, FileCheck, FileText } from "lucide-react";

export default function Home() {
  const { activeTab, setActiveTab, setWizardStep } = useUIStore();

  return (
    <div className="min-h-screen flex flex-col justify-between bg-zinc-950 text-zinc-100 font-sans">
      <div>
        <Navbar />

        <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
          {/* Dashboard View */}
          {activeTab === "dashboard" && (
            <div className="space-y-8">
              {/* Minimal Hero Section */}
              <div className="min-panel p-8 space-y-4">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs font-mono">
                  <span>LlamaIndex RAG + LangGraph Workflows + Guardrails AI Safety</span>
                </div>

                <div className="space-y-2 max-w-3xl">
                  <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-zinc-100">
                    Build one master resume. Tailor it infinitely.
                  </h1>
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    Tailr optimizes LaTeX resumes for specific job descriptions using Multi-Agent AI. Grounded in truth, validated by deterministic guardrails, and structured for maximum ATS performance.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3 pt-2">
                  <button
                    onClick={() => {
                      setWizardStep(1);
                      setActiveTab("wizard");
                    }}
                    className="min-button min-button-primary"
                  >
                    <Cpu className="w-4 h-4" /> Start Tailoring Wizard <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setActiveTab("resumes")}
                    className="min-button min-button-secondary"
                  >
                    <FileText className="w-4 h-4" /> Manage Resumes
                  </button>
                </div>
              </div>

              {/* Stat Cards */}
              <HeroStats />

              {/* Feature Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="min-card p-5 space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold text-zinc-200">
                    <FileCheck className="w-4 h-4 text-zinc-400" /> Fact Grounding
                  </div>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    The Guardrails Engine compares rewrites against the Canonical Resume Model to eliminate hallucinations or unverified claims.
                  </p>
                </div>

                <div className="min-card p-5 space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold text-zinc-200">
                    <Cpu className="w-4 h-4 text-zinc-400" /> LangGraph Multi-Agent
                  </div>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Event-driven agent orchestration coordinating JD analysis, context retrieval, planning, rewriting, and validation.
                  </p>
                </div>

                <div className="min-card p-5 space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold text-zinc-200">
                    <ShieldCheck className="w-4 h-4 text-zinc-400" /> LaTeX Compiler
                  </div>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Raw LaTeX is rendered deterministically without direct LLM LaTeX code editing, ensuring compilation safety.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Tailoring Wizard View */}
          {activeTab === "wizard" && <WorkflowWizard />}

          {/* Master Resumes Management View */}
          {activeTab === "resumes" && <ResumeManager />}

          {/* Job Descriptions Management View */}
          {activeTab === "job_descriptions" && <JobDescriptionManager />}

          {/* Results View */}
          {activeTab === "results" && <ResultsView />}

          {/* Guardrails Audit View */}
          {activeTab === "audit" && <AuditLogTable />}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-4 text-center text-xs text-zinc-500 font-mono">
        Tailr v1.0 — FastAPI • Next.js 16 • LlamaIndex • LangGraph • Guardrails AI Engine
      </footer>
    </div>
  );
}
