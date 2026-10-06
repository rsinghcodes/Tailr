"use client";

import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { uploadResumeFile } from "@/lib/api";
import { FileText, CheckCircle2, AlertCircle, Loader2, Upload, CloudUpload } from "lucide-react";

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
      if (onSuccess) onSuccess(result.resume_id, selectedFile.name);
    } catch (err: unknown) {
      setIsUploading(false);
      const msg = err instanceof Error ? err.message : "Failed to upload file";
      setStatusMsg({ type: "error", text: msg });
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) handleFile(e.target.files[0]);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className="cursor-pointer rounded-3xl p-10 text-center transition-all duration-300 select-none"
      style={{
        background: isDragOver
          ? "rgba(187,179,255,0.08)"
          : "var(--md-surface-c1)",
        border: `2px dashed ${isDragOver ? "var(--md-primary)" : "var(--md-outline-v)"}`,
        boxShadow: isDragOver ? "0 0 40px rgba(187,179,255,0.12)" : undefined,
        transform: isDragOver ? "scale(1.01)" : undefined,
      }}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        className="hidden"
      />

      {isUploading ? (
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-16 h-16 rounded-3xl flex items-center justify-center"
            style={{ background: "rgba(187,179,255,0.10)", border: "1px solid rgba(187,179,255,0.25)" }}
          >
            <Loader2 className="w-7 h-7 animate-spin" style={{ color: "var(--md-primary)" }} />
          </div>
          <div>
            <p className="text-base font-semibold" style={{ color: "var(--md-on-bg)" }}>Uploading…</p>
            <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>{file?.name}</p>
          </div>
        </div>
      ) : file && statusMsg?.type === "success" ? (
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-16 h-16 rounded-3xl flex items-center justify-center"
            style={{ background: "rgba(160,216,212,0.10)", border: "1px solid rgba(160,216,212,0.30)" }}
          >
            <CheckCircle2 className="w-7 h-7" style={{ color: "var(--md-tertiary)" }} />
          </div>
          <div>
            <p className="text-base font-semibold" style={{ color: "var(--md-on-bg)" }}>{file.name}</p>
            <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>Click or drag to replace</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-16 h-16 rounded-3xl flex items-center justify-center transition-all duration-300"
            style={{
              background: isDragOver ? "rgba(187,179,255,0.12)" : "var(--md-surface-c2)",
              border: `1.5px solid ${isDragOver ? "rgba(187,179,255,0.40)" : "var(--md-outline)"}`,
            }}
          >
            <CloudUpload className="w-7 h-7" style={{ color: isDragOver ? "var(--md-primary)" : "var(--md-on-surface-d)" }} />
          </div>
          <div>
            <p className="text-base font-semibold" style={{ color: "var(--md-on-bg)" }}>
              Drop your resume here
            </p>
            <p className="text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>
              PDF, DOCX, or TXT · Click to browse
            </p>
          </div>
        </div>
      )}

      {statusMsg?.type === "error" && (
        <div
          className="mt-5 flex items-center gap-3 px-4 py-3 rounded-2xl text-sm"
          style={{
            background: "rgba(255,180,171,0.08)",
            border: "1px solid rgba(255,180,171,0.25)",
            color: "var(--md-error)",
          }}
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{statusMsg.text}</span>
        </div>
      )}
    </div>
  );
}
