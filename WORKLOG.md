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

## ROADMAP additions — 2026-06-27 (later)
5. **Translator button** — top corner of Pebble (in Header, next to settings/jar). Tap → quick EN↔ES translator panel. Needs Claude key.
6. **Conversation mode** — toggle that goes FULL-SCREEN; AI holds a live Spanish conversation, speaking aloud WITH synced subtitles (hear + read simultaneously). Needs Claude key.
   - **Live-voice constraint:** Kokoro (the nice baked voice) is a local Python batch tool, can't run live in the browser. Live options: (a) browser SpeechSynthesis Spanish voice (works in-browser, lower quality), (b) a small local Kokoro HTTP server the app calls (keeps the nice voice, needs the server running), (c) Google TTS once billing is re-enabled. DECISION NEEDED.
   - Input side TBD: does Gabby SPEAK back (Web Speech recognition / mic) or type? "talk to me ... i can hear it and see it" = at minimum AI→Gabby voice+subtitles; clarify if she wants mic input too.

## 2026-06-27 — Oz Chapter 1 "Modo Escucha" (listening mode) built
**Done:** New `escucha` screen in the Veo app. Launch via "🎧 Modo Escucha" button at top of the reader (shows for any story; full content only for oz1 so far). Per page (4 steps): Escucha (auto-plays Alex reading the sentence + replay), Ordena la frase (tap shuffled word-chips into order, checks vs `pg.words`), ¿Qué significa? (pick English `pg.en` from 3, distractors = other pages' en), Comprensión (18 authored Spanish Qs in `ozQ.oz1`). Progress bar + page counter; finish screen. Art via `scenes[pg.art]`. 18 Ch.1 sentence clips generated (Kokoro em_alex 0.85) and merged into FC_AUDIO (now 609). Verified: order step renders, art shows, audio plays, Pebble mounts clean.
**Next:** roll out oz2–oz8 — generate their page audio (reuse `generate_oz1_audio.py`, change the block slice) + author comprehension Qs per chapter into `ozQ`. The escucha engine already handles any story key.
**Committed:** YES — this commit.

## 2026-06-27 — Oz Ch.2-8 rolled out (audio + listen/order/meaning), comprehension Ch.1-3
**Done:** Generated audio for all 219 oz2-8 page sentences (Kokoro em_alex 0.85) → FC_AUDIO now 828 clips. All 8 Oz chapters now play full Modo Escucha (listen + ordena la frase + ¿qué significa?). Comprehension questions authored for Ch.1, Ch.2 (18), Ch.3 (13) in `ozQ`. Ch.4-8 comprehension step auto-skips (engine handles missing Qs). pebble-app.html now ~14.3 MB (async blob decode keeps load non-blocking). Verified mount + audio.
**Next:** author comprehension Qs for oz4 (43), oz5 (12), oz6 (11), oz7 (104), oz8 (18) into `ozQ` — pure content authoring, sentences via the extract snippet in generate_oz1_audio.py. NOTE FILE SIZE: at 14MB, consider whether to keep growing the single baked file or split audio out (e.g., separate audio bank fetched lazily) if it gets heavier.
**Committed:** YES — this commit.

## 2026-06-27 — Diario autocorrect AI wired (dormant until key)
**Done:** The Veo Diario already had a Claude-call `diarioSave()` but was missing auth headers (so it always failed → saved raw). Added `x-api-key`/`anthropic-version`/`anthropic-dangerous-direct-browser-access` headers, updated model `claude-sonnet-4-20250514`→`claude-sonnet-4-6`, personalized prompt (Brie→Gabby, feminine forms). Key routing: Pebble `EspanolPage` reads `data.settings.apiKey` and `postMessage`s it into the iframe (`{type:'pebbleClaudeKey'}`) on load + on change; Veo listens and sets `window.__claudeKey`. No key → `diarioSave` skips the API and saves raw (graceful). Verified app mounts clean.
**To activate:** put an Anthropic `sk-ant-…` key in Pebble Settings → apiKey (or bake into DEFAULT_DATA.settings). Then writing in Diario + save → Claude rewrites to natural LatAm Spanish + a one-line tip.
**Same key unlocks:** future translator + conversation + recommendations.
**Committed:** YES.

## 2026-06-27 — Anthropic API key baked in; Diario autocorrect LIVE
Baked the sk-ant key into DEFAULT_DATA.settings.apiKey + a window.PEBBLE_API_KEY hard fallback (out of babel) + EspanolPage falls back to it. Verified: key valid (200, billing active, correction works), app mounts. Diario autocorrect now functional. Same key powers Pebble chat + future translator/conversation. Key is in pebble-app.html (private repo). Committed, NOT pushed.

## 2026-06-28 — Conversation mode (live Spanish chat with Dora) built
**Done:** Full-screen "Conversación" in the Veo app (home card → #convo screen, registered in `screens`). Claude (sonnet-4-6) holds a back-and-forth in simple LatAm Spanish via `window.__claudeKey`; system prompt = warm beginner tutor, SHORT replies, returns JSON {es,en}. Each AI bubble shows Spanish + English subtitle + 🔊 replay. Voice: **Kokoro Dora** via a local server (`kokoro-tts-server.py`, ef_dora, http://127.0.0.1:7070) — `convoProbe()` checks /health; `convoSpeak()` uses the server if up, else falls back to browser `SpeechSynthesis` (es-MX). Input: text + 🎤 mic (Web Speech `SpeechRecognition`, es-MX, graceful if unsupported). Verified end-to-end (real Claude greeting rendered; Dora server serves MP3).
**Run the nice voice:** `cd ~/Desktop/my\ projects/pebble && /opt/homebrew/bin/python3.11 kokoro-tts-server.py` (note on Desktop: start-dora-voice.txt). Phone/no-server → device voice.
**Committed:** YES.

## 2026-06-28 — Session handoff
State saved. Memory note: `project_pebble_spanish_app.md`. Next-session prompt + full context: **`pebble/NEXT-SESSION.md`** (read it first next time). Roadmap remaining: (1) translator button, (2) recommendations (ask Gabby the scope), (3) Oz Ch.4-8 comprehension Qs. Everything committed, NOT pushed.

## 2026-06-28 — NEW phone-first priorities added to roadmap (Gabby)
Gabby uses Pebble MOSTLY ON HER PHONE. Three new top-priority items captured in NEXT-SESSION.md (block "NEW — phone-first priorities"):
- **A. Voice without the Mac.** Dora needs the local Kokoro server, which dies when the session ends and is unreachable from the phone (127.0.0.1 + mixed-content). Need a no-server voice path: device SpeechSynthesis (free/offline) vs cloud TTS (paid, best quality). **DECISION PENDING from Gabby.**
- **B. Merge Conversación into the main "talk to Pebble" chat** via a mode toggle/button (not a separate Veo screen).
- **C. Fix the 🎤 mic** so she can speak AND type. Suspect the `EspanolPage` iframe is missing `allow="microphone"` (+ autoplay) so SpeechRecognition is blocked; also iOS Safari quirks. Investigate iframe `allow=` first.
No code changed yet — capturing scope + waiting on the voice decision. Working tree was clean before this edit.

## 2026-06-28 — Phone voice (Paulina) + mic fix built (items A + C)
**Working on:** Making Conversación work on Gabby's iPhone with no Mac/Dora server, and fixing the dead 🎤 button.
**Files changed:** `veo-y-digo-source.html` (convo voice + mic JS), `pebble-app.html` (iframe `allow=` + re-baked `VEO_DIGO_B64`).
**What:**
- **Device voice, Paulina preferred.** Added `convoRankVoice`/`convoLoadVoices`/`convoVoice` to pick the best Spanish `SpeechSynthesis` voice on the device (es-MX/es-419 weighted, Premium/Enhanced/localService bonuses, **Paulina +40 so she wins**; honors `localStorage.convoVoiceName` if set). `convoBrowserSpeak` now sets `u.voice`/`u.lang` to that voice. Wired `speechSynthesis.onvoiceschanged`. The Dora local-server path still works on desktop when up, but the phone now uses Paulina instead of the flat compact voice. Gabby downloaded Paulina on her iPhone.
- **Mic permission.** The `EspanolPage` iframe had NO `allow=` attr, so the embedded app could never get the mic. Added `allow="microphone; autoplay; clipboard-read; clipboard-write"`.
- **Mic graceful failure.** Replaced the blocking `alert()` with `convoMicHint()` (non-blocking placeholder hint, auto-resets after 5s). On `not-allowed`/no-SR it now focuses the input and tells her to use the keyboard mic 🎙️ instead of silently doing nothing.
**Verified:** Re-baked (source 10.98MB → app 14.97MB). Headless boot: top app `ERRS(0) mounted`; Veo source `ERRS(0)`, all 3 new fns defined. NOT yet tested on a real iPhone — Gabby needs to confirm Paulina speaks + whether iOS SpeechRecognition works in the standalone homescreen PWA (may need to fall back to keyboard dictation).
**Committed:** YES.

## 2026-06-28 — Item B: Spanish mode merged into the main Pebble chat + Conversación launcher
**Working on:** Making the Dora/Spanish conversation part of Pebble's own "talk to pebble" chat with a toggle, and turning the old Veo Conversación screen into a doorway (no duplicate input).
**Files changed:** `pebble-app.html` (ChatBar Spanish mode + message listener; committed e020c68 for the toggle), `veo-y-digo-source.html` (Conversación card → launcher, screen input removed) + re-baked.
**What:**
- **ChatBar Spanish toggle (committed e020c68):** `ES` button in the chat bar → full-screen Spanish tutor. Replies spoken in **Paulina** (device voice, `_rankEsVoice`/`speakSpanish`) with English subtitle + 🔊 replay (`SpanishChatBubble`). Reuses the existing input/mic/send; mic switches to es-MX and auto-sends in ES mode (via `spanishModeRef`/`sendSpanishRef`). Ephemeral `esMsgs` thread, no persistence, no Pebble tools; wiped on exit. `primeSpeech()` on enter to satisfy iOS gesture rule. Header shows "volver al inglés".
- **Launcher (this commit):** Veo Conversación home card now calls `convoLaunchPebble()` → `window.parent.postMessage({type:'openSpanishChat'})`. ChatBar has a `message` listener that calls `enterSpanish()`. The standalone `#convo` screen's chatbox/mic/send were removed (the "doubling up" Gabby flagged); it's now a simple `.cv-launch` CTA. `openConvo` no longer auto-starts the old in-iframe convo.
**Verified (headless, local):** Veo `ERRS(0)` + launch button/fn present; full app `ERRS(0)` + chat bar renders; **functional: posting `openSpanishChat` flips Pebble into the Spanish view (spanish-view:YES, ERRS(0))**. NOT tested on a real iPhone yet.
**Committed:** YES.
**Notes for next session:** ON-DEVICE TEST NEEDED (Gabby's iPhone, GitHub Pages PWA): does Paulina speak, does the mic work in standalone mode (iOS may block SpeechRecognition → keyboard-dictation fallback), does the Conversación card open Pebble's Spanish chat. Remaining roadmap: translator button, recommendations (scope), Oz Ch.4-8 comp Qs. **API key still public via GitHub Pages** (proxy before sharing).
**(superseded below)** Earlier note — Remaining: **B. merge Conversación into the main "talk to Pebble" chat** (has design choices — ask Gabby: toggle vs separate, keep history, what changes besides the system prompt). Also still open from before: translator button, recommendations (scope), Oz Ch.4-8 comp Qs. **API KEY IS PUBLIC via GitHub Pages** (https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html serves the baked sk-ant key to anyone) — Gabby aware, chose to leave for now, fix (Netlify-function proxy) before sharing. iOS PWA mic is the big unknown to test on-device.
