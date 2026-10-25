"use client";

type Variant = "hero" | "default" | "assessment" | "results" | "auth";

interface Props {
  variant?: Variant;
}

const gridSvg = `url("data:image/svg+xml,%3Csvg width='60' height='60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='30' cy='30' r='0.8' fill='rgba(255,255,255,0.04)'/%3E%3C/svg%3E")`;

export default function PageBackground({ variant = "default" }: Props) {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {variant === "hero" && (
        <div
          className="absolute inset-0 opacity-60"
          style={{
            backgroundImage: gridSvg,
            backgroundSize: "60px 60px",
          }}
        />
      )}

      {variant === "assessment" && (
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 47px, rgba(255,255,255,0.3) 47px, rgba(255,255,255,0.3) 48px)`,
          }}
        />
      )}

      {variant === "results" && (
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpolygon points='40,5 75,25 75,65 40,85 5,65 5,25' fill='none' stroke='rgba(251,146,60,0.3)' stroke-width='0.5'/%3E%3Cpolygon points='40,30 55,38 55,52 40,60 25,52 25,38' fill='none' stroke='rgba(16,185,129,0.3)' stroke-width='0.5'/%3E%3C/svg%3E")`,
            backgroundSize: "160px 160px",
            backgroundPosition: "center",
          }}
        />
      )}

      {(variant === "default" || variant === "auth") && (
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: gridSvg,
            backgroundSize: "72px 72px",
          }}
        />
      )}
    </div>
  );
}
