"use client";

import {
  LayoutDashboard,
  Wand2,
  FileText,
  Briefcase,
  BarChart3,
  ShieldCheck,
} from "lucide-react";
import { useUIStore, type TabType } from "@/lib/store";
import { cn } from "@/lib/utils";

const NAV_ITEMS: { tab: TabType; label: string; icon: typeof LayoutDashboard }[] = [
  { tab: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { tab: "wizard", label: "Optimize", icon: Wand2 },
  { tab: "resumes", label: "Resumes", icon: FileText },
  { tab: "job_descriptions", label: "Job Descriptions", icon: Briefcase },
  { tab: "results", label: "Results", icon: BarChart3 },
  { tab: "audit", label: "Audit Trail", icon: ShieldCheck },
];

export default function Sidebar() {
  const { activeTab, setActiveTab } = useUIStore();

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-slate-800 bg-sidebar">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
          T
        </div>
        <span className="text-lg font-semibold tracking-tight text-white">
          Tailr
        </span>
      </div>

      <nav className="mt-2 flex-1 px-3">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.tab;
          return (
            <button
              key={item.tab}
              onClick={() => setActiveTab(item.tab)}
              className={cn(
                "mb-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-accent/15 text-accent"
                  : "text-slate-400 hover:bg-sidebar-hover hover:text-slate-200"
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="border-t border-slate-800 px-5 py-4">
        <p className="text-xs text-slate-500">AI Resume Intelligence</p>
        <p className="text-xs text-slate-600">v0.1.0</p>
      </div>
    </aside>
  );
}
