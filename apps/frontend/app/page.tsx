"use client";

import { useUIStore } from "@/lib/store";
import Sidebar from "@/components/sidebar";
import Dashboard from "@/components/dashboard";
import Wizard from "@/components/wizard";
import Resumes from "@/components/resumes";
import JobDescriptions from "@/components/job-descriptions";
import Results from "@/components/results";
import Audit from "@/components/audit";

function ActiveView() {
  const activeTab = useUIStore((s) => s.activeTab);

  switch (activeTab) {
    case "dashboard":
      return <Dashboard />;
    case "wizard":
      return <Wizard />;
    case "resumes":
      return <Resumes />;
    case "job_descriptions":
      return <JobDescriptions />;
    case "results":
      return <Results />;
    case "audit":
      return <Audit />;
    default:
      return <Dashboard />;
  }
}

export default function Home() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6 lg:p-8">
        <ActiveView />
      </main>
    </div>
  );
}
