"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";
import { LogOut, Database } from "lucide-react";

export function Navbar({ onOpenData }: { onOpenData?: () => void }) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  return (
    <header className="sticky top-0 z-50">
      <div className="glass-panel-sm mx-4 md:mx-8 mt-3 px-5 h-12 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center font-bold text-white text-xs shadow-lg shadow-indigo-500/20">
            T
          </div>
          <span className="font-semibold text-sm tracking-tight text-zinc-100">Tailr</span>
        </div>

        <div className="flex items-center gap-2">
          {user && (
            <>
              <button
                onClick={onOpenData}
                className="btn-ghost px-2.5 py-1.5 text-xs rounded-lg flex items-center gap-1.5"
              >
                <Database className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Data</span>
              </button>
              <span className="text-xs text-zinc-600 hidden md:inline mx-1">{user.email}</span>
              <button
                onClick={() => { logout(); router.push("/login"); }}
                className="btn-ghost px-2 py-1.5 text-xs rounded-lg"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
