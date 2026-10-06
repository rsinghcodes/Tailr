'use client';

import { useAuthStore } from '@/lib/auth-store';
import { Database, LogOut, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function Navbar({ onOpenData }: { onOpenData?: () => void }) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  return (
    <header className="sticky top-0 z-50">
      <div
        className="glass-panel-sm mx-4 md:mx-6 mt-4 px-6 h-16 flex items-center justify-between"
        style={{ borderRadius: '20px' }}
      >
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-2xl flex items-center justify-center font-bold text-sm"
            style={{
              background: '#18181b',
              color: '#ffffff',
            }}
          >
            T
          </div>
          <div>
            <div className="font-bold text-base tracking-tight" style={{ color: 'var(--md-on-bg)', letterSpacing: '-0.02em' }}>
              Tailr
            </div>
            <div className="text-[11px] font-medium" style={{ color: 'var(--md-on-surface-v)', letterSpacing: '0.01em' }}>
              AI Resume Intelligence
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {user && (
            <>
              <button
                onClick={onOpenData}
                className="btn btn-secondary py-2 px-4 text-sm gap-2"
              >
                <Database className="w-4 h-4" />
                <span className="hidden sm:inline">My Data</span>
              </button>

              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full"
                style={{ background: 'var(--md-surface-c3)', border: '1px solid var(--md-outline)' }}>
                <div className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold"
                  style={{ background: 'var(--md-primary-c)', color: 'var(--md-on-primary-c)' }}>
                  {user.email?.[0]?.toUpperCase() ?? 'U'}
                </div>
                <span className="text-xs font-medium" style={{ color: 'var(--md-on-surface-v)' }}>
                  {user.email}
                </span>
              </div>

              <button
                onClick={() => { logout(); router.push('/login'); }}
                className="btn btn-ghost p-2.5 rounded-xl"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
