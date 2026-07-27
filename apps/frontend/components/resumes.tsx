"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listResumes, deleteResume, getResumeVersions } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import {
  FileText,
  Trash2,
  CheckCircle,
  Clock,
  ChevronDown,
  ChevronUp,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

export default function Resumes() {
  const queryClient = useQueryClient();
  const { selectedResumeId, setSelectedResume } = useUIStore();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: resumes, isLoading } = useQuery({
    queryKey: ["resumes"],
    queryFn: listResumes,
  });

  const { data: versions } = useQuery({
    queryKey: ["resume-versions", expandedId],
    queryFn: () => getResumeVersions(expandedId!),
    enabled: !!expandedId,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      if (expandedId) setExpandedId(null);
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Resumes</h1>
        <p className="mt-1 text-sm text-muted">
          Manage your uploaded master resumes
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-accent" />
        </div>
      ) : !resumes || resumes.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-surface py-12 text-center">
          <FileText className="mx-auto mb-3 h-10 w-10 text-slate-600" />
          <p className="text-sm text-muted">
            No resumes uploaded yet. Use the Optimize wizard to upload one.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {resumes.map((resume) => (
            <div
              key={resume.id}
              className={cn(
                "rounded-xl border bg-surface transition-colors",
                selectedResumeId === resume.id
                  ? "border-accent/50"
                  : "border-slate-800"
              )}
            >
              <div className="flex items-center justify-between p-4">
                <button
                  onClick={() =>
                    setSelectedResume(resume.id, resume.title)
                  }
                  className="flex flex-1 items-center gap-3 text-left"
                >
                  <FileText
                    className={cn(
                      "h-5 w-5 shrink-0",
                      selectedResumeId === resume.id
                        ? "text-accent"
                        : "text-muted"
                    )}
                  />
                  <div>
                    <p className="text-sm font-medium text-white">
                      {resume.title}
                    </p>
                    <p className="text-xs text-muted">
                      Version {resume.current_version} · {resume.status}
                    </p>
                  </div>
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      setExpandedId(expandedId === resume.id ? null : resume.id)
                    }
                    className="rounded p-1.5 text-muted transition-colors hover:bg-slate-800 hover:text-slate-300"
                  >
                    {expandedId === resume.id ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(resume.id)}
                    disabled={deleteMutation.isPending}
                    className="rounded p-1.5 text-muted transition-colors hover:bg-danger/10 hover:text-danger"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {expandedId === resume.id && versions && (
                <div className="border-t border-slate-800 px-4 py-3">
                  <p className="mb-2 text-xs font-medium uppercase text-muted">
                    Version History
                  </p>
                  {versions.length === 0 ? (
                    <p className="text-xs text-slate-600">No versions</p>
                  ) : (
                    <div className="space-y-1">
                      {versions.map((v) => (
                        <div
                          key={v.version_id}
                          className="flex items-center justify-between rounded-lg bg-slate-900 px-3 py-2 text-xs"
                        >
                          <div className="flex items-center gap-2">
                            <Clock className="h-3 w-3 text-muted" />
                            <span className="text-slate-300">
                              Version {v.version}
                            </span>
                          </div>
                          <span className="text-muted">
                            {new Date(v.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {selectedResumeId === resume.id && (
                <div className="border-t border-accent/20 px-4 py-2">
                  <p className="flex items-center gap-1 text-xs text-accent">
                    <CheckCircle className="h-3 w-3" /> Selected for
                    optimization
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
