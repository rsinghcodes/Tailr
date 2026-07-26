"use client";

import { useEffect, useState } from "react";
import { useUIStore } from "../lib/store";
import { FileText, Trash2, Layers, Cpu, AlertCircle } from "lucide-react";
import { listResumes, getResumeVersions, deleteResume, ResumeItem, ResumeVersionItem } from "../lib/api";
import { ResumeUploader } from "./ResumeUploader";

export function ResumeManager() {
  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [versions, setVersions] = useState<ResumeVersionItem[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);

  const { setSelectedResume, setWizardStep, setActiveTab } = useUIStore();

  const loadResumes = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const items = await listResumes();
      setResumes(items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load resumes");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadResumes();
  }, []);

  const handleSelectResume = (r: ResumeItem) => {
    setSelectedResume(r.id, r.title);
  };

  const handleViewVersions = async (r: ResumeItem) => {
    setSelectedResumeId(r.id);
    setLoadingVersions(true);
    try {
      const vers = await getResumeVersions(r.id);
      setVersions(vers);
    } catch {
      setVersions([]);
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this master resume?")) return;
    try {
      await deleteResume(id);
      setResumes((prev) => prev.filter((r) => r.id !== id));
      if (selectedResumeId === id) setSelectedResumeId(null);
    } catch {
      alert("Failed to delete resume");
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Master Resume Component */}
      <ResumeUploader onSuccess={loadResumes} />

      {/* Stored Master Resumes List */}
      <div className="min-panel p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div>
            <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-zinc-400" /> Stored Master Resumes
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              Select a master resume to start tailoring or view LaTeX version history.
            </p>
          </div>
          <button onClick={loadResumes} className="min-button min-button-secondary text-xs">
            Refresh
          </button>
        </div>

        {error && (
          <div className="p-3 rounded bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}

        {isLoading ? (
          <div className="p-8 text-center text-xs text-zinc-500 font-mono">Loading resumes from PostgreSQL...</div>
        ) : resumes.length === 0 ? (
          <div className="p-8 text-center text-xs text-zinc-500 font-mono">
            No master resumes found. Upload a .tex file above to get started.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {resumes.map((r) => (
              <div key={r.id} className="min-card p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="text-sm font-semibold text-zinc-100">{r.title}</div>
                    <div className="text-[10px] font-mono text-zinc-500">ID: {r.id}</div>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-[10px] font-mono text-zinc-300">
                    v{r.current_version}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-zinc-400 font-mono border-t border-zinc-800/80 pt-2">
                  <span>Status: {r.status}</span>
                  <span>{new Date(r.created_at).toLocaleDateString()}</span>
                </div>

                <div className="flex items-center justify-between pt-2 gap-2">
                  <button
                    onClick={() => {
                      handleSelectResume(r);
                      setWizardStep(2);
                      setActiveTab("wizard");
                    }}
                    className="min-button min-button-primary text-xs"
                  >
                    <Cpu className="w-3.5 h-3.5" /> Tailor Resume
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleViewVersions(r)}
                      className="min-button min-button-secondary text-xs"
                    >
                      <Layers className="w-3.5 h-3.5" /> Versions
                    </button>
                    <button
                      onClick={() => handleDelete(r.id)}
                      className="p-2 rounded bg-zinc-900 border border-zinc-800 text-rose-400 hover:bg-rose-950/40 hover:border-rose-800 transition-colors"
                      title="Delete Resume"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resume Version History Modal */}
      {selectedResumeId && (
        <div className="min-panel p-6 space-y-4 border-l-4 border-l-zinc-400">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <h4 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
              <Layers className="w-4 h-4 text-zinc-400" /> Version History for {selectedResumeId}
            </h4>
            <button
              onClick={() => setSelectedResumeId(null)}
              className="text-xs text-zinc-500 hover:text-zinc-300 font-mono"
            >
              Close
            </button>
          </div>

          {loadingVersions ? (
            <div className="text-xs font-mono text-zinc-500 py-4">Fetching versions...</div>
          ) : versions.length === 0 ? (
            <div className="text-xs font-mono text-zinc-500 py-4">No version history records found.</div>
          ) : (
            <div className="space-y-2">
              {versions.map((v) => (
                <div key={v.version_id} className="min-card p-3 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-zinc-200">Version {v.version}</span>
                    <span className="text-zinc-500">{v.latex_path || "canonical_json"}</span>
                  </div>
                  <span className="text-zinc-400">{new Date(v.created_at).toLocaleString()}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
