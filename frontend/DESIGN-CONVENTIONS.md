# Design conventions

Visual standards established during the 2026 visual refactor. Apply these to any new UI.

## Spacing scale
`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64` (4pt base). No `.5` steps (`p-3.5`, `py-2.5`, `gap-1.5`, …).
- `4/8` micro-gaps (icon-to-label, inline chips)
- `12/16` field & control padding
- `24` section spacing
- `32/48/64` page/section rhythm

## Type scale
- `display` `text-4xl sm:text-5xl` (hero only)
- `h1` `text-3xl font-bold`
- `h2` `text-xl font-semibold`
- `h3` `text-base font-semibold`
- `body` `text-sm`
- `caption`/label `text-xs font-medium`
- `mono` `text-sm font-mono` (scores/percentages only)

Fonts: DM Sans (body), JetBrains Mono (`--font-mono`, numeric values only). No `text-[10px]`/`text-[11px]`/`text-6xl`.

## Radius
- controls (buttons/inputs/selects): `rounded-lg` (8px) — token `--radius-control`
- cards/panels: `rounded-xl` (12px) — token `--radius-card`
- pills/badges: `rounded-full`
No `rounded-2xl`/`rounded-3xl` on containers or buttons. Radius tokens defined in `globals.css` `@theme`.

## Shadow
- cards: `shadow-sm`
- floating panel (ChatPanel): `shadow-lg`
- no shadows on buttons, inputs, or pills; no colored (`shadow-amber-*`) glows.

## Components (single source of truth)
- `components/ui/button.tsx` → `Button` / `buttonVariants` (`primary | secondary | destructive | ghost` × `sm | md | lg`)
- `components/ui/card.tsx` → `Card`
- `components/ui/badge.tsx` → `Badge` (`default | primary`)
- `components/ui/loading.tsx` → `LoadingState`
- `components/ui/error-state.tsx` → `ErrorState`
- `components/ui/empty-state.tsx` → `EmptyState`
- Assessment-only primitives: `app/assessment/components/SectionBadge.tsx`, `SelectField.tsx`
- Score/status color helpers live in `lib/score.ts` (`scoreTier`, `scoreBand`) — do not re-implement per-component.

## Interaction states
- hover: `primary` → `hover:bg-amber-300`; `secondary` → `hover:bg-stone-800`; `ghost` → `hover:text-white`
- focus-visible: `focus-visible:ring-2 focus-visible:ring-amber-500/50` on every control
- disabled: `disabled:opacity-50 disabled:cursor-not-allowed` (use `disabled:pointer-events-none`)

## Iconography
Icons only where they convey meaning: trend arrows, error/status indicators, list chevrons, nav actions (logout), and empty-state illustrations. No decorative icons on section headers, buttons, badges, or form fields.

## Layout
- `max-w-2xl` forms/auth · `max-w-4xl` lists/dashboards · `max-w-6xl` marketing · `max-w-7xl` results
- Content left-aligned by default; center only for empty states, the onboarding hero, and auth card headers.

## Color
Palette preserved verbatim from the 2026 refactor. No new hues, no adjusted brand colors; fix contrast within existing colors only.
