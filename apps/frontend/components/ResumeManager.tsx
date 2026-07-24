"use client";

import { useEffect, useState } from "react";
import { useUIStore } from "@/lib/store";
import { listResumes, deleteResume, getResumeVersions, ResumeVersionItem } from "@/lib/api";
import { ResumeUploader } from "./ResumeUploader";
import { FileText, Trash2, History, RefreshCw, ArrowRight, Loader2 } from "lucide-react";

export function ResumeManager() {
  const { savedResumes, setSavedResumes, setMasterResumeText, setWizardStep, setActiveTab } = useUIStore();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedVersions, setSelectedVersions] = useState<{ resumeId: string; items: ResumeVersionItem[] } | null>(null);

  const fetchResumes = async () => {
    setIsLoading(true);
    try {
      const items = await listResumes();
      setSavedResumes(items);
    } catch {
      // Ignore fallback if backend empty
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleDelete = async (id: string) => {
    if (confirm("Delete this master resume and all associated versions?")) {
      await deleteResume(id);
      fetchResumes();
    }
  };

  const handleViewVersions = async (id: string) => {
    try {
      const versions = await getResumeVersions(id);
      setSelectedVersions({ resumeId: id, items: versions });
    } catch {
      setSelectedVersions(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="min-panel p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-zinc-100">Upload Master Resume</h2>
            <p className="text-xs text-zinc-400">Upload LaTeX (.tex) or text (.txt) files to parse into the canonical resume model.</p>
          </div>
        </div>

        <ResumeUploader onSuccess={() => fetchResumes()} />
      </div>

      {/* Resumes List */}
      <div className="min-panel p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-zinc-400" />
            <h3 className="text-base font-semibold text-zinc-100">Stored Master Resumes</h3>
          </div>
          <button
            onClick={fetchResumes}
            disabled={isLoading}
            className="min-button min-button-secondary text-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} /> Refresh
          </button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs text-zinc-400 flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" /> Loading resumes...
          </div>
        ) : savedResumes.length === 0 ? (
          <div className="p-8 text-center text-xs text-zinc-500">
            No master resumes stored yet. Upload a .tex file above or paste content in the wizard.
          </div>
        ) : (
          <div className="space-y-3">
            {savedResumes.map((resume) => (
              <div key={resume.id} className="min-card p-4 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="font-medium text-sm text-zinc-100 flex items-center gap-2">
                    <span>{resume.title}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                      v{resume.current_version}
                    </span>
                  </div>
                  <div className="text-xs text-zinc-500 font-mono mt-1">
                    ID: {resume.id} | Created: {new Date(resume.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleViewVersions(resume.id)}
                    className="min-button min-button-secondary text-xs"
                  >
                    <History className="w-3.5 h-3.5" /> Versions
                  </button>
                  <button
                    onClick={() => {
                      setMasterResumeText(`% Selected Master Resume: ${resume.title}\n\\documentclass{article}\n\\begin{document}\n\\section{Experience}\nExperience loaded from stored resume ${resume.id}.\n\\end{document}`);
                      setWizardStep(2);
                      setActiveTab("wizard");
                    }}
                    className="min-button min-button-primary text-xs"
                  >
                    Use in Wizard <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDelete(resume.id)}
                    className="p-2 text-zinc-400 hover:text-rose-400 hover:bg-zinc-800 rounded-md transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Versions Modal / Card */}
      {selectedVersions && (
        <div className="min-panel p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <h4 className="text-sm font-semibold text-zinc-200">Version History (Resume ID: {selectedVersions.resumeId})</h4>
            <button
              onClick={() => setSelectedVersions(null)}
              className="text-xs text-zinc-400 hover:text-zinc-200"
            >
              Close
            </button>
          </div>
          <div className="space-y-2 font-mono text-xs">
            {selectedVersions.items.map((v) => (
              <div key={v.version_id} className="p-3 bg-zinc-900 border border-zinc-800 rounded-md flex justify-between">
                <span>Version {v.version}</span>
                <span className="text-zinc-500">{new Date(v.created_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
