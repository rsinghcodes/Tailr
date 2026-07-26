"use client";

import { useEffect, useState } from "react";
import { useUIStore, TabType } from "../lib/store";
import { Search, LayoutDashboard, Cpu, FileText, Briefcase, History, X } from "lucide-react";

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const { setActiveTab, setWizardStep } = useUIStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (!isOpen) return null;

  const actions: { id: string; label: string; tab: TabType; step?: number; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "dash", label: "Go to Dashboard", tab: "dashboard", icon: LayoutDashboard },
    { id: "wizard", label: "Start Resume Tailoring Wizard", tab: "wizard", step: 1, icon: Cpu },
    { id: "resumes", label: "Manage Master Resumes", tab: "resumes", icon: FileText },
    { id: "jds", label: "Manage Job Descriptions", tab: "job_descriptions", icon: Briefcase },
    { id: "results", label: "View Tailored Resume Results & LaTeX Diff", tab: "results", icon: FileText },
    { id: "audit", label: "View Guardrail Security Audit Logs", tab: "audit", icon: History },
  ];

  const filtered = actions.filter((a) => a.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-start justify-center pt-24 px-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg shadow-2xl w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
        <div className="flex items-center px-4 border-b border-zinc-800">
          <Search className="w-4 h-4 text-zinc-400 mr-2" />
          <input
            type="text"
            placeholder="Type a command or search tabs..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent py-3 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none"
          />
          <button onClick={() => setIsOpen(false)} className="text-zinc-500 hover:text-zinc-300">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-2 max-h-72 overflow-y-auto space-y-1">
          {filtered.length === 0 ? (
            <div className="p-4 text-center text-xs text-zinc-500 font-mono">No matching actions found.</div>
          ) : (
            filtered.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.id}
                  onClick={() => {
                    if (action.step) setWizardStep(action.step);
                    setActiveTab(action.tab);
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded text-xs text-left text-zinc-300 hover:bg-zinc-800 hover:text-zinc-100 transition-colors font-medium"
                >
                  <Icon className="w-4 h-4 text-zinc-400" />
                  <span>{action.label}</span>
                </button>
              );
            })
          )}
        </div>

        <div className="px-4 py-2 border-t border-zinc-800 text-[10px] text-zinc-500 font-mono flex items-center justify-between">
          <span>Press ESC to close</span>
          <span>Navigation Shortcuts</span>
        </div>
      </div>
    </div>
  );
}
