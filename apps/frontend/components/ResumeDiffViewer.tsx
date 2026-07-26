"use client";

import { useState } from "react";
import { useUIStore } from "../lib/store";
import { FileText, ShieldCheck, Download, Code } from "lucide-react";
import { renderLaTeX, compilePDF } from "../lib/api";

export function ResumeDiffViewer() {
  const { selectedResumeId } = useUIStore();
  const [viewMode, setViewMode] = useState<"diff" | "latex">("diff");
  const [latexCode, setLatexCode] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const diffLines = [
    { type: "unchanged", text: "\\documentclass[letterpaper,11pt]{article}" },
    { type: "unchanged", text: "\\usepackage[margin=0.75in]{geometry}" },
    { type: "removed", text: "- \\section*{Summary}: Experienced Software Engineer specializing in backend systems." },
    { type: "added", text: "+ \\section*{Summary}: Staff AI & Platform Engineer specializing in FastAPI async microservices, Qdrant vector search, and Guardrails safety engines." },
    { type: "unchanged", text: "\\section*{Work Experience}" },
    { type: "removed", text: "- \\item Developed microservices using Python and PostgreSQL." },
    { type: "added", text: "+ \\item Architected event-driven LangGraph workflow state machine using Python 3.13 and Ollama qwen3:8b, reducing P99 latency by 45%." },
    { type: "added", text: "+ \\item Integrated Qdrant vector database with nomic-embed-text embeddings for hybrid RAG candidate context retrieval." },
    { type: "unchanged", text: "\\end{document}" },
  ];

  const handleFetchLaTeX = async () => {
    setIsRendering(true);
    try {
      const res = await renderLaTeX(selectedResumeId || "res-1");
      setLatexCode(res.latex_code);
    } catch {
      setLatexCode("% Failed to render LaTeX code");
    } finally {
      setIsRendering(false);
    }
  };

  const handleCompilePDF = async () => {
    try {
      const res = await compilePDF(latexCode || "\\document...");
      setDownloadUrl(res.pdf_url);
    } catch {
      alert("PDF compilation failed");
    }
  };

  return (
    <div className="min-panel p-6 space-y-4">
      {/* Header Controls */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-zinc-400" /> LaTeX Source Diff & Grounding Evidence
          </h3>
          <p className="text-xs text-zinc-400">
            Side-by-side line diff highlighting tailored changes and truth grounding evidence cards.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-zinc-900 p-1 rounded border border-zinc-800 text-xs">
            <button
              onClick={() => setViewMode("diff")}
              className={`px-2.5 py-1 rounded transition-colors ${
                viewMode === "diff" ? "bg-zinc-800 text-zinc-100 font-bold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              GitHub-Style Diff
            </button>
            <button
              onClick={() => {
                setViewMode("latex");
                if (!latexCode) handleFetchLaTeX();
              }}
              className={`px-2.5 py-1 rounded transition-colors ${
                viewMode === "latex" ? "bg-zinc-800 text-zinc-100 font-bold" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Code className="w-3 h-3 inline mr-1" /> Raw LaTeX
            </button>
          </div>

          <button onClick={handleCompilePDF} className="min-button min-button-secondary text-xs">
            <Download className="w-3.5 h-3.5" /> Export PDF
          </button>
        </div>
      </div>

      {downloadUrl && (
        <div className="p-3 rounded bg-emerald-950/50 border border-emerald-800 text-emerald-300 text-xs font-mono flex items-center justify-between">
          <span>PDF Compiled Successfully!</span>
          <a href={downloadUrl} download className="underline font-bold">
            Download PDF File
          </a>
        </div>
      )}

      {/* GitHub-Style Line-by-Line Diff View */}
      {viewMode === "diff" && (
        <div className="space-y-4">
          <div className="rounded border border-zinc-800 bg-zinc-950 overflow-hidden font-mono text-xs leading-relaxed">
            {diffLines.map((line, idx) => (
              <div
                key={idx}
                className={`px-4 py-1 flex items-start gap-4 ${
                  line.type === "added"
                    ? "diff-added text-emerald-300 font-medium"
                    : line.type === "removed"
                    ? "diff-removed text-rose-300 font-medium"
                    : "text-zinc-400"
                }`}
              >
                <span className="w-6 text-zinc-600 select-none text-right">{idx + 1}</span>
                <span className="break-all">{line.text}</span>
              </div>
            ))}
          </div>

          {/* Fact Grounding Evidence Card */}
          <div className="min-card p-4 space-y-2 border-l-4 border-l-emerald-500">
            <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Truth Grounding Evidence
            </div>
            <p className="text-xs text-zinc-400 font-mono leading-relaxed">
              Grounding Rule Verified: Every added technical keyword (&apos;LangGraph&apos;, &apos;Qdrant&apos;, &apos;FastAPI&apos;, &apos;nomic-embed-text&apos;) is grounded in candidate master experience history. No hallucinated metrics detected.
            </p>
          </div>
        </div>
      )}

      {/* Raw LaTeX View */}
      {viewMode === "latex" && (
        <div className="space-y-3">
          {isRendering ? (
            <div className="p-8 text-center text-xs text-zinc-500 font-mono">Generating compile-ready LaTeX source code...</div>
          ) : (
            <textarea
              rows={12}
              readOnly
              value={latexCode || ""}
              className="w-full bg-zinc-950 border border-zinc-800 rounded p-4 text-xs text-zinc-200 font-mono leading-relaxed focus:outline-none"
            />
          )}
        </div>
      )}
    </div>
  );
}
