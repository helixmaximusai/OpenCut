---
name: helixbuilds-editing-host
description: Use when working on HelixBuilds editing (faceless YouTube pipeline) hosted in helixmaximusai/OpenCut. Absorb OpenCut — do not fork a parallel editor. Covers when-to-use, $0 constraints, and the classic/ bun install + bun run build verify path.
---

# HelixBuilds editing host (OpenCut absorb)

**Candidate only.** Lives in-repo at `skill-candidates/helixbuilds-editing-host/SKILL.md`. Do not install this into a user skill library. Do not merge. Do not publish. Do not deploy to opencut.app or Vercel. **$0** — no fal.ai, no paid APIs.

## When to use

Use this host when the task is **HelixBuilds editing** (faceless YouTube pipeline) and the code lives in `helixmaximusai/OpenCut`.

- **Absorb, do not fork.** OpenCut *is* HelixBuilds editing. Do not create a new desk, vault, editor stack, or venture repo.
- Positioning: a HelixBuilds editing tool **based on OpenCut** — not a second CapCut business.
- **Runnable editor = classic.** Upstream `main` is a rewrite (hello-world / "Editor coming soon"). The working tree is `helix/working-and-tested` (draft PR #1). Classic is vendored at `classic/` (pin `OpenCut-app/opencut-classic` `cf5e79e`, see `classic/.helix-classic-sha`).
- **Green classic build** requires the Next 16.1.3 pin on `cursor/classic-next-pin-build-0e4c` (draft PR #3) until that pin is absorbed. Without it, workspace `next@^16.1.3` hoists 16.2.4 and `bun run build` fails typecheck in `next.config.ts`.

Do **not** use this skill for the rewrite at repo-root `apps/web`, desktop/GPUI, wasm rebuilds, or live auth/DB/Redis/Freesound/Marble.

## Verify

On `cursor/classic-next-pin-build-0e4c` (or a descendant that keeps the Next pin). Placeholders only — Docker/Postgres/Redis are not required for the production build.

```sh
cd classic
bun install
export DATABASE_URL="postgresql://opencut:opencut@localhost:5432/opencut"
export BETTER_AUTH_SECRET="supersecret-helix-working-and-tested-32"
export NEXT_PUBLIC_SITE_URL="http://localhost:3000"
export UPSTASH_REDIS_REST_URL="https://your-upstash-redis-url"
export UPSTASH_REDIS_REST_TOKEN="your-upstash-redis-token"
export NEXT_PUBLIC_MARBLE_API_URL="https://placeholder.example.com"
export MARBLE_WORKSPACE_KEY="placeholder"
export FREESOUND_CLIENT_ID="placeholder"
export FREESOUND_API_KEY="placeholder"
bun run build
```

**Pass:** both commands exit 0. Expect Next.js 16.1.3, TypeScript, and 18 generated routes.

### Re-verified (do not merge)

| Ref | Tip SHA | Notes |
|---|---|---|
| `origin/main` | `400f097becba5db0fbc305d5a65348cb81c20356` | Rewrite; not the editor |
| PR #1 `helix/working-and-tested` | `5d5cbad4334e13b958d226f1cb3d424998d95f3c` | Open draft. Host + classic vendor. Do not merge/deploy |
| PR #3 `cursor/classic-next-pin-build-0e4c` | `ac431055cd8525a193b48d3c215c5b83b806f373` | Open draft. `bun install` **0**, `bun run build` **0** |

## Still fail (do not fake green)

- `cd classic && bun test` — published `opencut-wasm` (`wasm.__wbindgen_start is not a function`)
- `bun run build:wasm` / rewrite `cargo check` — need Rust edition 2024; rustc 1.83 cannot compile
- Live services (auth, DB, Redis, Freesound, Marble) — placeholders only
- Desktop / GPUI — not a headless Linux GUI
