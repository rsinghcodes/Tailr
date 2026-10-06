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
      // ignore
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="card-3d p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider" style={{ color: "var(--md-primary)" }}>
          <Database className="w-4 h-4" />
          {isResume ? "Saved Resumes" : "Saved Job Descriptions"}
        </div>
        <span
          className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-full"
          style={{ background: "var(--md-surface-c3)", color: "var(--md-on-surface-v)" }}
        >
          {items.length}
        </span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-5 h-5 animate-spin" style={{ color: "var(--md-primary)" }} />
        </div>
      ) : items.length === 0 ? (
        <p className="text-sm py-2" style={{ color: "var(--md-on-surface-d)" }}>
          {isResume
            ? "No saved resumes yet. Upload one above to begin."
            : "No saved job descriptions yet. Add one to begin."}
        </p>
      ) : (
        <div className="space-y-2.5">
          {items.map((item) => {
            const subtitle = isResume
              ? `v${(item as ResumeListItem).current_version} · ${new Date((item as ResumeListItem).updated_at).toLocaleDateString()}`
              : ((item as JobDescriptionData).company ?? "");
            const isSelected = selectedId === item.id;
            return (
              <div
                key={item.id}
                className="rounded-2xl p-3.5 flex items-center justify-between gap-3 border transition-all duration-200"
                style={{
                  background: isSelected ? "rgba(187,179,255,0.08)" : "var(--md-surface-c1)",
                  borderColor: isSelected ? "var(--md-primary)" : "var(--md-outline)",
                }}
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <div
                    className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                    style={{
                      background: isSelected ? "var(--md-primary-c)" : "var(--md-surface-c3)",
                      color: isSelected ? "var(--md-on-primary-c)" : "var(--md-on-surface-v)",
                    }}
                  >
                    {isResume ? <FileText className="w-4.5 h-4.5" /> : <Briefcase className="w-4.5 h-4.5" />}
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-semibold truncate" style={{ color: "var(--md-on-bg)" }}>
                      {item.title}
                    </div>
                    {subtitle && (
                      <div className="text-xs mt-0.5" style={{ color: "var(--md-on-surface-d)" }}>
                        {subtitle}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {isSelected && (
                    <span className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background: "rgba(160,216,212,0.15)", color: "var(--md-tertiary)" }}>
                      <Check className="w-3.5 h-3.5" /> Selected
                    </span>
                  )}
                  {!isSelected && (
                    <button
                      onClick={() => onUse(item.id)}
                      className="btn btn-secondary py-1.5 px-3 text-xs gap-1.5"
                    >
                      <Play className="w-3 h-3" /> Use
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(item.id)}
                    disabled={deleting === item.id}
                    title={isResume ? "Delete resume" : "Delete job description"}
                    className="btn btn-ghost p-2 text-xs rounded-xl hover:text-red-400"
                    style={{ color: "var(--md-on-surface-d)" }}
                  >
                    {deleting === item.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
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
