"use client";

import { useState } from "react";
import { useUIStore } from "../lib/store";
import { Briefcase, Plus, CheckCircle2, AlertCircle, Cpu } from "lucide-react";
import { createJobDescription, JobDescriptionData } from "../lib/api";

export function JobDescriptionManager() {
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<JobDescriptionData | null>(null);

  const { setSelectedJD, setWizardStep, setActiveTab } = useUIStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !company || !description) return;

    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const jd = await createJobDescription({ title, company, description });
      setSuccess(jd);
      setSelectedJD(jd.id, `${jd.title} (${jd.company})`);
      setTitle("");
      setCompany("");
      setDescription("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to parse job description");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Create Target Job Description Form */}
      <form onSubmit={handleSubmit} className="min-panel p-6 space-y-4">
        <div className="space-y-1 border-b border-zinc-800 pb-3">
          <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-zinc-400" /> Target Job Description & AI Requirements Extractor
          </h3>
          <p className="text-xs text-zinc-400">
            Paste target role details. The JD Analyzer agent (qwen3:8b) will parse required skills, seniority, and priority keywords.
          </p>
        </div>

        {error && (
          <div className="p-3 rounded bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {success && (
          <div className="p-4 rounded bg-emerald-950/50 border border-emerald-800 text-emerald-300 space-y-2 font-mono">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> JD Parsed Successfully!</span>
              <span>ID: {success.id}</span>
            </div>
            {success.parsed_requirements?.required_skills && (
              <div className="text-[11px] text-zinc-300">
                Extracted Skills: {success.parsed_requirements.required_skills.join(", ")}
              </div>
            )}
            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => {
                  setWizardStep(3);
                  setActiveTab("wizard");
                }}
                className="min-button min-button-primary text-xs"
              >
                <Cpu className="w-3.5 h-3.5" /> Continue to Tailoring Pipeline
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">Job Title *</label>
            <input
              type="text"
              required
              placeholder="e.g. Senior Software Engineer - AI Platform"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">Company Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Tailr AI Systems"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1">Full Job Description Text *</label>
          <textarea
            required
            rows={6}
            placeholder="Paste full job requirements, responsibilities, and qualifications..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded p-3 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 font-mono leading-relaxed"
          />
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isSubmitting || !title || !company || !description}
            className="min-button min-button-primary"
          >
            <Plus className="w-4 h-4" /> {isSubmitting ? "Analyzing JD with AI..." : "Parse & Save Target JD"}
          </button>
        </div>
      </form>
    </div>
  );
}
