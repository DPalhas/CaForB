# Frontend conventions

## Naming
- PascalCase for components and files; `useXxx` for hooks; lowercase `xxx.ts` for lib modules.
- Domain/GraphQL types live in `lib/types.ts` — never re-declare a local interface.
- One concept, one name: maturity banding = `scoreTier()` (3-tier) and `scoreBand()` (4-tier, ScoreCard only — distinct scale, do not merge).

## Folder structure
- Route code co-locates under `app/<route>/`; its components in `app/<route>/components/`.
- Cross-route shared UI in `components/`; primitives in `components/ui/`.
- Data hooks in `lib/hooks/`; GraphQL ops in `lib/graphql/`; pure helpers in `lib/`.

## State rule
- Server data via hooks in `lib/hooks/` (Apollo), not raw `useQuery` in components.
- Auth via `AuthProvider`/`useAuth`. Prefer derived values (`useMemo`) over `useEffect` syncing.

## Styling
- Tailwind utility classes. Shared class strings → extracted components/constants.
- Semantic color tokens live in `globals.css` and hold the exact literal values currently in use; use tokens over bare hex/rgba where CSS `var()` is supported (not in SVG presentation attributes — see `lib/score.ts`).
- **Color palette intentionally left unchanged during the 2026 refactor** — no colors added, removed, or adjusted. The pre-existing terracotta/sage `:root` set is retained; it is used only by `PageBackground`/shadcn until a later migration phase.
- Motion variants/easing import from `lib/motion.ts`.

## Verification
- `npm run build` (TypeScript + Next.js production build) is the authoritative gate; `npm run lint` (ESLint); `npm test` (Vitest) for unit/snapshot tests.
