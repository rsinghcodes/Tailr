"use client";

import { useUIStore, TabType } from "@/lib/store";
import { LayoutDashboard, Cpu, FileText, Briefcase, ShieldCheck, History } from "lucide-react";

export function Navbar() {
  const { activeTab, setActiveTab } = useUIStore();

  const navItems: { id: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "wizard", label: "Tailor Resume", icon: Cpu },
    { id: "resumes", label: "Resumes", icon: FileText },
    { id: "job_descriptions", label: "Job Descriptions", icon: Briefcase },
    { id: "results", label: "Results", icon: FileText },
    { id: "audit", label: "Audit Log", icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveTab("dashboard")}>
          <div className="w-7 h-7 rounded-md bg-zinc-100 flex items-center justify-center font-bold text-zinc-950 text-xs">
            T
          </div>
          <span className="font-semibold text-base tracking-tight text-zinc-100">
            Tailr
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
            v1.0
          </span>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-zinc-900 p-1 rounded-md border border-zinc-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-zinc-800 text-zinc-100 font-semibold border border-zinc-700 shadow-xs"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Guardrails Status Badge */}
        <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Guardrails Active</span>
        </div>
      </div>
    </header>
  );
}
