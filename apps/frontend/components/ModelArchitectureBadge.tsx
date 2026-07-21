"use client";

import { Cpu } from "lucide-react";

export function ModelArchitectureBadge() {
  const agents = [
    { name: "JD Extraction", model: "Qwen 3 (8B)" },
    { name: "Planner", model: "Qwen 3 (14B)" },
    { name: "Rewriter", model: "Llama 3.1 (8B)" },
    { name: "ATS Advisor", model: "Gemma 3 (9B)" },
  ];

  return (
    <div className="min-panel p-4 space-y-3">
      <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
        <span className="flex items-center gap-1.5 text-zinc-200 font-semibold">
          <Cpu className="w-4 h-4 text-zinc-400" /> Multi-Agent AI Model Allocation
        </span>
        <span className="font-mono text-[11px] text-zinc-500">Agent Architecture Sec. 16</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {agents.map((agent, idx) => (
          <div key={idx} className="bg-zinc-900/90 border border-zinc-800 rounded-md p-2.5 space-y-1">
            <div className="text-[11px] font-medium text-zinc-400">{agent.name}</div>
            <div className="text-xs font-mono font-semibold text-zinc-200">{agent.model}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
