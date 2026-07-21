"use client";

import { useUIStore } from "@/lib/store";
import { Navbar } from "@/components/Navbar";
import { HeroStats } from "@/components/HeroStats";
import { WorkflowWizard } from "@/components/WorkflowWizard";
import { ResultsView } from "@/components/ResultsView";
import { AuditLogTable } from "@/components/AuditLogTable";
import { Cpu, Sparkles, ArrowRight, ShieldCheck, FileCheck } from "lucide-react";

export default function Home() {
  const { activeTab, setActiveTab, setWizardStep } = useUIStore();

  return (
    <div className="min-h-screen flex flex-col justify-between">
      <div>
        <Navbar />

        <main className="max-w-7xl mx-auto px-6 py-8 space-y-10">
          {/* Dashboard View */}
          {activeTab === "dashboard" && (
            <div className="space-y-10">
              {/* Hero Banner */}
              <div className="glass-panel rounded-3xl p-10 border border-slate-800 space-y-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-sky-500/10 to-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold">
                  <Sparkles className="w-3.5 h-3.5" /> Multi-Agent AI + LlamaIndex RAG + LangGraph Engine
                </div>

                <div className="space-y-3 max-w-3xl">
                  <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                    Build one master resume. <br />
                    <span className="gradient-text">Tailor it infinitely.</span>
                  </h1>
                  <p className="text-base text-slate-300 leading-relaxed">
                    Tailr uses Multi-Agent AI and RAG to tailor resumes for specific job descriptions. Grounded in truth, validated by mandatory guardrails, and deterministically rendered to compilable LaTeX.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-4 pt-2">
                  <button
                    onClick={() => {
                      setWizardStep(1);
                      setActiveTab("wizard");
                    }}
                    className="flex items-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 via-indigo-600 to-purple-600 text-white font-bold shadow-xl shadow-sky-500/20 hover:opacity-95 transition-all"
                  >
                    <Cpu className="w-5 h-5" /> Start Tailoring Wizard <ArrowRight className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setActiveTab("audit")}
                    className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-200 font-medium hover:bg-slate-700 transition-all"
                  >
                    <ShieldCheck className="w-4 h-4 text-emerald-400" /> View Guardrails Audit
                  </button>
                </div>
              </div>

              {/* Stat Cards */}
              <HeroStats />

              {/* Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
                  <div className="p-3 rounded-xl bg-sky-500/10 text-sky-400 w-fit">
                    <FileCheck className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white">Fact Grounding</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Tailr never fabricates experience. The Guardrails Engine rejects unverified employers, projects, metrics, or dates.
                  </p>
                </div>

                <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
                  <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 w-fit">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white">LangGraph Workflows</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Stateful event-driven multi-agent orchestration coordinating JD analysis, context retrieval, planning, and rewriting.
                  </p>
                </div>

                <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
                  <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 w-fit">
                    <ShieldCheck className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white">LaTeX Safety</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    LLMs never edit raw LaTeX directly. Output is validated against command injection and rendered deterministically.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Tailoring Wizard View */}
          {activeTab === "wizard" && <WorkflowWizard />}

          {/* Results View */}
          {activeTab === "results" && <ResultsView />}

          {/* Guardrails Audit View */}
          {activeTab === "audit" && <AuditLogTable />}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 font-mono">
        Built with FastAPI, Next.js 16, LlamaIndex, LangGraph, Qdrant, and Guardrails AI Safety Engine.
      </footer>
    </div>
  );
}
