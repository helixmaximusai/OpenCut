# HelixBuilds demo/preview — W&T checklist

**DRAFT / branch-only.** Do not merge. Do not mark ready. Do not publish. Do not deploy. Do not open Cloudflare billing, Workers, or Pages. **$0.**

SoT: helix-vault `_system/2026-09-14-mattyp-x-bookmarks-loop.md` ([PR #54](https://github.com/helixmaximusai/helix-vault/pull/54) MERGED). KEEP Helix-meta / promote-on-green. Cloudflare preview = RESEARCH until Nick writes a cap.

**PASS ≠ GREEN ≠ live.** A check that cannot FAIL is not a check. Skills/routines only after W&T green **and** Nick.

published: **NOTHING.** Law 5. **H-01** (HelixBuilds OpenCut host HOLD — absorb, do not fork; never merge/deploy/publish from this packet). Cap **$0**.

---

## 1. Branch-only (never `main`)

- [ ] Work is on a feature branch. Never commit to `main` (Law 3).
- [ ] Base: `helix/working-and-tested` @ `5d5cbad4334e13b958d226f1cb3d424998d95f3c` (draft [PR #1](https://github.com/helixmaximusai/OpenCut/pull/1)).
- [ ] If classic `bun run build` fails Next typecheck on that tip, use `cursor/classic-next-pin-build-0e4c` @ `ac431055cd8525a193b48d3c215c5b83b806f373` (draft [PR #3](https://github.com/helixmaximusai/OpenCut/pull/3) — pin Next **16.1.3** so workspace `next@^16.1.3` cannot hoist 16.2.4).
- [ ] PR stays **draft**. Do not merge. Do not mark ready.

## 2. Build (classic, placeholder env)

From `classic/` with [Bun](https://bun.sh). Placeholders only. Docker/Redis/Postgres are **not** required for the production build. No fal.ai. No paid APIs.

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

On **PR #3** (`ac431055`), classic root `build` is aliased to `build:web`. On **W&T tip** (`5d5cbad`), run `bun run build` from `classic/apps/web` (same placeholder env) if the root has no `build` script.

- [ ] `bun install` exit **0**
- [ ] `bun run build` exit **0**
- [ ] If typecheck fails with Next **16.2.4** vs apps/web **16.1.3**, stop quoting W&T tip as green for this check — cite PR #3 and re-run on `ac431055`. Do not fake green.

## 3. Local preview only — Cloudflare forbidden

**Allowed** (localhost, no CF):

```sh
cd classic
bun install
bun run dev:web
# or: cd apps/web && bun run dev
```

Classic README: app at [http://localhost:3000](http://localhost:3000). After a green `bun run build`, local `cd apps/web && bun run start` is also allowed (still localhost).

**Forbidden until Nick writes a CF cap** (do not run, do not wire, do not open billing):

| Command / surface | Why forbidden |
|---|---|
| `bun run preview` / `preview:web` in classic | `opennextjs-cloudflare build && opennextjs-cloudflare preview` |
| `bun run deploy` / `deploy:web` | `opennextjs-cloudflare deploy` |
| `wrangler` (any) | Workers / Pages |
| Cloudflare dashboard, billing, Workers, Pages, secrets | RESEARCH only. This packet must **not** enable CF. |

- [ ] Previewed on **localhost** only (`dev` or local `start`)
- [ ] Did **not** run wrangler / OpenNext CF preview / CF deploy
- [ ] Did **not** open Cloudflare billing / Workers / Pages

## 4. Screenshot validation before GREEN

SoT KEEP: screenshot / video validation before treating a demo as reviewed. Same as fail-closed / W&T: a check that cannot FAIL is not a check.

- [ ] Human (or agent with a recorded screenshot) opened the local preview
- [ ] Screenshot (or video) of the demo UI is attached to the draft PR / packet
- [ ] **Do not call GREEN** from `bun run build` exit 0 alone. Build PASS ≠ preview validated.

## 5. PASS ≠ GREEN ≠ live

| Token | Means | Does **not** mean |
|---|---|---|
| **PASS** | A named command exited 0 (install, build, local dev came up) | The demo is promoted |
| **GREEN** | W&T: build PASS **and** screenshot-validated local preview, on a branch | Live, merged, or a skill |
| **live** | Public URL / `main` / published artifact | Anything this packet may do |

- [ ] Skills / routines **not** installed. Only after W&T green **and** Nick.
- [ ] Auto-merge / auto-publish **not** enabled (SoT DROP).
- [ ] published **NOTHING**
- [ ] Law 5 held (MERGES / MONEY / CREDITS / PUBLISHING)
- [ ] **H-01** held (this host is absorb-only; not a parallel product)
- [ ] **$0** — no CF spend, no fal.ai, no Higgs, no paid APIs

## 6. Still fail (do not fake)

Same as the editing-host candidate; this packet does not claim them green:

- `cd classic && bun test` — published `opencut-wasm` (`wasm.__wbindgen_start is not a function`)
- `bun run build:wasm` / rewrite `cargo check` — need Rust edition 2024
- Live auth/DB/Redis/Freesound/Marble — placeholders only
- Desktop / GPUI — not a headless Linux GUI
- Cloudflare preview — **not run**. RESEARCH until Nick caps.
