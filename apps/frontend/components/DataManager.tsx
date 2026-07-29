"use client";

import { useState, useEffect } from "react";
import { useUIStore } from "@/lib/store";
import {
  listResumes, deleteResume, getResumeDetails,
  listJobDescriptions, deleteJobDescription, getJobDescriptionDetails,
} from "@/lib/api";
import { ParsedResumeView, JdDetailView } from "@/components/DetailViews";
import {
  FileText, Briefcase, Trash2, ChevronDown, ChevronRight,
  CheckCircle2, X, Loader2, Play,
} from "lucide-react";

export function DataManager({
  open, onClose,
  onUseResume, onUseJd,
}: {
  open: boolean;
  onClose: () => void;
  onUseResume?: (id: string) => void;
  onUseJd?: (id: string) => void;
}) {
  const {
    savedResumes, setSavedResumes,
    savedJds, setSavedJds,
    selectedResumeId,
    selectedJdId,
  } = useUIStore();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"resumes" | "jds">("resumes");
  const [deleting, setDeleting] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [details, setDetails] = useState<Record<string, Record<string, unknown> | null>>({});
  const [loadingDetails, setLoadingDetails] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError(null);
    Promise.all([
      listResumes().then(setSavedResumes).catch(() => {}),
      listJobDescriptions().then(setSavedJds).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, [open, setSavedResumes, setSavedJds]);

  const toggleExpand = async (id: string, type: "resume" | "jd") => {
    if (expanded.has(id)) {
      const next = new Set(expanded);
      next.delete(id);
      setExpanded(next);
      return;
    }
    if (details[id] !== undefined) {
      setExpanded(new Set([...expanded, id]));
      return;
    }
    setLoadingDetails(new Set([...loadingDetails, id]));
    try {
      const data: Record<string, unknown> = type === "resume"
        ? await getResumeDetails(id)
        : (await getJobDescriptionDetails(id)) as unknown as Record<string, unknown>;
      setDetails((prev) => ({ ...prev, [id]: data }));
      setExpanded(new Set([...expanded, id]));
    } catch {
      setDetails((prev) => ({ ...prev, [id]: null }));
    } finally {
      const next = new Set(loadingDetails);
      next.delete(id);
      setLoadingDetails(next);
    }
  };

  const handleDeleteResume = async (id: string) => {
    setDeleting(id);
    try {
      await deleteResume(id);
      setSavedResumes(savedResumes.filter((r) => r.id !== id));
      const next = new Set(expanded);
      next.delete(id);
      setExpanded(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setDeleting(null);
    }
  };

  const handleDeleteJd = async (id: string) => {
    setDeleting(id);
    try {
      await deleteJobDescription(id);
      setSavedJds(savedJds.filter((j) => j.id !== id));
      const next = new Set(expanded);
      next.delete(id);
      setExpanded(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setDeleting(null);
    }
  };

  if (!open) return null;

  const renderResumeItem = (r: { id: string; title: string; current_version: number; updated_at: string }) => {
    const isExpanded = expanded.has(r.id);
    const isLoadingDetail = loadingDetails.has(r.id);
    const detail = details[r.id];

    return (
      <div key={r.id}>
        <div className="flex items-center justify-between p-3 rounded bg-zinc-800/50 border border-zinc-700 hover:border-zinc-600 transition-colors">
          <button
            onClick={() => toggleExpand(r.id, "resume")}
            className="flex items-center gap-3 min-w-0 flex-1 text-left"
          >
            {isLoadingDetail ? (
              <Loader2 className="w-3.5 h-3.5 shrink-0 animate-spin text-zinc-500" />
            ) : isExpanded ? (
              <ChevronDown className="w-3.5 h-3.5 shrink-0 text-zinc-400" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5 shrink-0 text-zinc-500" />
            )}
            <FileText className="w-4 h-4 shrink-0 text-zinc-400" />
            <div className="min-w-0">
              <div className="text-xs font-semibold text-zinc-200 truncate">{r.title}</div>
              <div className="text-[10px] text-zinc-500 font-mono mt-px">
                v{r.current_version} · {new Date(r.updated_at).toLocaleDateString()}
                {selectedResumeId === r.id && <span className="text-emerald-400 ml-2">· Selected</span>}
              </div>
            </div>
          </button>
          <div className="flex items-center gap-1.5 shrink-0">
            {selectedResumeId !== r.id && onUseResume && (
              <button
                onClick={() => { onUseResume(r.id); onClose(); }}
                className="flex items-center gap-1 px-2 py-1 rounded text-[10px] font-mono bg-emerald-900/40 border border-emerald-700/50 text-emerald-300 hover:bg-emerald-800/40 transition-colors"
                title="Use this resume"
              >
                <Play className="w-3 h-3" /> Use
              </button>
            )}
            <button
              onClick={() => handleDeleteResume(r.id)}
              disabled={deleting === r.id}
              className="p-1.5 rounded hover:bg-zinc-700 text-zinc-500 hover:text-rose-400 disabled:opacity-50"
              title="Delete"
            >
              {deleting === r.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
        {isExpanded && (
          <div className="ml-8 mt-1 p-3 rounded bg-zinc-900 border border-zinc-700/50 text-xs max-h-96 overflow-y-auto">
            {detail ? <ParsedResumeView data={detail} /> : <div className="text-zinc-500">No details available.</div>}
          </div>
        )}
      </div>
    );
  };

  const renderJdItem = (j: { id: string; title: string; company?: string | null }) => {
    const isExpanded = expanded.has(j.id);
    const isLoadingDetail = loadingDetails.has(j.id);
    const detail = details[j.id];

    return (
      <div key={j.id}>
        <div className="flex items-center justify-between p-3 rounded bg-zinc-800/50 border border-zinc-700 hover:border-zinc-600 transition-colors">
          <button
            onClick={() => toggleExpand(j.id, "jd")}
            className="flex items-center gap-3 min-w-0 flex-1 text-left"
          >
            {isLoadingDetail ? (
              <Loader2 className="w-3.5 h-3.5 shrink-0 animate-spin text-zinc-500" />
            ) : isExpanded ? (
              <ChevronDown className="w-3.5 h-3.5 shrink-0 text-zinc-400" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5 shrink-0 text-zinc-500" />
            )}
            <Briefcase className="w-4 h-4 shrink-0 text-zinc-400" />
            <div className="min-w-0">
              <div className="text-xs font-semibold text-zinc-200 truncate">{j.title}</div>
              <div className="text-[10px] text-zinc-500 font-mono mt-px">
                {j.company}{selectedJdId === j.id && <span className="text-emerald-400 ml-2">· Selected</span>}
              </div>
            </div>
          </button>
          <div className="flex items-center gap-1.5 shrink-0">
            {selectedJdId !== j.id && onUseJd && (
              <button
                onClick={() => { onUseJd(j.id); onClose(); }}
                className="flex items-center gap-1 px-2 py-1 rounded text-[10px] font-mono bg-emerald-900/40 border border-emerald-700/50 text-emerald-300 hover:bg-emerald-800/40 transition-colors"
                title="Use this job description"
              >
                <Play className="w-3 h-3" /> Use
              </button>
            )}
            <button
              onClick={() => handleDeleteJd(j.id)}
              disabled={deleting === j.id}
              className="p-1.5 rounded hover:bg-zinc-700 text-zinc-500 hover:text-rose-400 disabled:opacity-50"
              title="Delete"
            >
              {deleting === j.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
        {isExpanded && (
          <div className="ml-8 mt-1 p-3 rounded bg-zinc-900 border border-zinc-700/50 text-xs max-h-96 overflow-y-auto">
            {detail ? <JdDetailView data={detail} /> : <div className="text-zinc-500">No details available.</div>}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-zinc-900 border border-zinc-700 rounded-lg w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-700">
          <h2 className="text-sm font-semibold text-zinc-100">My Data</h2>
          <button onClick={onClose} className="p-1 rounded hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex border-b border-zinc-700 px-5">
          <button
            onClick={() => setTab("resumes")}
            className={`px-3 py-2.5 text-xs font-medium font-mono border-b-2 transition-colors ${
              tab === "resumes" ? "border-zinc-100 text-zinc-100" : "border-transparent text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Resumes ({savedResumes.length})
          </button>
          <button
            onClick={() => setTab("jds")}
            className={`px-3 py-2.5 text-xs font-medium font-mono border-b-2 transition-colors ${
              tab === "jds" ? "border-zinc-100 text-zinc-100" : "border-transparent text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Job Descriptions ({savedJds.length})
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-2 min-h-[200px]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-5 h-5 animate-spin text-zinc-500" />
            </div>
          ) : error ? (
            <div className="p-3 rounded bg-rose-950/40 border border-rose-900/60 text-rose-400 text-xs">{error}</div>
          ) : tab === "resumes" ? (
            savedResumes.length === 0 ? (
              <div className="py-12 text-center text-xs text-zinc-500 font-mono">No resumes uploaded yet.</div>
            ) : (
              savedResumes.map(renderResumeItem)
            )
          ) : (
            savedJds.length === 0 ? (
              <div className="py-12 text-center text-xs text-zinc-500 font-mono">No job descriptions yet.</div>
            ) : (
              savedJds.map(renderJdItem)
            )
          )}
        </div>
      </div>
    </div>
  );
}
