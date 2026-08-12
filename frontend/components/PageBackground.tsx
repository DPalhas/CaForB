"use client";

import { motion } from "framer-motion";

type Variant = "hero" | "default" | "assessment" | "results" | "auth";

interface Props {
  variant?: Variant;
}

const gridSvg = `url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='30' cy='30' r='0.8' fill='rgba(255,255,255,0.04)'/%3E%3C/svg%3E")`;

export default function PageBackground({ variant = "default" }: Props) {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {variant === "hero" && (
        <>
          <div
            className="absolute inset-0 opacity-60"
            style={{
              backgroundImage: gridSvg,
              backgroundSize: "60px 60px",
            }}
          />
          <motion.div
            className="absolute top-0 left-0 w-full h-1/2 opacity-[0.08]"
            style={{
              background:
                "radial-gradient(ellipse at 20% 0%, var(--primary) 0%, transparent 70%)",
            }}
            animate={{ opacity: [0.05, 0.1, 0.05] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
        </>
      )}

      {variant === "assessment" && (
        <>
          <div className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 47px, rgba(255,255,255,0.3) 47px, rgba(255,255,255,0.3) 48px)`,
            }}
          />
          <div className="absolute left-0 top-0 w-px h-full bg-gradient-to-b from-amber-500/40 via-transparent to-transparent" />
          <div className="absolute left-1/4 top-0 w-px h-full bg-gradient-to-b from-transparent via-transparent to-transparent" />
        </>
      )}

      {variant === "results" && (
        <>
          <div className="absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpolygon points='40,5 75,25 75,65 40,85 5,65 5,25' fill='none' stroke='rgba(251,146,60,0.3)' stroke-width='0.5'/%3E%3Cpolygon points='40,30 55,38 55,52 40,60 25,52 25,38' fill='none' stroke='rgba(16,185,129,0.3)' stroke-width='0.5'/%3E%3C/svg%3E")`,
              backgroundSize: "160px 160px",
              backgroundPosition: "center",
            }}
          />
          <motion.div
            className="absolute bottom-0 right-0 w-1/2 h-1/2 opacity-[0.06]"
            style={{
              background:
                "radial-gradient(ellipse at bottom right, rgba(16,185,129,0.6) 0%, transparent 70%)",
            }}
            animate={{ scale: [1, 1.05, 1], opacity: [0.04, 0.08, 0.04] }}
            transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
          />
        </>
      )}

      {variant === "auth" && (
        <motion.div
          className="absolute -top-20 -left-20 w-64 h-64 rounded-full blur-3xl"
          style={{ background: "var(--primary)" }}
          animate={{ opacity: [0.08, 0.15, 0.08], scale: [1, 1.05, 1] }}
          transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        />
      )}

      {variant === "default" && (
        <>
          <div
            className="absolute inset-0 opacity-40"
            style={{
              backgroundImage: gridSvg,
              backgroundSize: "72px 72px",
            }}
          />
          <motion.div
            className="absolute -top-20 right-0 w-72 h-72 rounded-full blur-3xl"
            style={{ background: "var(--primary)" }}
            animate={{ opacity: [0.04, 0.09, 0.04] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          />
        </>
      )}

      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          opacity: 0.03,
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}
