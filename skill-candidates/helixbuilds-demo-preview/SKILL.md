---
name: helixbuilds-demo-preview
description: Use when running HelixBuilds demo/preview W&T on the OpenCut classic host after an X-bookmark → Cursor agent demo. Branch-only local preview. Not a new venture. Not a cobe clone. Do not enable Cloudflare. Do not install into a user skill library.
---

# HelixBuilds demo/preview (OpenCut classic host)

**Candidate only.** Lives in-repo at `skill-candidates/helixbuilds-demo-preview/`. Do not install this into a user skill library. Do not merge. Do not publish. Do not deploy. Do **not** enable Cloudflare Workers/Pages. **$0.**

Binding SoT (MERGED paper): helix-vault `_system/2026-09-14-mattyp-x-bookmarks-loop.md` — [helix-vault PR #54](https://github.com/helixmaximusai/helix-vault/pull/54). KEEP **Helix-meta / promote-on-green**. Cloudflare preview is **RESEARCH only** until Nick writes a cap.

Sibling of the editing-host candidate (`skill-candidates/helixbuilds-editing-host/`). This packet is the **bookmark → demo → preview** surface on the same OpenCut host. It is **not** a new HelixBuilds product and **not** a cobe clone.

## When to use

Use this after an **X-bookmark → Cursor agent demo** lands on `helixmaximusai/OpenCut` and a human needs a **local preview** to screenshot-validate before calling W&T.

- **Grow pattern (mattyp):** bookmark → Cursor agent demo → preview link. Maps to Helix-meta. Do **not** auto-ship demos.
- **Host = this repo.** Absorb, do not fork. OpenCut *is* HelixBuilds editing. Do not add a `ventures.yaml` row. Do not clone [cobe](https://github.com/shuding/cobe) (SoT DROP as Helix product).
- **Ingest lives elsewhere.** Bookmarks scan is research-backlog #5 `xfeed.py` / social-as-memory. This host is **demo + preview only**.
- **Branch-only.** Never write `main`. Preview is human review, not publish (Law 3, Law 5).
- **Local preview only.** `bun run dev` / classic `bun dev:web` at `http://localhost:3000`. Screenshot validation is required before GREEN.
- **Cloudflare is RESEARCH, not this PR.** Do not run wrangler, `@opennextjs/cloudflare` preview/deploy, or CF Pages. No Workers/Pages wiring or secrets. Cap in writing before any CF bill. Nick decides.

Do **not** use this skill to open Cloudflare billing, merge to `main`, install a skill/routine, remux Video #1, spend Higgs, or stand up a new venture.

## Do not enable

| Action | Why |
|---|---|
| `wrangler` / `opennextjs-cloudflare preview` / `opennextjs-cloudflare deploy` | CF preview is RESEARCH until Nick caps. Classic `apps/web` `preview` and `deploy` scripts call OpenNext+Cloudflare — **do not run them**. |
| Cloudflare Workers / Pages / secrets | Out of scope. This PR must not enable CF. |
| Merge / auto-merge / auto-publish | Law 5. Nick decides. SoT DROP. |
| Install into a user skill library | Skills/routines only after W&T green **and** Nick. |
| Clone cobe / new `ventures.yaml` row | SoT DROP. Not a new venture. |
| Remux Video #1 / Higgs spend | CREDITS. $0 this packet. |

Checklist: [`W-AND-T.md`](W-AND-T.md). One-pager: [`README.md`](README.md).
