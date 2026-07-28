"use client";

import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { uploadResumeFile } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import { FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface ResumeUploaderProps {
  onSuccess?: (rawContent: string, filename: string) => void;
}

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"];

export function ResumeUploader({ onSuccess }: ResumeUploaderProps) {
  const { setMasterResumeText } = useUIStore();
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

      if (ext === ".txt") {
        const text = await selectedFile.text();
        setMasterResumeText(text);
      }

      await uploadResumeFile(selectedFile, title);

      setIsUploading(false);
      setStatusMsg({ type: "success", text: `Uploaded ${selectedFile.name}` });

      if (onSuccess) {
        onSuccess("", selectedFile.name);
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
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`min-card p-6 border-dashed text-center cursor-pointer transition-colors ${
          isDragOver ? "border-zinc-400 bg-zinc-900" : "border-zinc-800 hover:border-zinc-700"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          className="hidden"
        />
        <div className="flex flex-col items-center justify-center space-y-2">
          {isUploading ? (
            <Loader2 className="w-8 h-8 text-zinc-400 animate-spin" />
          ) : file ? (
            <FileText className="w-8 h-8 text-zinc-300" />
          ) : (
            <UploadIcon />
          )}
          <div>
            <p className="text-sm font-medium text-zinc-200">
              {file ? file.name : "Upload Resume (PDF, DOCX, or TXT)"}
            </p>
            <p className="text-xs text-zinc-500 mt-0.5">Drag & drop or click to browse</p>
          </div>
        </div>
      </div>

      {statusMsg && (
        <div
          className={`p-3 rounded-md text-xs flex items-center gap-2 font-mono ${
            statusMsg.type === "success"
              ? "bg-emerald-950/40 text-emerald-400 border border-emerald-900/60"
              : "bg-rose-950/40 text-rose-400 border border-rose-900/60"
          }`}
        >
          {statusMsg.type === "success" ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
          <span>{statusMsg.text}</span>
        </div>
      )}
    </div>
  );
}

function UploadIcon() {
  return (
    <svg className="w-8 h-8 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
  );
}