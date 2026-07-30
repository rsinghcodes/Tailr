"use client";

import { useEffect, useState, startTransition, type ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/auth-store";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuthStore();
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    useAuthStore.getState().hydrate();
    startTransition(() => setHydrated(true));
  }, []);

  useEffect(() => {
    if (hydrated && !user && pathname !== "/login") {
      router.push("/login");
    }
  }, [hydrated, user, pathname, router]);

  if (!hydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin" />
          <span className="text-sm text-zinc-500">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user && pathname !== "/login") return null;

  return <>{children}</>;
}
