"use client";

import { useState } from "react";
import { useUIStore } from "@/lib/store";
import { createJobDescription, JobDescriptionData } from "@/lib/api";
import { Briefcase, Plus, CheckCircle2, ArrowRight, Loader2 } from "lucide-react";

export function JobDescriptionManager() {
  const { savedJds, setSavedJds, setJobDescriptionText, setWizardStep, setActiveTab } = useUIStore();
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeJd, setActiveJd] = useState<JobDescriptionData | null>(null);

  const handleCreate = async () => {
    if (!title || !description) return;

    setIsAnalyzing(true);
    try {
      const jdData = await createJobDescription({
        title,
        company: company || "Unknown Company",
        description,
      });

      setActiveJd(jdData);
      setSavedJds([jdData, ...savedJds]);
      setIsAnalyzing(false);
      setTitle("");
      setCompany("");
      setDescription("");
    } catch {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Create / Analyze JD Form */}
      <div className="min-panel p-6 space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-zinc-100">Analyze New Job Description</h2>
          <p className="text-xs text-zinc-400">Parse and extract structured skills, keywords, and responsibilities via AI.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Job Title (e.g. Senior AI Engineer)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="min-input"
          />
          <input
            type="text"
            placeholder="Company Name (optional)"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="min-input"
          />
        </div>

        <textarea
          rows={6}
          placeholder="Paste complete job description text here..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="min-input w-full font-mono text-xs"
        />

        <div className="flex justify-end">
          <button
            onClick={handleCreate}
            disabled={isAnalyzing || !title || !description}
            className="min-button min-button-primary"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Analyzing Requirements...
              </>
            ) : (
              <>
                <Plus className="w-4 h-4" /> Analyze Job Description
              </>
            )}
          </button>
        </div>
      </div>

      {/* Extracted Analysis Details */}
      {activeJd && (
        <div className="min-panel p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div>
              <h3 className="text-base font-semibold text-zinc-100">{activeJd.title}</h3>
              <p className="text-xs text-zinc-400">{activeJd.company}</p>
            </div>
            <button
              onClick={() => {
                setJobDescriptionText(activeJd.description);
                setWizardStep(3);
                setActiveTab("wizard");
              }}
              className="min-button min-button-primary text-xs"
            >
              Use in Tailoring Wizard <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {activeJd.parsed_requirements && (
            <div className="space-y-3 font-mono text-xs">
              <div>
                <span className="text-zinc-500 font-semibold uppercase">Required Skills:</span>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {activeJd.parsed_requirements.required_skills?.map((skill, sIdx) => (
                    <span key={sIdx} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {activeJd.parsed_requirements.responsibilities && (
                <div>
                  <span className="text-zinc-500 font-semibold uppercase">Core Responsibilities:</span>
                  <ul className="mt-1 space-y-1 text-zinc-300">
                    {activeJd.parsed_requirements.responsibilities.map((r, rIdx) => (
                      <li key={rIdx} className="flex items-center gap-2">
                        <CheckCircle2 className="w-3 h-3 text-zinc-400" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Saved JDs List */}
      {savedJds.length > 0 && (
        <div className="min-panel p-6 space-y-4">
          <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-zinc-400" /> Stored Job Descriptions
          </h3>
          <div className="space-y-2">
            {savedJds.map((jd) => (
              <div key={jd.id} className="min-card p-4 flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm text-zinc-200">{jd.title}</div>
                  <div className="text-xs text-zinc-500">{jd.company}</div>
                </div>
                <button
                  onClick={() => {
                    setJobDescriptionText(jd.description);
                    setWizardStep(3);
                    setActiveTab("wizard");
                  }}
                  className="min-button min-button-secondary text-xs"
                >
                  Select <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
