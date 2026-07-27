"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createJobDescription, type JobDescriptionData } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import {
  Briefcase,
  Plus,
  Loader2,
  MapPin,
  Building2,
  CheckCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function JobDescriptions() {
  const queryClient = useQueryClient();
  const { savedJds, setSavedJds, selectedJdId, setSelectedJD } = useUIStore();
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");

  const createMutation = useMutation({
    mutationFn: createJobDescription,
    onSuccess: (data: JobDescriptionData) => {
      setSavedJds([...savedJds, data]);
      setSelectedJD(data.id, data.title);
      setTitle("");
      setCompany("");
      setLocation("");
      setDescription("");
      setShowForm(false);
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Job Descriptions</h1>
          <p className="mt-1 text-sm text-muted">
            Create and manage job descriptions for optimization
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
        >
          <Plus className="h-4 w-4" />
          New JD
        </button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-slate-800 bg-surface p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Create Job Description
          </h2>
          <div className="space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm text-muted">
                  Job Title
                </label>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                  placeholder="e.g. Senior AI Engineer"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm text-muted">
                  Company
                </label>
                <input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                  placeholder="e.g. Acme Corp"
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm text-muted">Location</label>
              <input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                placeholder="e.g. San Francisco, CA (Remote)"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm text-muted">
                Full Job Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={8}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm text-white placeholder-slate-500 focus:border-accent focus:outline-none"
                placeholder="Paste the full job description here…"
              />
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowForm(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={() =>
                  createMutation.mutate({
                    title: title || "Untitled Position",
                    company: company || "Unknown Company",
                    description,
                    location: location || undefined,
                  })
                }
                disabled={!description || createMutation.isPending}
                className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
              >
                {createMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {savedJds.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-surface py-12 text-center">
          <Briefcase className="mx-auto mb-3 h-10 w-10 text-slate-600" />
          <p className="text-sm text-muted">
            No job descriptions created yet. Click &quot;New JD&quot; to create one.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {savedJds.map((jd) => (
            <div
              key={jd.id}
              className={cn(
                "rounded-xl border bg-surface p-4 transition-colors",
                selectedJdId === jd.id
                  ? "border-accent/50"
                  : "border-slate-800"
              )}
            >
              <div className="flex items-start justify-between">
                <button
                  onClick={() => setSelectedJD(jd.id, jd.title)}
                  className="flex flex-1 items-start gap-3 text-left"
                >
                  <Briefcase
                    className={cn(
                      "mt-0.5 h-5 w-5 shrink-0",
                      selectedJdId === jd.id ? "text-accent" : "text-muted"
                    )}
                  />
                  <div>
                    <p className="text-sm font-medium text-white">{jd.title}</p>
                    <div className="mt-1 flex items-center gap-3 text-xs text-muted">
                      <span className="flex items-center gap-1">
                        <Building2 className="h-3 w-3" /> {jd.company}
                      </span>
                      {jd.location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" /> {jd.location}
                        </span>
                      )}
                    </div>
                    {jd.parsed_requirements && (
                      <div className="mt-2">
                        {jd.parsed_requirements.required_skills && (
                          <div className="flex flex-wrap gap-1">
                            {jd.parsed_requirements.required_skills
                              .slice(0, 5)
                              .map((skill, i) => (
                                <span
                                  key={i}
                                  className="rounded bg-accent/10 px-2 py-0.5 text-xs text-accent"
                                >
                                  {skill}
                                </span>
                              ))}
                            {jd.parsed_requirements.required_skills.length >
                              5 && (
                              <span className="text-xs text-muted">
                                +{jd.parsed_requirements.required_skills.length - 5} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </button>

                {selectedJdId === jd.id && (
                  <CheckCircle className="h-4 w-4 shrink-0 text-accent" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
