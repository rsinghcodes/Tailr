"use client";

import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { uploadResumeFile } from "@/lib/api";
import { FileText, CheckCircle2, AlertCircle, Loader2, Upload } from "lucide-react";

interface ResumeUploaderProps {
  onSuccess?: (resumeId: string, filename: string) => void;
}

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"];

export function ResumeUploader({ onSuccess }: ResumeUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFile = async (selectedFile: File) => {
    const ext = "." + selectedFile.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setStatusMsg({ type: "error", text: `Unsupported file type. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}` });
      return;
    }

    setFile(selectedFile);
    setStatusMsg(null);
    setIsUploading(true);

    try {
      const title = selectedFile.name.replace(/\.[^/.]+$/, "");
      const result = await uploadResumeFile(selectedFile, title);

      setIsUploading(false);
      setStatusMsg({ type: "success", text: `Uploaded ${selectedFile.name}` });

      if (onSuccess) {
        onSuccess(result.resume_id, selectedFile.name);
      }
    } catch (err: unknown) {
      setIsUploading(false);
      const msg = err instanceof Error ? err.message : "Failed to upload file";
      setStatusMsg({ type: "error", text: msg });
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`card-3d p-8 text-center cursor-pointer ${
        isDragOver ? "border-[var(--accent)] scale-[1.02]" : ""
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        className="hidden"
      />

      {isUploading ? (
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-subtle)] flex items-center justify-center">
            <Loader2 className="w-6 h-6 text-[var(--text-secondary)] animate-spin" />
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--text-primary)]">Uploading...</p>
            <p className="text-xs text-[var(--text-muted)] mt-1">{file?.name}</p>
          </div>
        </div>
      ) : file ? (
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-subtle)] flex items-center justify-center">
            <FileText className="w-6 h-6 text-[var(--text-secondary)]" />
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--text-primary)]">{file.name}</p>
            <p className="text-xs text-[var(--text-muted)] mt-1">Click or drag to replace</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-[var(--bg-elevated)] border border-[var(--border-subtle)] flex items-center justify-center">
            <Upload className="w-6 h-6 text-[var(--text-muted)]" />
          </div>
          <div>
            <p className="text-sm font-medium text-[var(--text-primary)]">Upload Resume</p>
            <p className="text-xs text-[var(--text-muted)] mt-1">PDF, DOCX, or TXT</p>
          </div>
        </div>
      )}

      {statusMsg && (
        <div className={`mt-4 flex items-center gap-2 px-3 py-2 rounded-lg text-xs ${
          statusMsg.type === "success"
            ? "bg-emerald-950/30 border border-emerald-800/50 text-emerald-400"
            : "bg-rose-950/30 border border-rose-900/50 text-rose-400"
        }`}>
          {statusMsg.type === "success" ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" /> : <AlertCircle className="w-3.5 h-3.5 shrink-0" />}
          <span>{statusMsg.text}</span>
        </div>
      )}
    </div>
  );
}
