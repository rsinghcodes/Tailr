"use client";

import { useState, useEffect, startTransition } from "react";
import { useUIStore } from "@/lib/store";
import {
  listResumes, deleteResume, getResumeDetails,
  listJobDescriptions, deleteJobDescription, getJobDescriptionDetails,
} from "@/lib/api";
import { ParsedResumeView, JdDetailView } from "@/components/DetailViews";
import {
  FileText, Briefcase, Trash2, ChevronRight,
  X, Loader2, Play, Database,
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
    startTransition(() => {
      setLoading(true);
      setError(null);
    });
    Promise.all([
      listResumes().then(setSavedResumes).catch(() => {}),
      listJobDescriptions().then(setSavedJds).catch(() => {}),
    ]).finally(() => startTransition(() => setLoading(false)));
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
    const isSelected = selectedResumeId === r.id;

    return (
      <div key={r.id} className="space-y-1">
        <div
          className="rounded-2xl p-3.5 flex items-center justify-between gap-3 border transition-all"
          style={{
            background: isSelected ? "var(--md-primary-c)" : "var(--md-surface)",
            borderColor: isSelected ? "rgba(79,70,229,0.3)" : "var(--md-outline)",
          }}
        >
          <button onClick={() => toggleExpand(r.id, "resume")} className="flex items-center gap-3 min-w-0 flex-1 text-left">
            {isLoadingDetail ? (
              <Loader2 className="w-4 h-4 shrink-0 animate-spin" style={{ color: "var(--md-primary)" }} />
            ) : (
              <ChevronRight className={`w-4 h-4 shrink-0 transition-transform ${isExpanded ? "rotate-90" : ""}`} style={{ color: "var(--md-on-surface-d)" }} />
            )}
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
              style={{ background: isSelected ? "rgba(79,70,229,0.18)" : "var(--md-surface-c1)" }}
            >
              <FileText className="w-4.5 h-4.5" style={{ color: isSelected ? "var(--md-primary)" : "var(--md-on-surface-v)" }} />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold truncate" style={{ color: "var(--md-on-bg)" }}>{r.title}</div>
              <div className="text-xs mt-0.5" style={{ color: "var(--md-on-surface-v)" }}>
                v{r.current_version} · {new Date(r.updated_at).toLocaleDateString()}
                {isSelected && <span className="font-bold ml-2" style={{ color: "var(--md-primary)" }}>· Active</span>}
              </div>
            </div>
          </button>
          <div className="flex items-center gap-1.5 shrink-0">
            {!isSelected && onUseResume && (
              <button
                onClick={() => { onUseResume(r.id); onClose(); }}
                className="btn btn-secondary py-1.5 px-3 text-xs gap-1.5"
              >
                <Play className="w-3 h-3" /> Select
              </button>
            )}
            <button
              onClick={() => handleDeleteResume(r.id)}
              disabled={deleting === r.id}
              className="btn btn-ghost p-2 text-xs rounded-xl hover:text-red-600"
              style={{ color: "var(--md-on-surface-d)" }}
            >
              {deleting === r.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
            </button>
          </div>
        </div>
        {isExpanded && (
          <div
            className="ml-6 mt-1 p-5 rounded-2xl border"
            style={{ background: "var(--md-surface-c1)", borderColor: "var(--md-outline)" }}
          >
            {detail ? <ParsedResumeView data={detail} /> : <div className="text-sm" style={{ color: "var(--md-on-surface-d)" }}>No details available.</div>}
          </div>
        )}
      </div>
    );
  };

  const renderJdItem = (j: { id: string; title: string; company?: string | null }) => {
    const isExpanded = expanded.has(j.id);
    const isLoadingDetail = loadingDetails.has(j.id);
    const detail = details[j.id];
    const isSelected = selectedJdId === j.id;

    return (
      <div key={j.id} className="space-y-1">
        <div
          className="rounded-2xl p-3.5 flex items-center justify-between gap-3 border transition-all"
          style={{
            background: isSelected ? "var(--md-primary-c)" : "var(--md-surface)",
            borderColor: isSelected ? "rgba(79,70,229,0.3)" : "var(--md-outline)",
          }}
        >
          <button onClick={() => toggleExpand(j.id, "jd")} className="flex items-center gap-3 min-w-0 flex-1 text-left">
            {isLoadingDetail ? (
              <Loader2 className="w-4 h-4 shrink-0 animate-spin" style={{ color: "var(--md-primary)" }} />
            ) : (
              <ChevronRight className={`w-4 h-4 shrink-0 transition-transform ${isExpanded ? "rotate-90" : ""}`} style={{ color: "var(--md-on-surface-d)" }} />
            )}
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
              style={{ background: isSelected ? "rgba(79,70,229,0.18)" : "var(--md-surface-c1)" }}
            >
              <Briefcase className="w-4.5 h-4.5" style={{ color: isSelected ? "var(--md-primary)" : "var(--md-on-surface-v)" }} />
            </div>
            <div className="min-w-0">
              <div className="text-sm font-semibold truncate" style={{ color: "var(--md-on-bg)" }}>{j.title}</div>
              <div className="text-xs mt-0.5" style={{ color: "var(--md-on-surface-v)" }}>
                {j.company || "Unknown Company"}
                {isSelected && <span className="font-bold ml-2" style={{ color: "var(--md-primary)" }}>· Active</span>}
              </div>
            </div>
          </button>
          <div className="flex items-center gap-1.5 shrink-0">
            {!isSelected && onUseJd && (
              <button
                onClick={() => { onUseJd(j.id); onClose(); }}
                className="btn btn-secondary py-1.5 px-3 text-xs gap-1.5"
              >
                <Play className="w-3 h-3" /> Select
              </button>
            )}
            <button
              onClick={() => handleDeleteJd(j.id)}
              disabled={deleting === j.id}
              className="btn btn-ghost p-2 text-xs rounded-xl hover:text-red-600"
              style={{ color: "var(--md-on-surface-d)" }}
            >
              {deleting === j.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
            </button>
          </div>
        </div>
        {isExpanded && (
          <div
            className="ml-6 mt-1 p-5 rounded-2xl border"
            style={{ background: "var(--md-surface-c1)", borderColor: "var(--md-outline)" }}
          >
            {detail ? <JdDetailView data={detail} /> : <div className="text-sm" style={{ color: "var(--md-on-surface-d)" }}>No details available.</div>}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div
        className="w-full max-w-2xl max-h-[85vh] flex flex-col rounded-3xl shadow-2xl overflow-hidden border"
        style={{
          background: "var(--md-surface)",
          borderColor: "var(--md-outline)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b" style={{ borderColor: "var(--md-outline)" }}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl flex items-center justify-center" style={{ background: "var(--md-primary-c)", color: "var(--md-primary)" }}>
              <Database className="w-4.5 h-4.5" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight" style={{ color: "var(--md-on-bg)" }}>
                Saved Data
              </h2>
              <p className="text-xs" style={{ color: "var(--md-on-surface-v)" }}>
                Access and manage stored resumes and job postings
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn btn-ghost p-2 rounded-full hover:bg-slate-100"
            style={{ color: "var(--md-on-surface-v)" }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Pills */}
        <div className="flex gap-2 px-6 pt-3 pb-3 border-b" style={{ borderColor: "var(--md-outline)" }}>
          <button
            onClick={() => setTab("resumes")}
            className="px-4 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all duration-200"
            style={
              tab === "resumes"
                ? { background: "var(--md-primary)", color: "var(--md-on-primary)", boxShadow: "0 2px 8px rgba(79,70,229,0.25)" }
                : { background: "var(--md-surface-c1)", color: "var(--md-on-surface-v)" }
            }
          >
            Resumes ({savedResumes.length})
          </button>
          <button
            onClick={() => setTab("jds")}
            className="px-4 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all duration-200"
            style={
              tab === "jds"
                ? { background: "var(--md-primary)", color: "var(--md-on-primary)", boxShadow: "0 2px 8px rgba(79,70,229,0.25)" }
                : { background: "var(--md-surface-c1)", color: "var(--md-on-surface-v)" }
            }
          >
            Job Descriptions ({savedJds.length})
          </button>
        </div>

        {/* List Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 min-h-[260px]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <Loader2 className="w-7 h-7 animate-spin" style={{ color: "var(--md-primary)" }} />
              <span className="text-sm" style={{ color: "var(--md-on-surface-v)" }}>Loading stored documents…</span>
            </div>
          ) : error ? (
            <div className="p-4 rounded-2xl text-sm border" style={{ background: "var(--md-error-c)", borderColor: "rgba(220,38,38,0.2)", color: "var(--md-error)" }}>
              {error}
            </div>
          ) : tab === "resumes" ? (
            savedResumes.length === 0
              ? <div className="py-16 text-center text-sm" style={{ color: "var(--md-on-surface-d)" }}>No resumes uploaded yet.</div>
              : savedResumes.map(renderResumeItem)
          ) : (
            savedJds.length === 0
              ? <div className="py-16 text-center text-sm" style={{ color: "var(--md-on-surface-d)" }}>No job descriptions saved yet.</div>
              : savedJds.map(renderJdItem)
          )}
        </div>
      </div>
    </div>
  );
}
