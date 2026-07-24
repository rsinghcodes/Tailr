"use client";

import { useState, useRef, ChangeEvent, DragEvent } from "react";
import { uploadResumeFile } from "@/lib/api";
import { useUIStore } from "@/lib/store";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface ResumeUploaderProps {
  onSuccess?: (rawContent: string, filename: string) => void;
}

export function ResumeUploader({ onSuccess }: ResumeUploaderProps) {
  const { setMasterResumeText } = useUIStore();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFile = async (selectedFile: File) => {
    if (!selectedFile.name.endsWith(".tex") && !selectedFile.name.endsWith(".txt")) {
      setStatusMsg({ type: "error", text: "Only .tex or .txt files are supported." });
      return;
    }

    setFile(selectedFile);
    setStatusMsg(null);
    setIsUploading(true);

    try {
      const text = await selectedFile.text();
      setMasterResumeText(text);

      // Upload to backend API endpoint POST /api/v1/resumes
      await uploadResumeFile(selectedFile, selectedFile.name.replace(/\.[^/.]+$/, ""));

      setIsUploading(false);
      setStatusMsg({ type: "success", text: `Successfully uploaded ${selectedFile.name}` });

      if (onSuccess) {
        onSuccess(text, selectedFile.name);
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
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
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
          accept=".tex,.txt"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-2">
          {isUploading ? (
            <Loader2 className="w-8 h-8 text-zinc-400 animate-spin" />
          ) : file ? (
            <FileText className="w-8 h-8 text-zinc-300" />
          ) : (
            <Upload className="w-8 h-8 text-zinc-500" />
          )}

          <div>
            <p className="text-sm font-medium text-zinc-200">
              {file ? file.name : "Upload LaTeX (.tex) or Text (.txt) Resume"}
            </p>
            <p className="text-xs text-zinc-500 mt-0.5">
              Drag and drop your file here or click to browse files
            </p>
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
          {statusMsg.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0" />
          )}
          <span>{statusMsg.text}</span>
        </div>
      )}
    </div>
  );
}
