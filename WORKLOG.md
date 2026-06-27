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

## 2026-06-25 — Natural Spanish audio (Kokoro) baked into Veo & Digo
**Working on:** Replaced the robotic browser voice with pre-generated natural Spanish audio for the flashcards and the Atajos hack.
**Files changed:** `pebble-app.html` (re-baked, now ~7.4MB), `veo-y-digo-source.html` (updated source).
**What:** Generated 559 MP3 clips locally with **Kokoro** (`em_alex`, speed 0.85, offline, no API/billing): 521 flashcard phrases ("article word", e.g. "el sol") + 38 Atajos phrases ("estaba "+gerund, plus `estaba` conjugations). Baked them as a base64 `FC_AUDIO` map inside the Veo app (~4.5MB). Added shared `fcPlay()` (plays baked audio, falls back to browser `SpeechSynthesis`). Flashcard `🔊 escuchar` → `fcPlay`. Atajos: `🔊` on each gerund in the reference tables AND in the drill reveal, plays the full **"estaba ___"**. Generators + integrator live in session scratchpad (`generate_fc_audio.py`, `generate_atajos_audio.py`, `integrate_audio.py`).
**Why Kokoro not Google:** the shared `GOOGLE_TTS_API_KEY` (same key anchorED uses, in `anchorEDsite/.env`) now **403s — billing disabled on project #179024390731**. anchorED's voice is likely broken too until billing is re-enabled. Kokoro is local, free, and sounds better.
**Committed:** YES — this commit
**Notes for next session:** To extend audio, edit `veo-y-digo-source.html`, run the scratchpad generators (Kokoro via `/opt/homebrew/bin/python3.11`; model cached at `~/.cache/hyperframes/tts`), then `integrate_audio.py` re-bakes into `pebble-app.html`. Voice `em_alex`, speed 0.85, MP3 mono 24kHz 48k, keyed by exact spoken phrase. `sayLine`/`sayPhrase` (story/phrase sentences) still use the browser voice (not pre-baked). File is now ~7.4MB.

## ROADMAP — Spanish app (Veo & Digo embedded in Pebble) — as of 2026-06-27
1. **Bake keys into defaults** (`DEFAULT_DATA.settings` line ~1108: apiKey/gistId/gistToken/oneSignal*). Blocked: need Gabby's export-data JSON. Git is private, so baking is OK.
2. **Polished jar redesign** — `MarbleJar` (~line 2028). Make data-driven (currently hardcoded 12 marbles, MISSING Español page). Gabby chose: keep jar metaphor, neat rows, include all pages, bigger labels.
3. **AI in the Spanish app** (Veo source `veo-y-digo-source.html`; needs Claude key baked into the Veo app, call api.anthropic.com with `anthropic-dangerous-direct-browser-access`):
   - **Diario autocorrect**: on save, send entry to Claude → rewrite to natural Spanish (translate English, fix grammar/vocab). Example: "me gusta pineapple" → "me gusta piña". Show corrected version.
   - **Recommendations**: AI suggestions — SCOPE TBD (next story / words to drill / daily tip?).
4. **Oz Ch.1 listening mode**: per page → audio (Kokoro, generate), ordena la frase (word-order), ¿qué significa? (meaning), + hand-written comprehension Q. Oz data: `stories.oz1`..`oz8`; oz1 has 18 pages. Then roll out oz2-8.

Audio pipeline: Kokoro via `/opt/homebrew/bin/python3.11` (model ~/.cache/hyperframes/tts), em_alex @0.85, MP3 mono 24k/48k, base64 into `FC_AUDIO` in the Veo source; re-bake = base64 Veo source into `window.VEO_DIGO_B64` in pebble-app.html. Babel is pinned to @7.23.10 (floating CDN broke it).
