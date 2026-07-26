"use client";

import { useEffect, useState } from "react";
import { Server, Database, Cpu, Zap, RefreshCw, CheckCircle2, XCircle } from "lucide-react";
import { checkHealth, SystemHealthResponse, ServiceHealthDetail } from "../lib/api";

export function SystemHealthGrid() {
  const [healthData, setHealthData] = useState<SystemHealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchHealth = async () => {
    setIsLoading(true);
    try {
      const res = await checkHealth();
      setHealthData(res);
    } catch {
      setHealthData(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const services = [
    { key: "postgres", label: "PostgreSQL Database", icon: Database },
    { key: "redis", label: "Redis Cache & Locks", icon: Zap },
    { key: "qdrant", label: "Qdrant Vector Store", icon: Server },
    { key: "ollama", label: "Ollama AI Container", icon: Cpu },
  ];

  return (
    <div className="min-panel p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div>
          <h3 className="text-base font-semibold text-zinc-100 flex items-center gap-2">
            <Server className="w-5 h-5 text-zinc-400" /> System Infrastructure Health Diagnostics
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Real-time pre-flight diagnostic probes testing PostgreSQL, Redis, Qdrant, and Ollama Docker.
          </p>
        </div>
        <button
          onClick={fetchHealth}
          disabled={isLoading}
          className="min-button min-button-secondary text-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} /> Refresh Probe
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {services.map((svc) => {
          const Icon = svc.icon;
          const detail: ServiceHealthDetail | undefined = healthData?.services?.[svc.key];
          const isOnline = detail?.online ?? false;

          return (
            <div key={svc.key} className="min-card p-4 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                  <Icon className="w-4 h-4 text-zinc-400" /> {svc.label}
                </div>
                {isOnline ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : (
                  <XCircle className="w-4 h-4 text-rose-400" />
                )}
              </div>

              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-zinc-500">Status:</span>
                <span className={isOnline ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                  {isOnline ? "ONLINE" : "OFFLINE"}
                </span>
              </div>

              {detail?.latency_ms !== undefined && (
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-zinc-500">Latency:</span>
                  <span className="text-zinc-300">{detail.latency_ms} ms</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
