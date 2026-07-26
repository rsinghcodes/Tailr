"use client";

import { useState } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { uploadResumeFile, ResumeUploadResponse } from "../lib/api";

interface ResumeUploaderProps {
  onSuccess?: (res: ResumeUploadResponse) => void;
}

export function ResumeUploader({ onSuccess }: ResumeUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await uploadResumeFile(file, title || file.name);
      setSuccess(`Resume uploaded successfully! ID: ${result.resume_id}`);
      setFile(null);
      setTitle("");
      if (onSuccess) onSuccess(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to upload resume file");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleUpload} className="min-panel p-6 space-y-4">
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
          <FileText className="w-5 h-5 text-zinc-400" /> Upload Master Resume (.tex / .pdf / .json)
        </h3>
        <p className="text-xs text-zinc-400">
          Upload your master LaTeX file or structured resume document to be stored in PostgreSQL and vector embedded in Qdrant.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center gap-2 font-mono">
          <AlertCircle className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}

      {success && (
        <div className="p-3 rounded bg-emerald-950/50 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2 font-mono">
          <CheckCircle2 className="w-4 h-4 shrink-0" /> {success}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1">Resume Title (Optional)</label>
          <input
            type="text"
            placeholder="e.g. Senior Software Architect Resume 2026"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 font-sans"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-zinc-400 mb-1">Select File (.tex, .pdf, .json, .txt)</label>
          <input
            type="file"
            accept=".tex,.pdf,.json,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-zinc-600 font-mono file:mr-3 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700"
          />
        </div>
      </div>

      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={!file || isUploading}
          className="min-button min-button-primary"
        >
          <Upload className="w-4 h-4" /> {isUploading ? "Uploading & Parsing..." : "Upload Master Resume"}
        </button>
      </div>
    </form>
  );
}
