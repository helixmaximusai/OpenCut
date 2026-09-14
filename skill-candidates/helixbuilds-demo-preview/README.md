# HelixBuilds demo/preview on OpenCut (draft)

**DRAFT PACKET.** Do not merge. Do not publish. Do not deploy. Do not enable Cloudflare. **$0.**

OpenCut (`helixmaximusai/OpenCut`) is the **classic demo + local-preview surface** for HelixBuilds editing. Bookmarks ingest already exists elsewhere. This host is not a new venture and not a [cobe](https://github.com/shuding/cobe) clone.

Binding SoT: helix-vault `_system/2026-09-14-mattyp-x-bookmarks-loop.md` ([PR #54](https://github.com/helixmaximusai/helix-vault/pull/54) MERGED). KEEP **Helix-meta / promote-on-green**. Cloudflare preview = **RESEARCH** until Nick writes a cap.

| File | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | When-to-use (candidate only — do not install) |
| [`W-AND-T.md`](W-AND-T.md) | Branch / build / local-preview / screenshot / PASS≠GREEN checklist |

## mattyp steps → Helix

Daily loop claimed in the X post ([mattyp](https://x.com/mattyp/status/2099482348010328185)): Grok reads X Bookmarks → Cursor Agent builds a demo → screenshot/video validate → branch with a preview link → morning link for a human.

| mattyp step | Helix land | On **this** host? |
|---|---|---|
| 1. Scan X Bookmarks | research-backlog #5 `xfeed.py` / social-as-memory (ingest already built; OAuth keys still human) | **No.** Do not re-implement ingest here. |
| 2. Cursor Agent builds a demo | Cloud agents on librarian/research branches. Branch-only (Law 3). Do **not** auto-ship. | **Yes — demo code** on `helix/working-and-tested` (or PR #3 Next pin if classic build needs it). |
| 3. Screenshot / video validate | Harness / W&T promote-on-green. A check that cannot FAIL is not a check. | **Yes.** Required before GREEN. See [`W-AND-T.md`](W-AND-T.md) §4. |
| 4. Branch + preview | Law 3 branch-only. Preview = human review, not publish. CF Pages/Workers = RESEARCH, **no spend**. Prefer existing local preview. | **Yes — local only:** `cd classic && bun run dev:web` → `http://localhost:3000`. **Forbid** wrangler / OpenNext CF deploy. |
| 5. Morning link | Routine / CoS brief — human opens the link. | Localhost URL or draft-PR screenshots. Not a public CF URL. |

**DROP (SoT, not this host):** cobe as a Helix product; auto-merge / auto-publish / unattended spend.

## Pins (cite, do not merge)

| Ref | SHA | Role |
|---|---|---|
| SoT vault leaf PR #54 | MERGED on helix-vault | Paper KEEP / RESEARCH / DROP |
| OpenCut PR #1 `helix/working-and-tested` | `5d5cbad4334e13b958d226f1cb3d424998d95f3c` | Classic host. Draft HOLD. |
| OpenCut PR #3 `cursor/classic-next-pin-build-0e4c` | `ac431055cd8525a193b48d3c215c5b83b806f373` | Next 16.1.3 pin if W&T `bun run build` typecheck-fails |

## Will-not-do

- Will **not** write `main`.
- Will **not** open Cloudflare billing, Workers, or Pages; will **not** run wrangler / OpenNext CF preview or deploy.
- Will **not** clone cobe or add a `ventures.yaml` row.
- Will **not** auto-merge, auto-publish, remux Video #1, or spend Higgs.
- Will **not** install this candidate into a user skill library.

**published: NOTHING.** Law 5. H-01. **$0.** HOLD Nick MERGE.
