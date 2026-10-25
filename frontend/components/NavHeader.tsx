"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Cpu, Loader2, LogOut } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";

export default function NavHeader() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full bg-stone-950/80 border-b border-stone-800/80 px-6 lg:px-12 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-lg bg-amber-400 flex items-center justify-center">
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
                className="hidden sm:flex text-xs font-semibold text-stone-400 hover:text-white transition"
              >
                My Assessments
              </Link>
              <span className="hidden sm:flex text-sm text-stone-400">
                {user.username}
              </span>
              <Button variant="secondary" size="sm" onClick={() => logout()}>
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </Button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className={buttonVariants({ variant: "ghost", size: "sm" })}
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className={buttonVariants({ variant: "primary", size: "sm" })}
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
