"use client";

import { useEffect, useState } from "react";
import { FileText, Briefcase, Play, Check, Loader2, Database, Trash2 } from "lucide-react";
import { useUIStore } from "@/lib/store";
import {
  listResumes,
  listJobDescriptions,
  deleteResume,
  deleteJobDescription,
  type ResumeListItem,
  type JobDescriptionData,
} from "@/lib/api";

export function SavedList({
  variant,
  onUse,
}: {
  variant: "resume" | "jd";
  onUse: (id: string) => void;
}) {
  const isResume = variant === "resume";
  const {
    savedResumes, setSavedResumes,
    savedJds, setSavedJds,
    selectedResumeId, selectedJdId,
  } = useUIStore();

  const items = isResume ? savedResumes : savedJds;
  const selectedId = isResume ? selectedResumeId : selectedJdId;
  const [loading, setLoading] = useState(() => items.length === 0);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    if (items.length > 0) return;
    const request = isResume
      ? listResumes().then(setSavedResumes)
      : listJobDescriptions().then(setSavedJds);
    request.catch(() => {}).finally(() => setLoading(false));
  }, [isResume, items.length, setSavedResumes, setSavedJds]);

  const handleDelete = async (id: string) => {
    setDeleting(id);
    try {
      if (isResume) {
        await deleteResume(id);
        setSavedResumes(savedResumes.filter((r) => r.id !== id));
      } else {
        await deleteJobDescription(id);
        setSavedJds(savedJds.filter((j) => j.id !== id));
      }
    } catch {
      // ignore delete errors for now
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="card-3d p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="section-label flex items-center gap-1.5">
          <Database className="w-3.5 h-3.5" />
          {isResume ? "Saved Resumes" : "Saved Job Descriptions"}
        </div>
        <span className="text-[11px] font-mono text-[var(--text-muted)]">{items.length}</span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-4 h-4 animate-spin text-[var(--text-muted)]" />
        </div>
      ) : items.length === 0 ? (
        <p className="text-xs text-[var(--text-muted)]">
          {isResume
            ? "No saved resumes yet. Upload one on the left to begin."
            : "No saved job descriptions yet. Add one below to begin."}
        </p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const subtitle = isResume
              ? `v${(item as ResumeListItem).current_version} · ${new Date((item as ResumeListItem).updated_at).toLocaleDateString()}`
              : ((item as JobDescriptionData).company ?? "");
            return (
              <div
                key={item.id}
                className="card-3d-sm px-3 py-2.5 flex items-center justify-between gap-2"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {isResume ? (
                    <FileText className="w-4 h-4 shrink-0 text-[var(--text-muted)]" />
                  ) : (
                    <Briefcase className="w-4 h-4 shrink-0 text-[var(--text-muted)]" />
                  )}
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-[var(--text-primary)] truncate">
                      {item.title}
                    </div>
                    {subtitle && (
                      <div className="text-[11px] text-[var(--text-muted)] mt-px">{subtitle}</div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  {selectedId === item.id && (
                    <span className="flex items-center gap-1 text-[11px] font-mono text-emerald-400">
                      <Check className="w-3.5 h-3.5" /> Selected
                    </span>
                  )}
                  {selectedId !== item.id && (
                    <button onClick={() => onUse(item.id)} className="btn btn-secondary px-2.5 py-1 text-[11px]">
                      <Play className="w-3 h-3" /> {isResume ? "Use Resume" : "Use JD"}
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(item.id)}
                    disabled={deleting === item.id}
                    title={isResume ? "Delete resume" : "Delete job description"}
                    className="btn btn-ghost p-1.5 text-[var(--text-muted)] hover:text-rose-400 disabled:opacity-40"
                  >
                    {deleting === item.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
