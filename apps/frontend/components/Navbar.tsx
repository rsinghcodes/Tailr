"use client";

"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";
import { ShieldCheck, LogOut, Database } from "lucide-react";

export function Navbar({ onOpenData }: { onOpenData?: () => void }) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-zinc-100 flex items-center justify-center font-bold text-zinc-950 text-xs">
            T
          </div>
          <span className="font-semibold text-base tracking-tight text-zinc-100">
            Tailr
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
            v1.0
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Guardrails Active</span>
          </div>
          {user && (
            <div className="flex items-center gap-2">
              <button
                onClick={onOpenData}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                title="Manage Data"
              >
                <Database className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">My Data</span>
              </button>
              <span className="text-xs text-zinc-400 font-mono hidden sm:inline">{user.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs text-zinc-400 hover:text-rose-400 hover:bg-zinc-800 transition-colors"
                title="Logout"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
