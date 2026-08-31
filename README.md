<table width="100%">
  <tr>
    <td align="left" width="120">
      <img src="https://assets.opencut.app/branding/symbol.svg" alt="OpenCut Logo" width="100" />
    </td>
    <td align="right">
      <h1>OpenCut</h1>
      <h3 style="margin-top: -10px;">HelixBuilds editing tool (faceless YouTube pipeline), based on OpenCut.</h3>
    </td>
  </tr>
</table>

## HelixBuilds editing (code host only)

**Absorb, do not fork a parallel product.** This repository (`helixmaximusai/OpenCut`) is the **code host** for HelixBuilds’ editing tool. OpenCut *is* HelixBuilds editing — the faceless YouTube pipeline — not a new desk, vault, editor stack, or venture repo.

Positioning: a **HelixBuilds editing tool, based on OpenCut**. Not a second CapCut business and not a CapCut clone-in-name.

Do **not** create another repo for this. Do **not** publish. Do **not** deploy to opencut.app or Vercel. $0: no fal.ai spend and no paid APIs.

`helix/working-and-tested` is the working tree on this host. Upstream OpenCut `main` is a rewrite and is **not contribution-ready**. The runnable editor is still [opencut-app/opencut-classic](https://github.com/opencut-app/opencut-classic) ([opencut.app](https://opencut.app) still runs classic). This branch vendors that classic tree under [`classic/`](classic/) so the HelixBuilds editing tool has a command that actually exits 0.

### Verified command (exit 0)

From this repo, after installing [Bun](https://bun.sh):

```sh
cd classic
bun install
cd apps/web
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

That is the same `apps/web` `bun run build` classic CI runs. Placeholders only; Docker/Redis/Postgres are not required for the production build.

Classic source pin: [`classic/.helix-classic-sha`](classic/.helix-classic-sha) (`OpenCut-app/opencut-classic` `cf5e79e`).

### What still fails (not faked green)

- **`cd classic && bun test`**: 4 files still error when Bun loads published `opencut-wasm` (`wasm.__wbindgen_start is not a function`). Remaining tests pass, including keybinding persistence after host type-guard fixes.
- **Local WASM rebuild** (`bun run build:wasm`): classic `rust/wasm` needs Rust edition 2024; this environment’s `rustc 1.83.0` cannot compile it.
- **Rewrite at repo root** (`apps/web`): `bun run build` exits 0, but the UI is still “hello world” / “Editor coming soon”. `bun run test` fails (`depsOptimizer is required in dev mode`). Desktop `cargo check` fails on the same Rust 1.83 / edition 2024 mismatch. Documented `proto` / `moon` are not installed here.
- **Desktop / GPUI** (rewrite and classic): not a headless Linux GUI; not verified as an interactive app.
- **Auth/DB/Redis/Freesound/Marble**: build uses placeholders. Live editor features that need those services are unverified. No fal.ai.

Compile fixes on this host (missing runtime type guards and leftover positional-arg calls after object-params refactors) live in `classic/apps/web/src`.

[![Discord](https://img.shields.io/discord/1386309140057690133?label=Discord&logo=discord&logoColor=fff&color=5865F2&style=flat)](https://discord.gg/zmR9N35cjK)
[![X](https://img.shields.io/badge/follow-%40opencutapp-000?logo=x&logoColor=fff&style=flat)](https://x.com/opencutapp)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

## Status

**OpenCut is being rewritten from the ground up.** What's coming:

- An Editor API
- First-class third party plugins (made possible by a plugin-first architecture)
- Desktop, mobile, and browser from one codebase (Rust core)
- MCP server (for AI agents)
- Headless mode (automation, batch rendering)
- A scripting tab directly in the editor

You can still find the previous version at [opencut-app/opencut-classic](https://github.com/opencut-app/opencut-classic), which is the one to reach for today. [opencut.app](https://opencut.app) still runs the classic version. The rewrite will live at [new.opencut.app](https://new.opencut.app) until it's ready to take over.

HelixBuilds does not replace that with a new editor stack. This host absorbs classic so HelixBuilds editing can run.

## Development

Install [proto](https://moonrepo.dev/proto) if you haven't already:

**Linux, macOS, WSL:**

```sh
bash <(curl -fsSL https://moonrepo.dev/install/proto.sh)
```

**Windows (PowerShell):**

```powershell
irm https://moonrepo.dev/install/proto.ps1 | iex
```

If shims fail to run, allow local scripts for your user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

From the repo root (rewrite scaffold):

```sh
proto use    # installs the tools pinned in .prototools
```

```sh
moon run web:dev       # localhost:5173
moon run api:dev       # localhost:8787
moon run desktop:dev   # see apps/desktop/README.md
```

For the HelixBuilds editing tool on this host, use `classic/` and the verified `bun run build` command above. Do not stand up a second product repo.

## Contributing

We're not set up to take outside contributions yet while the architecture is being designed. If you want to follow along, ask questions, or just hang out, [join the Discord](https://discord.gg/zmR9N35cjK) or [open an issue](https://github.com/opencut-app/opencut/issues).

## Sponsors

OpenCut is supported by companies that believe in open source creator tools.

- [**fal.ai**](https://fal.ai?utm_source=github-opencut&utm_campaign=oss): Generative image, video, and audio models all in one place.

Want your logo here? Reach out at [sponsor@opencut.app](mailto:sponsor@opencut.app).

## License

[MIT](LICENSE)
