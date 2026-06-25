# Work Log

Every session must: read this first, write an entry before stopping, never commit over an uncommitted entry without resolving it.

---

## HOW TO USE

At session start: read every entry since the last commit. If anything says "uncommitted," handle it before writing new code on top.

At session end:
```
## YYYY-MM-DD — [Bot or session name]
**Working on:**
**Files changed:**
**Committed:** YES — [hash] / NO
**Uncommitted:**
**Notes for next session:**
```

If you find an uncommitted entry from another bot: do not overwrite. Commit it or ask Gabby first.

---


## 2026-06-25 — Embed Veo & Digo Spanish app into Pebble
**Working on:** Added an "Español" page to Pebble that embeds the standalone Veo & Digo Spanish-learning artifact (flashcards, stories, phrases, worksheet, journal, builder).
**Files changed:** `pebble-app.html` — added `VEO_DIGO_B64` base64 const + `EspanolPage` component (before `App()`), appended `EspanolPage` to `staticPages`, added `'Español'` to `PAGE_LABELS`.
**How:** Bake-in approach. Veo HTML base64-encoded into a JS const, decoded at runtime (`atob` + `TextDecoder('utf-8')` so Spanish accents render) into an `<iframe srcDoc>` on a new vertical swipe page. Fully self-contained, no external deps. Verified the embed renders via an isolated test (`/tmp/veo-embed-test.html`); app boots with no JS errors and "Español" appears in nav.
**Committed:** YES — this commit
**Uncommitted:** none
**Notes for next session:** Español is the LAST swipe page; reached via jar/tabs/pebbles nav. Veo uses NO localStorage (in-memory only) so the Diario/progress reset on reload — could wire real persistence later. Source artifact: `~/Downloads/veo-y-digo.html`. Pre-change baseline is commit 08acdb1.

## 2026-06-25 — Atajos (gerund / progressive) section added to Veo & Digo
**Working on:** New "Atajos" (shortcuts) section in the embedded Veo & Digo Spanish app — the `estaba + gerundio` ("I was ___ing") hack as reference + drill.
**Files changed:** `pebble-app.html` (re-baked `VEO_DIGO_B64` with updated Veo source); added `veo-y-digo-source.html` (editable un-baked source of the embedded app).
**What:** Home card "Atajos" → `#atajos` screen with: the `-ar→-ando` / `-er/-ir→-iendo` rule, a typed drill (random infinitive+English → type the gerundio → Revisar checks accent-insensitively, shows the `estaba` example + o→u/e→i/i→y reason for irregulars, running score), and collapsible reference tables (regular -ar, regular -er/-ir, irregulars w/ "Por qué", `estaba` conjugations). Registered `'atajos'` in `screens`; `openAtajos()/atNext()/atCheck()/atBuildRef()` JS; scoped `.at-*` CSS on the app's terracotta/olive/gold tokens. Verified inside a 375px frame (matches Pebble's iframe).
**Committed:** YES — this commit
**Notes for next session:** Edit the embedded app via `pebble/veo-y-digo-source.html`, then re-base64 it into `pebble-app.html`'s `VEO_DIGO_B64` const (the `const VEO_DIGO_B64 = "...";` line). Dropped the redundant "Ejemplo" column from the regular tables to fit phone width (every example is just `estaba `+gerund). Atajos is the home for future helper-verb hacks (`voy a`+inf, `tengo que`+inf, `acabo de`+inf, `estoy`+gerund). Veo has no persistence, so drill score resets on reload.
