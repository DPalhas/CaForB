"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Cpu, Loader2, LogOut, User, History } from "lucide-react";

export default function NavHeader() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full backdrop-blur-md bg-stone-950/80 border-b border-stone-800/80 px-6 lg:px-12 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-amber-400 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Cpu className="w-5 h-5 text-stone-950 font-bold" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight group-hover:text-amber-400 transition">
            CaForB
          </span>
        </Link>

        <div className="flex items-center gap-3">
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin text-stone-500" />
          ) : user ? (
            <>
              <Link
                href="/dashboard"
                className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-stone-400 hover:text-amber-300 transition"
              >
                <History className="w-3.5 h-3.5" />
                <span>My Assessments</span>
              </Link>
              <span className="hidden sm:flex items-center gap-1.5 text-sm text-stone-400">
                <User className="w-4 h-4" />
                {user.username}
              </span>
              <button
                onClick={() => logout()}
                className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-stone-300 bg-stone-900/80 hover:bg-stone-800 rounded-xl transition border border-stone-800"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="px-3 py-2 text-xs font-semibold text-stone-300 hover:text-white transition"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-xs font-semibold text-stone-950 bg-amber-400 rounded-xl hover:bg-amber-300 transition shadow-lg shadow-amber-500/20"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
