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

## 2026-06-30 — Final-review fixes (Lecciones)
**Working on:** Three precise fixes from final review of the Lecciones feature.
**Files changed:** `veo-y-digo-source.html` (3 edits), `pebble-app.html` (re-baked).
**What:** Fix 1 - wrapped the 'in-progress' postMessage in openLeccion with a done-status guard so reopening a completed lesson does not downgrade it. Fix 2 - added three display-reset lines at the top of renderLecciones so re-entering the section always shows the checklist, not a stale lesson view. Fix 3 - extended leccGenerate's shape guard to also reject an empty/missing quiz array.
**Committed:** YES -- 4b32858
**Uncommitted:** none
**Notes for next session:** .superpowers/sdd/task-7-report.md is gitignored; report lives only locally.

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
## 2026-06-28 — Bilingual study replies + tap-to-save flashcards — BUILT (stages 1-3) + ES toggle moved
All committed. Feature done end to end (still only local, NOT pushed):
- **Stage 1 (3dde200):** structured replies (`{sentences:[{es,en,words:[{w,t}]}]}` via ES_SYSTEM). `SpanishChatBubble` renders line-by-line: big Spanish (tappable word spans) / colored underline / small English. Tap word → popup w/ gloss + ✓ save; tap underline → save sentence; "guardada ✓" toast. Verified headless (stubbed reply: 2 sentences, underlines, word spans, en subtitles; tap→popup→save→toast all fire, 0 errors).
- **ES toggle (0e45e87):** moved inside the chat box, hides while typing.
- **Stage 2 (875477e):** `data.esFlash.sets` + `ES_FLASH_NEW_SET`/`ES_FLASH_ADD_CARD` reducer cases. Each fresh chat = a new session set (lazy-created on first save), label `Conversación · <date> <time>`. Persists via Pebble localStorage; dedup per set. Verified card lands in `pebble-data.esFlash.sets`.
- **Stage 3 (this commit):** `EspanolPage` posts `{type:'esFlashSets',sets}` into the Veo iframe on load + whenever esFlash changes. Veo `applyEsFlashSets()` registers each set into `themeDecks` (keyed by label) so they appear in the **Tarjetas** sub-deck selector. Session cards map `{front:es, word:en, en:es, art:''}`; `renderCard` shows `c.front` (Spanish) on the front face via `.fc-txt-front`, English on the back. Added a `fcRenderToken` stale-guard to `fetchWikiImage`/`setWikiImg` so a picture deck's late image fetch can't clobber a session text card. Verified: session deck button appears, card front=`gato`/back=`cat`, sentence front=`Hola amiga.`, and the stale-image clobber is fixed.
**Architecture:** Pebble (parent) = source of truth + persistence; Veo Tarjetas = display/study surface, fed via postMessage. Card data shape matches Veo's `deck:[]`.
**Still NOT pushed** — Gabby's phone won't see ANY of today's work (voice/mic/Spanish mode/launcher/this) until we push to GitHub (Pages). API key still public via Pages (proxy before sharing). On-device test pending: Paulina voice, iOS mic in standalone PWA, the whole flow.

## 2026-06-28 — NEW FEATURE SPEC: bilingual study replies + tap-to-save flashcards (Gabby, approved — now BUILT, see entry above)
Big feature for the Pebble Spanish chat (ChatBar Spanish mode). Spec confirmed with Gabby:
- **Reply layout:** each Paulina reply renders sentence-by-sentence, stacked: a BIGGER Spanish line, its SMALLER English translation directly under it, then the next Spanish line + English, etc. Spanish/English paired PER SENTENCE so they align/match. Plan: have Claude return the reply pre-split into sentences with each sentence's `en` translation AND a per-word gloss, so matching is exact and taps are instant (no extra calls). (Replaces the current single {es,en} JSON.)
- **Word tap:** tap any Spanish word → small popup with its English gloss + a ✓ button. ✓ saves that WORD to the current session's flashcard set.
- **Sentence underline:** each Spanish sentence has a colored underline (cycle colors). Tap underline → no translation, just a "save sentence" option → saves the whole SENTENCE to the flashcard set.
- **Flashcards destination:** saved words/sentences go into the **Veo app's "Tarjetas" flashcard section** (NOT a separate Pebble view) as a **per-session set**. Each chat reload = new session = NEW set. **KEEP all past sets permanently** (Gabby confirmed) so she can study old sessions. Since the Veo iframe has NO storage (blob origin, in-memory only), persistence must live in PEBBLE (parent) and be fed into the Veo Tarjetas section on load via postMessage; saves flow Pebble→Veo too.
- Architecture note: cross-iframe. Pebble = source of truth + persistence; Veo Tarjetas = display/study surface. Card data shape must match Veo's existing `deck:[]` format (mapping in progress via Explore agent).
- Status: spec captured, flashcard-section map running, build pending. Build in stages: (1) structured replies + bilingual render + word/sentence interactions in ChatBar with a Pebble-side set store; (2) wire saves into Veo Tarjetas as persistent session sets.

**(superseded)** Earlier note — Remaining: **B. merge Conversación into the main "talk to Pebble" chat** (has design choices — ask Gabby: toggle vs separate, keep history, what changes besides the system prompt). Also still open from before: translator button, recommendations (scope), Oz Ch.4-8 comp Qs. **API KEY IS PUBLIC via GitHub Pages** (https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html serves the baked sk-ant key to anyone) — Gabby aware, chose to leave for now, fix (Netlify-function proxy) before sharing. iOS PWA mic is the big unknown to test on-device.

## 2026-06-28 — Convo flashcards collapsed into one rolling Conversación deck (branch convo-one-deck)
**Working on:** Replacing the per-conversation Spanish flashcard decks with a single permanent "Conversación" deck, and merging existing decks into it on load. Spec and plan in `docs/superpowers/`. Built subagent-driven across 3 tasks, each reviewed clean, plus a final whole-branch review (READY TO MERGE, no critical or important findings).
**Files changed:** `pebble-app.html` only (code). Veo source and the base64 `VEO_DIGO_B64` were intentionally NOT touched, so no re-bake.
**What:**
- Added `CONVO_DECK_ID = 'convo-all'`, `CONVO_DECK_LABEL = 'Conversación'`, a shared `convoCardKey()` dedup helper, and a pure `mergeConvoSets()` (lines ~1134-1147).
- Added the idempotent `ES_FLASH_MERGE_ALL` reducer case. `ES_FLASH_ADD_CARD` now uses `convoCardKey()` too, so every path shares one key formula.
- `saveSpanishCard` writes to the fixed `convo-all` deck (no more per-session sets). `enterSpanish` seeds the dedup cache from the persisted deck so dedup spans all sessions. The save toast counts the whole deck.
- One reactive migration `useEffect` (`[data.esFlash]`) folds any legacy per-convo decks into the single deck on load. Idempotent, so no re-render loop.
- `esSessionRef` is now unused (left in place, harmless).
**Testing (headless):** App boots clean, `PEBBLECHECK ERRS(0)`. Migration assertion `MIGCHECK SETS(1) CARDS(3) ID(convo-all)` (two seeded legacy decks, 4 cards, Hola/hola deduped, collapse into one). Real localStorage key is `pebble-data` (hyphen). Node logic test for the merge helper passes 7/7.
**Committed:** YES. Branch `convo-one-deck`, commits fb8d0fa, 3c117ca, ed3db8f plus docs and worklog. NOT pushed, NOT merged to main.
**Notes for next session:** ON-DEVICE CHECK PENDING (Gabby, iPhone): save a word in two separate Spanish chats, open Veo Tarjetas, confirm a single "Conversación" deck holds both and the old separate per-chat decks are gone. Then decide merge to main. API key is still public via Pages (proxy before sharing) as flagged in earlier entries.

## 2026-06-28 — convo-one-deck merged to main + PUSHED to origin
**Working on:** Shipping the convo-one-deck feature after the post-restart git sanity check + Gabby's on-device Tarjetas check (she confirmed: one rolling Conversación deck, old per-chat decks gone).
**What happened:**
- Git sanity check passed — `.git` survived the laptop restart, all feature commits present.
- Fast-forwarded `main` (was 32 ahead of origin) to `convo-one-deck` (`aaa4464`). No merge commit.
- First push REJECTED by GitHub push protection: the baked Anthropic `sk-ant` key in `pebble-app.html` (lines 566 + 1109) flagged across commits `cafd5e4`, `ed3db8f`, `91f0f9a`.
- Gabby chose "allow the secret," clicked GitHub's unblock URL, then push succeeded: `65cb183..aaa4464  main -> main` (38 commits total — the 6 feature commits + 32 prior unpushed).
**Committed:** YES — pushed. `main` == `origin/main` == `aaa4464`.
**Notes for next session:** The live API key is now in public repo history AND served via Pages. WATCH FOR AUTO-REVOCATION — Anthropic + GitHub secret scanning may kill this key, which would break AI in Pebble (Diario autocorrect, Spanish chat, translator). If AI suddenly fails, rotate the key (Anthropic console → swap into DEFAULT_DATA.settings.apiKey + window.PEBBLE_API_KEY at pebble-app.html:566/1109, re-bake not needed since it's React-side). The real fix remains the Netlify-function proxy so no key lives in client code. Remaining roadmap: phone voice decision (device vs cloud TTS), translator button, recommendations (scope TBD), Oz Ch.4-8 comprehension Qs.

## 2026-06-28 — Remove baked API key (Settings-only) + remove standalone Conversación screen
**Working on:** Two things. (1) The baked sk-ant key got auto-revoked because it was pushed to the public repo + served via Pages (predicted in the prior entry), so AI stopped working. Removed the key from the code entirely so it now comes only from what the user pastes in Settings. (2) Finished + re-baked the in-progress Conversación-screen removal.
**Why the session kept crashing:** pebble-app.html (15MB) and veo-y-digo-source.html (11MB) have giant single-line base64 blobs. Any tool that loads them whole (plain Read, or an Edit that scans the file) overruns and kills the session. Fix: never read them whole. All edits this session were surgical byte-replacements via python (read bytes, replace exact string, write temp, atomic rename), verified with grep + round-trip checks. No whole-file Reads.
**Files changed:**
- `pebble-app.html`: emptied `DEFAULT_DATA.settings.apiKey` (line 1109) and `window.PEBBLE_API_KEY` (line 566) to `''`. Only the Settings input placeholder `sk-ant-...` (line 5463) remains. Re-baked `window.VEO_DIGO_B64` (line 567) from the updated source.
- `veo-y-digo-source.html`: removed the `#convo` launch screen + its mode button, dropped `'convo'` from the `screens` array, and removed the orphaned `openConvo(){ nav('convo') }` (no callers). Convo engine kept; `convoLaunchPebble()` still posts `openSpanishChat` to the parent for the merged-into-main-chat flow.
**Read path verified:** all AI calls use `data.settings.apiKey` (lines 2799/2883/3277/3325), forwarded to the iframe via `params.set('k', settings.apiKey)` (1606); fallback chain `settings.apiKey || PEBBLE_API_KEY || ''` (5787). Re-bake verified: baked base64 decodes byte-for-byte to the current source.
**Committed:** YES — `86a1b04` (key removal), `77d5b7b` (convo screen removal + re-bake). On `main`, NOT pushed.
**Notes for next session:**
- THE FIX for AI not working: Gabby pastes a NEW valid sk-ant key into Pebble Settings (old ones are revoked, cannot be reused). A new key entered in Settings lives only in that device's localStorage, never in code, so it will NOT get auto-revoked like the baked one did. This is the permanent fix the proxy was meant to solve.
- Existing installs (phone + this browser) still have the old revoked key saved in localStorage under settings.apiKey — Gabby must delete it in Settings and paste the new one.
- Git HISTORY still contains the old (dead) key; harmless since revoked. New commits no longer carry it.
- WATCH: if settings ever sync to the gist (gistId/gistToken, currently empty), that could expose the key again. Keep gist sync off or strip apiKey before syncing.
- Convo-screen removal is React/source verified at the byte level but NOT yet checked on-device. On-device check (Gabby): open the Veo app, confirm there's no standalone Conversación screen and that launching conversation drops into the main Pebble chat. Roadmap B (toggle inside main chat) is still partially open.
- These two commits are safe to push whenever Gabby wants (they remove a key, add nothing secret). Not pushed per the no-push-without-asking rule.

## 2026-06-28 — iOS keyboard accessory bar (up/down arrows) + chat scroll fix
**Working on:** Gabby on iPhone (home-screen PWA) saw the iOS keyboard accessory bar (up/down field-nav arrows on the left, Done checkmark on the right) over the chat, and the chat messages scrolled out of view when typing.
**Root cause:** Pebble mounts all 8 swipe pages at once, so ~16 visible text inputs sit in the DOM simultaneously (add task, add event, what did you study, etc.). iOS shows the prev/next field arrows because there are multiple focusable form fields. Confirmed live via JS DOM inspection (16 visible inputs).
**Fix (additive, no React changes):** Injected a plain <script> before </body> in pebble-app.html. On focusin of any input/textarea it sets tabindex=-1 on every OTHER field (records originals, fully restores on focusout), so while one field is focused iOS has nothing to arrow to. On chat-field focus it also scrolls the chat overflow container(s) to the bottom after 320ms so the latest messages stay visible when the keyboard opens.
**Tested (desktop Chrome, local http server):** app mounts clean, typing works, synthetic focusin traps 15 others + leaves chat tabbable, focusout fully restores. NOT yet tested on real iOS (programmatic focus does not fire focusin in an unfocused automation tab, so verified by dispatching synthetic focusin/focusout).
**Honest limits:** the up/down arrows should vanish, but the Done checkmark is Apple's and cannot be removed by a web app (only a native wrapper could). Scroll-keep is best-effort and may need a tweak after on-device testing.
**Voice (Mónica Enhanced):** not a code change. _rankEsVoice already prefers enhanced/premium voices; iOS only exposes installed voices. Gabby to download the higher-quality Mónica in iOS Settings > Accessibility > Spoken Content > Voices > Spanish, then reopen.
**Committed:** YES — `d78feea`. **Pushed:** YES, origin/main.
**Notes for next session:** PENDING on-device test (Gabby, iPhone): after Pages rebuilds + a hard reload (swipe-close PWA, reopen), tap chat box — did up/down arrows go away, does chat stay in view while typing? If arrows persist, iOS prev/next may not honor tabindex=-1 and we'd try a contenteditable composer (bigger, riskier change). If scroll still jumps, add visualViewport-based keyboard-aware layout.

## 2026-06-28 — Chat composer → contenteditable + API key made device-local (key-reset bug)
**Working on:** Follow-up after on-device testing. (1) iOS keyboard accessory bar (up/down arrows) + contact autofill over the chat; the earlier tabindex approach did NOT work on iOS. (2) Gabby's API key "reset / asked again in chat" — only the key reset, other data fine.
**Fix 1 — contenteditable composer:** Replaced BOTH chat `<input>`s (collapsed chat-bar + expanded composer) with a new `ChatField` contenteditable component (defined before Mount). A contenteditable is not a form field, so iOS shows no field-nav arrows and no contact autofill. React state syncs via onInput→onChange; external value changes (clear after send, voice) sync back via React.useLayoutEffect with caret-to-end. Placeholder via CSS `.pebble-ce:empty:before`. `-webkit-user-modify: read-write-plaintext-only`. Helper script updated to also scroll the chat to bottom on CE focus and keep the tabindex-trap for the OTHER real inputs.
**Fix 2 — key device-local (the real reset cause):** With Gist sync configured, `updateHashCreds` wrote `apiKey` into the URL hash (`k=`) and `getHashCreds` read it back; load merge (line 1632) let hash creds "override everything." A home-screen icon freezes its launch URL, so every cold launch re-applied a stale/empty `k=` and wiped the freshly-pasted key (only settings reset → matches report). Removed apiKey from BOTH `getHashCreds` (no longer returns it) and `updateHashCreds` (no longer writes `k=`). Key now lives only in localStorage + `pebble-credentials` backup. Gist save already strips settings (1702) and LOAD_DATA preserves `...state.settings` (1466), so Gist was not the clobber. Bonus: key no longer sits in the URL (security).
**Tested (desktop Chrome, local server):** both — app compiles/mounts, no errors, contenteditable typing/clear/state-sync/placeholder all work, getHashCreds ignores `k=` in the hash.
**Committed:** YES — `1ad4626` (contenteditable), `b3a75a3` (key device-local). **Pushed:** YES, origin/main (this WORKLOG entry commit may be local until next push).
**Notes for next session:** PENDING on-device test (Gabby, iPhone): after Pages rebuilds + reopen (do NOT delete/re-add the icon — destructive and unnecessary now), re-paste the key in Settings ONCE; it should now persist across launches. Check chat box: up/down arrows + autofill gone? chat stays in view while typing? Mic button (roadmap C) still unaddressed. Durable key fix is still the Netlify-function proxy so no key lives client-side at all. Voice (Mónica Enhanced) = iOS Settings download, not code.

## 2026-06-28 — BUILD stamp in Settings + keyboard-aware chat (BUILD 1, BUILD 2)
**Working on:** On-device iOS issues persisted; added a visible BUILD number in Settings so Gabby can confirm she's on the latest deploy (cache check), then fixed the keyboard UX.
**BUILD 1 (commit be0525a):** Added `PEBBLE_BUILD` + `PEBBLE_BUILD_NOTE` consts and render them at the top of SettingsPanel ("BUILD n" + summary). Bump both on every future fix. This is the cache-confusion killer: if she sees the build number she's on new code.
**BUILD 2 (commit f5890b6):** Keyboard fixes after Gabby described: keyboard opens → reply hidden; scrolling up to read → composer slides off; sending → keyboard auto-dismisses.
- Root cause of hidden chat: `.phone-frame` was `height: 100vh` with no visualViewport handling, so it ignored the keyboard. Changed to `height: var(--app-h, 100vh)`; added a visualViewport `resize`/`scroll` listener that sets `--app-h` to `visualViewport.height`. App now shrinks above the keyboard. Messages already auto-scroll to bottom (useEffect at 2676 on [messages, chatOpen, chatExpanded]).
- Root cause of keyboard dropping on send: tapping the send/mic buttons blurred the contenteditable. Added `onMouseDown={e => e.preventDefault()}` to both send buttons (3032/3094) and both mic buttons (3026/3088) so focus stays on the composer and the keyboard stays open after sending.
**Tested (desktop):** compiles, no errors, BUILD renders in Settings, `--app-h` set by the listener, desktop frame stays 812px (var only used at mobile width), typing works. iOS keyboard behavior itself NOT desktop-testable — needs Gabby.
**Committed/Pushed:** YES — be0525a (BUILD 1 stamp), f5890b6 (BUILD 2 keyboard). origin/main.
**Notes for next session:** Gabby tests on iPhone (confirm Settings shows BUILD 2 first). If the frame shifts/offsets when keyboard opens, add `visualViewport.offsetTop` handling (translateY) or pin `.phone-frame` position:fixed top:0 — that's the likely BUILD 3. Autofill: should be gone via contenteditable; confirm on BUILD 2. Mic button (roadmap C) still separate. Durable key fix still = Netlify proxy.

## 2026-06-29 — Running backlog (Gabby, ordered)
Tracked so nothing slips. Build/fix as prioritized.
1. **Keyboard fixes (BUILD 3)** — TWO issues:
   (a) Normal chat: dead/blank gap between keyboard and chat bar; user must manually pull chat down each focus. Screenshot pending.
   (b) REGRESSION from BUILD 2: the visualViewport `--app-h` resize is GLOBAL to `.phone-frame`, so the keyboard-aware shrink now fires for EVERY input (Atajos, Journal, etc.), not just chat. The chat-bar/keyboard "goes up" behavior leaked into Atajos. FIX: scope the keyboard-aware shrink to ONLY when the main chat composer is focused (gate the `--app-h` apply on chat focus, restore default `--app-h`/100vh on blur or non-chat focus). Screenshot pending.
2. **Flashcard editor** — design APPROVED, spec at `docs/superpowers/specs/2026-06-29-flashcard-editor-design.md`. Phase 1 (editor: list/edit/delete/manual-add-dedup/from-chat-suggestions) then Phase 2 (AI suggest + AI organize/split into themed decks). Awaiting Gabby's spec review, then writing-plans.
3. **Spanish chat corrections + explain** (new, needs design) — under the user's Spanish message, show the corrected Spanish + an "Explain" button breaking down the grammar they missed (e.g. used "yo" but "estoy" works like X).
4. **Save facts & quotes with a heart** (new, needs design) — heart a fact/quote, view saved ones later. Scope TBD (source + view location).
Durable key fix (Netlify proxy) and mic button (roadmap C) still open from before.

## 2026-06-29 — BUILD 3: chat-scoped keyboard resize + frame pin (gap fix)
**Working on:** Fix the BUILD 2 keyboard regressions Gabby reported (screenshot "look at.PNG": expanded Spanish chat composer floating with dead space below it down to the keyboard; and the keyboard-aware shrink firing in Atajos where it shouldn't).
**Fixes (commit 1b351f9):**
- Consolidated the two end-of-body scripts into one. The `--app-h` visualViewport shrink now applies ONLY while the chat composer is focused, gated by an `html.kb-chat` class toggled on chat focusin/focusout. Non-chat inputs (Atajos in the Veo iframe, Journal, add-task, etc.) no longer trigger the app shrink. Verified on desktop: chat focus → kb-chat + --app-h set; other input focus → kb-chat false.
- `.phone-frame` is now `position: fixed; top:0; left:0; right:0` on mobile so iOS can't scroll the layout and open a gap between composer and keyboard. Desktop media query overrides back to `position: relative` (centered mockup verified intact on desktop).
- BUILD bumped to 3.
**Caveat:** the actual iOS keyboard gap + scoping can only be confirmed on Gabby's iPhone. CRITICAL open question across the last several builds: we still don't know which BUILD her phone is actually running — if Settings shows < 3, she's been testing cached old code (no service worker; iOS caches the webclip), which would explain why autofill/key-reset/gap all persisted. The BUILD stamp exists to settle this.
**Committed/Pushed:** YES — 1b351f9, origin/main.
**Notes for next session:** Gabby MUST report the BUILD number in Settings. If < 3 → cache problem is the real blocker; consider a network-first service worker so the PWA always fetches fresh (currently none). If BUILD 3 and gap persists → add visualViewport.offsetTop translate. Backlog unchanged: flashcard editor (spec approved, ready for writing-plans), Spanish corrections (design), facts/quotes (design).

## 2026-06-29 — Backlog add: Listening mode (Modo Escucha) — wrong answer traps you
**Bug (Gabby, on-device):** In the listening mode for the story (Alice in Wonderland / Oz "Modo Escucha"), when you get a question WRONG it won't let you skip or advance — you get stuck redoing the same words with no way to move to the next question. FIX: add a Skip / "next" option (or auto-advance after N tries / reveal answer) so a wrong answer doesn't lock you in. Logged for later, not fixed yet.

## 2026-06-29 — Flashcard editor Phase 1 (Tasks 1, 3, 4 done; 2, 5 remain)
**Working on:** Building the flashcard editor per spec/plan in docs/superpowers/. Done inline this session, verified on desktop (local http server + browser JS).
- **Task 1 (2749989):** reducer actions ES_FLASH_DELETE_CARD/EDIT_CARD/MOVE_CARDS/PUSH_RECENT + `recent: []` in DEFAULT_DATA.esFlash. Updated existing NEW_SET/ADD_CARD/MERGE_ALL to spread `...state.esFlash` so they don't drop `recent`.
- **Task 3 (a56f21a):** `FlashEditor` component (before App) + `flashEditorOpen` state + `openFlashEditor` window-message listener in App + render after SettingsPanel. List/edit/delete/manual-add. Dedup is reducer-enforced (no dup ever) + "ya guardada" toast in normal (non-racing) use. Verified: opens, add/dedup/delete work, 🗑 renders. (Fixed a raw-string `\U0001f5d1` escape bug → real emoji.)
- **Task 4 (cd5bcd0):** "✏️ Administrar tarjetas" button + manageFlashCards() bridge (posts openFlashEditor) in the Veo Tarjetas panel (#cPanelCards); re-baked VEO_DIGO_B64 (round-trips to source). Bumped BUILD to 4. Verified the bridge opens the editor end-to-end.
**REMAINING for Phase 1:**
- **Task 2:** capture recent Spanish chat words into `data.esFlash.recent` (dispatch ES_FLASH_PUSH_RECENT from the Spanish reply parse path) so the "de tus chats" suggestions populate. Currently that section is empty.
- **Task 5:** confirm the esFlashSets post effect (~5817) re-fires on esFlash change so Tarjetas reflects edits (likely already does; verify).
**Committed:** YES — 2749989, a56f21a, cd5bcd0 (+ plan abf8b1e). **Pushed:** NO — awaiting Gabby's OK.
**Recurring issue:** git index keeps corrupting (tracked count → 0, everything shows deleted) after some operations — a crashed git leaves it empty. Fix each time: back up working files, `git reset --mixed HEAD` (rebuilds index from HEAD, working tree untouched), recommit. Working files are never lost.
**Notes for next session:** Editor is usable + reachable now. Phone test (after push + reload, confirm Settings shows BUILD 4): open Español → Tarjetas → Administrar tarjetas → add/edit/delete a card. Keyboard BUILD 3 test still pending too.

## 2026-06-29 — Spanish chat corrections + explicar + guardar (BUILD 6)
**Working on:** Feature from spec docs/superpowers/specs/2026-06-29-spanish-corrections-design.md (approved). Built inline this session, React-side only (no re-bake).
**What:** ES_SYSTEM extended so the Spanish reply JSON also returns `correction:{fixed,en,changed}` for the user's latest message (folded into the existing reply call, no extra cost). esCall parses it; sendSpanish attaches it to the last user message in esMsgs. SpanishChatBubble user branch now renders the correction under the bubble ("más natural ·" / "✓ suena bien ·" + fixed + en) with two buttons: `explicar` (separate AI call via explainSpanish, cached on the message as m.explanation) and `＋ guardar` (saveSpanishCard('sentence', fixed, en), deduped). Always-on (option 2: shows natural version even when correct). BUILD 6.
**Tested (desktop):** compiles + mounts clean, no errors. The live AI correction/explain flow needs a valid key → on-device test only.
**Committed:** YES — 476b0e2 (+ spec 48b4af6). **Pushed:** NO — awaiting OK.
**Backlog remaining:** flashcard "from your chats" suggestions (Task 2); facts/quotes with heart (needs design); Modo Escucha skip bug; keyboard BUILD 3 on-device confirm. Across-the-board: still UNCONFIRMED on Gabby's phone whether any BUILD (3-6) is loading (cache) — she keeps deferring the Settings BUILD-number check.

## 2026-06-29 — Heart quotes/facts + scrollable saved section (BUILD 8)
**Working on:** Gabby's "save facts and quotes with a heart, scroll a saved section underneath" — turned out the feature already exists (NotebookPage "pebble's picks": daily quote + funFact + rec; only rec was heartable, tiny saved list).
**What:** Added a heart to the quote card and the fun-fact card (toggle save + dedup); made the rec heart toggle too; enlarged the "saved" list to a scrollable section (maxHeight 260) showing full content (quote+author / fact text / rec) each with a remove (✕). Reducer: SAVE_PICK now dedups + stores `author`; added `REMOVE_SAVE`. BUILD 8.
**Tested (desktop):** compiles, mounts clean, picks page renders. Could not exercise the heart on the test browser — its gist-synced data has an empty dailyPick (no AI pick generated) so nothing to heart; edits mirror the existing working rec-heart pattern. On-device test needed.
**Committed/Pushed:** YES — 649a79c, origin/main.
**Backlog now:** Modo Escucha skip fix; flashcard Phase 2 (AI organize/split). All features this session (BUILD 1-8) STILL UNCONFIRMED on Gabby's phone — she keeps deferring the Settings BUILD-number check; if cached, none of it is reaching her.

## 2026-06-29 — Modo Escucha wrong-order escape + finish emoji (BUILD 9)
**Bug fixed:** Modo Escucha (Spanish story listening mode, Veo source) step 2 "Ordena la frase" had no escape — a wrong word order only said "Casi… inténtalo otra vez" with no skip, trapping the user (her report). The meaning/comprehension steps already advance on wrong; only order trapped.
**Fix:** escCheckOrder wrong-branch now shows a "Ver respuesta y seguir →" button → escRevealOrder() reveals the correct phrase + a Continuar button (escAdvance). Retry still available. Also fixed a pre-existing bug: escFinish showed literal "\U0001F389" (JS has no \U escape) → real 🎉. Re-baked into VEO_DIGO_B64 (round-trips). BUILD 9.
**Tested (desktop):** boots clean, no errors; baked Veo source contains escRevealOrder + the fixed emoji. In-game flow (navigate a story's Modo Escucha, get order wrong) → on-device test.
**Committed/Pushed:** YES — b08254e, origin/main.
**Backlog now:** only flashcard Phase 2 (AI organize/split into themed decks) remains from the session's asks. Everything (BUILD 1-9) still UNCONFIRMED on Gabby's phone (cache / build-number check outstanding).

## 2026-06-29 — Flashcard Phase 2: AI suggest + organize/split into themed decks (BUILD 10)
**What:** FlashEditor gains AI (shown when deck has cards + apiKey): 'sugerir palabras' (Claude proposes 8 new related words → tap chips to add, deduped) and 'organizar' (Claude categorizes each card → per-category buttons 'cat (n) →' split those cards into a new themed deck). Helpers: aiCall + parseJ (fence-strip + brace-salvage), suggestAI, organizeAI, splitCategory. Uses ES_FLASH_NEW_SET (now stores `themed`) + ES_FLASH_MOVE_CARDS.
**Migration made themed-safe (critical):** mergeConvoSets now keeps themed decks (only flattens non-themed into convo-all); ES_FLASH_MERGE_ALL no-ops unless a legacy non-convo, non-themed deck exists; the migration useEffect `needsMerge` ignores themed decks → no render loop, themed decks survive reloads.
**Tested (desktop):** compiles, editor opens, add works (no regression), no errors. AI buttons correctly gated on apiKey (hidden on the keyless test browser). The AI suggest/organize/split + themed-deck-survives-reload flow needs a real key → on-device test.
**Committed/Pushed:** YES — fc53da1, origin/main.
**SESSION BACKLOG CLEARED.** Shipped BUILD 1-10 this session. Still UNCONFIRMED end-to-end on Gabby's phone (she said "its good" once but never reported a specific BUILD number); the AI flashcard features especially need an on-device run with her key.

## 2026-06-29 — Keyboard gap fix: track visualViewport.offsetTop (BUILD 11)
**Bug (Gabby, iPhone):** When the chat keyboard opens, the chat moves up but a big dead gap sits between the keyboard and the chatbox, and she has to scroll down each time to close it.
**Root cause (confirmed by code + the BUILD 2/3 notes, which predicted exactly this):** `.phone-frame` is `position: fixed; top: 0` sized to `visualViewport.height` on chat focus, but the helper never compensated for `visualViewport.offsetTop`. iOS scrolls the LAYOUT viewport to reveal the focused composer; the fixed frame stays pinned at top:0 while the visible region shifts down by offsetTop, leaving a gap (= offsetTop) below the composer. Manually scrolling resets offsetTop→~0 and closes it (matches her report). The offsetTop translate was flagged as the next fix in BUILD 2 AND BUILD 3 but never added.
**Fix (pebble-app.html only, no React change, NO re-bake):**
- CSS: `.phone-frame` base rule `top: 0` → `top: var(--kb-top, 0px)`. Desktop media query still overrides `top: auto`, so desktop is unaffected.
- Helper `applyViewport()`: while `kb-chat` is active, also set `--kb-top` = `Math.round(vv.offsetTop)`; clear it on blur. The existing `vv.scroll`/`resize` listeners already call applyViewport, so the frame now tracks the visible region continuously and the composer stays flush above the keyboard.
- Added one `applyViewport()` re-pin inside the 320ms post-focus timeout so it settles after the iOS keyboard animation.
- Bumped PEBBLE_BUILD 10 → 11.
**Tested (this session):** extracted the helper IIFE → `node --check` = JS SYNTAX OK; `--kb-top` set+removed in JS and referenced in the base CSS rule confirmed via grep. iOS keyboard behavior itself is NOT desktop-testable → needs Gabby.
**Committed/Pushed:** Committed locally — NOT pushed (deploy rule). Awaiting Gabby's OK to push to Pages.
**CRITICAL on-device step:** Open Settings FIRST and confirm it says **BUILD 11**. If it shows anything lower, her phone is on cached webclip code (no service worker exists) and NONE of the keyboard fixes (BUILD 2/3/11) have ever actually loaded — which would fully explain "a problem I asked to be solved was not." In that case the real fix is a cache-bust / network-first service worker, not more layout code. Then: tap chat, open keyboard — composer should sit flush above the keyboard with no gap and no need to scroll down.
**Notes for next session:** If BUILD 11 still shows a gap, next lever is suppressing the layout scroll entirely (lock body / preventScroll on focus) or `t.scrollIntoView` may be fighting the pin — try removing the block:'center' scrollIntoView. Bigger picture: add a service worker so deploys actually reach her phone. Spanish LESSONS feature (her earlier ask this session) is still in brainstorming, not started — back-burnered the "how the CIA learns languages" research (report saved in context).

## 2026-06-29 — Flashcard flip-back spoiler fix (BUILD 12)
**Bug (Gabby):** On the 3D flip flashcards, with a card's meaning showing (flipped to back), clicking "next" briefly shows the NEW card's answer before it flips to the front — spoiling it.
**Root cause (Veo source, fcCard system):** `renderCard()` removed the `flipped` class to return to the front, but `.card` has `transition: transform 0.6s`, so removing `flipped` ANIMATES a 0.6s rotate-back. The back face had already been repopulated with the new card's word/answer, so it's visible for ~0.3s of the rotation. (The other flashcard system, cCard/cShowCard, uses display:none and was never affected.)
**Fix:** In `renderCard()`, when the card is currently flipped, snap it to the front WITHOUT animating — set `transition:'none'`, remove `flipped`, force a reflow (`void offsetWidth`), then restore `transition:''` so user taps still animate at 0.6s. New card always appears front-first, no flash of the answer.
**Re-bake:** edited `veo-y-digo-source.html` → re-baked into `window.VEO_DIGO_B64`; round-trip verified (decoded bytes == source) and fix confirmed present in the baked payload. BUILD 12.
**Tested (this session):** `node --check` on the full Veo script block (10.9MB) = OK; React-side untouched this build. Visual no-spoiler behavior → on-device.
**Committed/Pushed:** Committed locally — NOT pushed (deploy rule). Bundled with BUILD 11 keyboard fix for one push when Gabby OKs.
**On-device:** confirm Settings shows BUILD 12; Español → Tarjetas (theme or story deck), flip a card to see the meaning, tap next → the next card should appear front-first with no glimpse of its answer.

## 2026-06-30 — Lecciones: Claude lesson generator (Task 3)
**Working on:** Task 3 of the Spanish Lecciones feature (branch `lecciones`). Added the AI lesson generator functions to `veo-y-digo-source.html`, re-baked into `pebble-app.html`.
**Files changed:** `veo-y-digo-source.html` (35 lines added), `pebble-app.html` (re-baked).
**What:** Three functions inserted after `openLeccion` in the Lecciones section:
- `leccParseJson(text)` -- strips code fences, slices outer braces, calls JSON.parse.
- `async leccGenerate(topic)` -- builds lesson prompt, calls Claude (claude-sonnet-4-6, headers matching convoCall exactly), writes result to window.__esLessons + posts esLessonCache to parent.
- `leccTopicById(id)` -- linear search through LECCIONES groups to find a topic by id.
**Verified:** `checkblock.py` -> JS SYNTAX OK; `rebake.py` -> re-bake OK marker-present. Live API call deferred to on-device test (key not available in this session).
**Committed:** YES -- 31c4623. NOT pushed.
**Notes for next session:** Task 4 will wire `openLeccion` into the full lesson view, calling `leccGenerate`/`leccTopicById`. The three new functions are in place and ready.

## 2026-06-30 -- Lecciones: "teach me X" command in Spanish chat (Task 6)
**Working on:** Task 6 of the Spanish Lecciones feature. Added the `teach me X` / `enseñame X` shortcut to the main Pebble Spanish chat (ChatBar in `pebble-app.html`). React-side only -- no re-bake, no Veo source touched.
**Files changed:** `pebble-app.html` only (+26 lines).
**What:**
- `teachSpanish(topic, userText)` added before `sendSpanish`. Uses a direct fetch to `api.anthropic.com` (same pattern as `explainSpanish`), asks Claude for `{"teach":"...","examples":[{"es":"...","en":"..."}]}`, parses with an inline `stripParse` fence-stripper. Builds `sentences = [{es: teach explanation, en:'', words:[]}].concat(examples)`, appends `{role:'assistant', sentences, teach:true}` to `esMsgs`, and calls `speakSpanish`. No-key path mirrors sendSpanish. Try/catch/finally wraps the whole body.
- In `sendSpanish`, after the `if (sending) return;` guard: `const teachMatch = userText.match(/^(?:teach me|ens[eeñ]ame)\s+(.*)/i); if (teachMatch) { return teachSpanish(teachMatch[1].trim(), userText); }`.
- `SpanishChatBubble` already renders `m.sentences` for all assistant messages; no rendering change needed. `teach:true` is a marker only.
- `aiCall`/`parseJ` (FlashEditor scope, not ChatBar) are NOT used -- direct fetch + inline parser instead.
**Verified:** `node scratchpad/checkbabel.js pebble-app.html "function ChatBar"` -> BABEL SYNTAX OK. Same for "teachSpanish" -> BABEL SYNTAX OK.
**Committed:** YES -- 94ade67. NOT pushed.
**Notes for next session:** On-device test: type "teach me the future tense" in Spanish mode -- expect an assistant bubble with an English explanation + 2-3 Spanish examples with hear/save controls. Normal Spanish messages unchanged.

## 2026-06-30 — Lecciones Spanish lessons feature COMPLETE (BUILD 13)
**Working on:** The full "Lecciones" feature on branch `lecciones`, built subagent-driven from the plan at docs/superpowers/plans/2026-06-30-spanish-lecciones.md (spec at docs/superpowers/specs/2026-06-29-spanish-lecciones-design.md).
**What shipped (Tasks 1-6, each reviewed):**
- React data layer: `data.esLessons` + reducer (ES_LESSON_CACHE / ES_LESSON_PROGRESS); EspanolPage posts `esLessonsData` into the iframe and handles `esLessonCache`/`esLessonProgress`/`saveEsCard` back out (saveEsCard routes into a themed `lecciones` flashcard deck via the idempotent ES_FLASH_NEW_SET + ES_FLASH_ADD_CARD).
- Veo source: a new `lecciones` screen (section.screen) with the phased road-to-fluency checklist (`LECCIONES` constant, 6 phases), progress count, "Lección de hoy" button, home nav entry; `renderLecciones`/`leccStatus`/`leccionDeHoy`.
- Lesson generator `leccGenerate` (Claude claude-sonnet-4-6, headers matching convoCall) returning structured JSON, cached to window.__esLessons + posted to React; hardened with `if(!res.ok)` + shape guard BEFORE the cache write so a failed/garbage response cannot poison the persisted cache.
- Full lesson view `openLeccion`/`renderLeccionView`/`leccQuestionHtml`/`leccAnswer`/`leccFinishQuiz`: teach text, pattern, multiple-choice practice with per-question "why", mini-quiz scored on a 0.6 threshold that marks the topic done; all AI strings HTML-escaped via `esc()`.
- Hear + save on examples: `leccHear` (fcSpeak) and `leccSaveEx` (postMessage saveEsCard -> lecciones deck).
- "teach me X" / "enseñame X" in the Spanish chat (`teachSpanish` in ChatBar): short English explanation + 2-3 Spanish examples; speaks ONLY the example sentences (not the English text).
**Files changed:** `veo-y-digo-source.html` (Lecciones screen + lesson engine) re-baked into `pebble-app.html`; React data layer + chat command in `pebble-app.html`. PEBBLE_BUILD 12 -> 13.
**Verified (static):** every task node --check (Veo plain JS) / Babel-transform (React JSX) clean; re-bake round-trips verified per Veo task; final bake in sync with all Lecciones functions in the payload. Each task passed an independent spec+quality review (Task 2 needed an accent fix, Task 6 needed an enseñame-regex fix; both fixed + verified).
**NOT yet verified:** runtime behavior in a browser. No live lesson generation was run (API key is device-local). Needs Gabby's on-device pass.
**Committed:** branch `lecciones`, NOT merged to main, NOT pushed (deploy rule).
**Deferred Minors (for final review / follow-up):** home Lecciones button has no .icon SVG like siblings; leccFinishQuiz does not disable its button against a double-tap; cache shape-guard checks practice but not quiz (empty-quiz response could not be completed).
**On-device test plan (BUILD 13):** confirm Settings shows BUILD 13. Español -> Lecciones: checklist renders; tap a topic (with API key set) -> lesson generates (teach, pattern, practice, mini-quiz), finishing at >=60% checks it off; reopen loads instantly from cache; hear + save an example -> appears in Tarjetas "Lecciones" deck; in the Spanish chat, "teach me the future tense" returns an explanation + examples.

## 2026-07-01 — Lecciones v2 formatting upgrade (BUILD 14)
**Working on:** Upgrading Lecciones lesson rendering per Gabby's on-device feedback.
**Files changed:** `veo-y-digo-source.html` (7 edits), `pebble-app.html` (BUILD bump + re-baked).
**What:**
- Generator prompt updated to request v2 JSON shape: teach (1-2 sentences), tips[], patternTable{headers,rows}, examples[{es,en,highlight,label}], practice, quiz.
- Shape guard now also requires `Array.isArray(lesson.examples)`; sets `lesson._v = 2` after parsing.
- `openLeccion` treats any cached lesson without `_v === 2` as stale, forcing regeneration into the new format.
- All 34 LECCIONES topics gained an `en:'...'` field with exact English labels from spec.
- `renderLecciones` now shows the English as a small muted `lecc-en-sm` line under each Spanish label.
- `renderLeccionView` now renders: teach paragraph, tips bullet list, a real `<table class="lecc-table">` (fallback to `<pre>` for old string pattern), and highlighted/labeled examples (first occurrence of `highlight` wrapped in `<span class="lecc-hl">`; short `<span class="lecc-tag">` label pill).
- 13 new CSS rules added to the lecc style block (.lecc-tips, .lecc-table, .lecc-hl, .lecc-tag, .lecc-ex-line, .lecc-ex-tools, .lecc-label, .lecc-en-sm).
- PEBBLE_BUILD bumped 13 -> 14 with updated note.
**Verification:** checkblock.py -> JS SYNTAX OK; rebake.py -> re-bake OK marker-present; checkbabel.js -> BABEL SYNTAX OK. All grep markers confirmed.
**Committed:** YES -- 2e05a41
**Uncommitted:** none.
**Notes for next session:** ON-DEVICE TEST NEEDED. Old cached lessons will auto-regenerate on first open (by design). Full report: `.superpowers/sdd/lecciones-v2-report.md`. NOT pushed -- push when Gabby is ready.

## 2026-07-01 -- Lecciones: heart-to-save (Guardadas) + per-lesson flashcard decks (BUILD 15)
**Working on:** Two new features on top of the v2 lesson formatting: (A) heart a lesson to save it to a "Guardadas" list, and (B) a "Hacer tarjetas de esta leccion" button that builds a per-lesson flashcard deck.
**Files changed:** `veo-y-digo-source.html` (7 edits), `pebble-app.html` (reducer + message handlers + BUILD bump + re-baked).
**What:**
- veo source: `.lecc-heart` / `.lecc-heart.on` CSS; `leccIsSaved(id)` + `leccToggleSave(id)` helpers; heart button in `renderLeccionView` header; Guardadas section at top of `renderLecciones`; "Hacer tarjetas de esta leccion" button before Terminar; `leccMakeDeck()` function; `split(h).join` fix for the `$` hazard in the highlight replace.
- pebble-app.html: `ES_LESSON_SAVE` reducer case (spreads `...cur`, so the `saved` flag survives later cache/progress updates, which was confirmed -- both reducers use `...cur`); `esLessonSave` + `esMakeDeck` message handlers in `EspanolPage`.
- PEBBLE_BUILD bumped 14 -> 15.
**Verification:** checkblock.py -> JS SYNTAX OK; rebake.py -> re-bake OK marker-present; checkbabel.js x2 -> BABEL SYNTAX OK. All grep markers confirmed. Report: `.superpowers/sdd/lecciones-save-decks-report.md`.
**Committed:** YES -- (see commit)
**Uncommitted:** none.
**Notes for next session:** ON-DEVICE: open a Lecciones lesson, tap the heart, back out, confirm it appears in "Guardadas" at the top of the list. Tap "Hacer tarjetas", confirm "Tarjetas creadas" message appears, then open Tarjetas and verify the "Leccion: ..." deck is present. NOT pushed -- push when Gabby OKs.

## 2026-06-30 — Lecciones merged to main + LIVE (BUILD 13); repo moved to ~/dev
**Working on:** Shipping the Lecciones feature and relocating the repo out of iCloud.
**Went live:** merged `lecciones` -> `main` (fast-forward to 2eea589) and pushed. `origin/main` now serves BUILD 13 via GitHub Pages. This deploy also carried the earlier BUILD 11 (keyboard offsetTop gap fix) and BUILD 12 (flashcard flip-back spoiler fix) that had not reached the phone yet. The `lecciones` branch is kept on origin as a backup.
**Repo moved (rule #5):** pebble relocated from `Desktop/my projects/pebble` to **`~/dev/pebble`** via a fresh `git clone` from GitHub (avoids iCloud dataless-placeholder corruption), checked out `lecciones`, carried over the gitignored `scratchpad/` helpers + `.superpowers/` ledger, verified (clean tree, BUILD 13, bake in sync, helpers run), then removed the Desktop copy. Updated memory notes + CLAUDE.md rule #5 to point at `~/dev/pebble`.
**Files changed:** merge brought in veo-y-digo-source.html + pebble-app.html (Lecciones) + docs/superpowers specs/plans; this entry + NEXT-SESSION rewrite are docs only.
**Committed:** YES — feature at 2eea589 on main (pushed). Docs update commit follows.
**Uncommitted:** none.
**Notes for next session:** ON-DEVICE TEST STILL PENDING — confirm Settings shows BUILD 13, then walk the Lecciones flow (see NEXT-SESSION.md). Non-blocking follow-up polish (home Lecciones icon, leccFinishBtn double-tap disable, e.origin check, teachSpanish English-in-es-slot) documented in NEXT-SESSION.md. Lecciones v2 ideas: typed-answer questions, spaced-repetition review, streak.

## 2026-07-01 — Lecciones v2 formatting + save/decks LIVE (BUILD 14, 15)
**From Gabby's on-device feedback on the first Lecciones lessons.**
**BUILD 14 (live, 001f8ce):** lesson formatting v2. LessonObject shape v2 (`_v:2`): pattern is now a real horizontal TABLE (patternTable{headers,rows}); examples HIGHLIGHT the target word (colored span) and TAG the sentence with a label (e.g. ser/estar); teach is a short intro + `tips[]` each on its own line; the lesson LIST shows the English translation per topic (added `en` to all 34 LECCIONES topics). Old cached lessons (no `_v:2`) auto-regenerate on open. Generator prompt + renderLeccionView + renderLecciones + CSS. Spec: docs/superpowers/specs/2026-07-01-lecciones-formatting.md.
**BUILD 15 (live, 877debc):** (A) heart-to-save — heart on the lesson view toggles a topic into a "Guardadas" section at the top of the Lecciones list; `ES_LESSON_SAVE` reducer + `esLessonSave` message + `saved` flag on data.esLessons (preserved across cache/progress updates). (B) per-lesson flashcard decks — "Hacer tarjetas de esta leccion" builds a themed deck `Leccion: <topic>` from the examples (es/en sentence cards) + highlighted words (word cards) via a new `esMakeDeck` message. Plus polish: flex header for the heart, in-place heart toggle (does not blank quiz feedback), guard leccMakeDeck, and a split/join highlight-injection hardening.
**Built subagent-driven; each build reviewed (v2 Approved w/ minors; save/decks Approved; polish applied). All static-verified + re-baked + LIVE on main.**
**Committed/Pushed:** YES — main at 877debc, pushed to GitHub Pages.
**On-device to confirm (BUILD 15):** open a lesson -- table renders as rows, example target word is highlighted + labeled, tips on their own lines, list shows English; heart a lesson → appears under "Guardadas"; "Hacer tarjetas de esta leccion" → a "Leccion: X" deck shows in Tarjetas; heart toggle mid-quiz no longer blanks answers.

## 2026-07-01 — Lecciones: no auto-regen + manual regenerar + custom topic input (BUILD 16)
**Working on:** Three fixes per spec docs/superpowers/specs/2026-07-01-lecciones-no-autoregen-custom.md.
**Files changed:** `veo-y-digo-source.html` (6 edits), `pebble-app.html` (reducer + handler + BUILD bump + re-baked).
**What:**
- (A) Deleted the `_v !== 2` line from `openLeccion`. Cached lessons of any version are now used as-is; no auto-regen. Only a topic with NO cached lesson triggers generation. leccGenerate still sets `_v = 2` on new lessons.
- (B) Added a "regenerar" lecc-mini button in the lesson header (alongside the heart). Added `leccRegen()`: shows a loading state, calls `leccGenerate`, resets `leccState`, re-renders. Only spends a credit on explicit tap.
- (C) Custom topic input: `<div class="lecc-custom">` with text input + "Crear leccion" button above `leccList`. `leccSlug()` + `leccCreateCustom()` handle input → `custom-<slug>` id → `window.__customTopics`. `leccTopicById` falls back to `window.__customTopics`. `leccGenerate` posts `label: topic.label` in the `esLessonCache` message. `applyEsLessons` rebuilds `window.__customTopics` from cached custom entries on reload. `renderLecciones` adds a "Mis lecciones" phase for any custom- id with a cached lesson (label escaped via `esc()`). React: `ES_LESSON_CACHE` reducer stores optional `label`; `esLessonCache` handler passes `label` through.
- PEBBLE_BUILD bumped 15 -> 16.
**Verification:** checkblock.py -> JS SYNTAX OK; rebake.py -> re-bake OK marker-present; checkbabel.js -> BABEL SYNTAX OK. All grep markers confirmed. Full report: `.superpowers/sdd/lecciones-b16-report.md`.
**Committed:** YES -- 395be26
**Uncommitted:** none.
**Notes for next session:** NOT pushed -- push when Gabby OKs. On-device: open any existing lesson -- should load from cache without regenerating. Tap "regenerar" to force a new one. Scroll to top of Lecciones list, type a custom topic, tap "Crear leccion" -- lesson generates, custom topic appears in "Mis lecciones" on subsequent visits.

## 2026-07-01 — BUILD 16 LIVE: no auto-regen + manual regenerate + custom lessons
**From Gabby's feedback (regenerating an already-loaded lesson wastes credits; wants to type her own topic).**
- **Removed the auto-regen** (`_v!==2` line in openLeccion). A cached lesson of any version now always loads free; old-format lessons render via backward-compat fallbacks. NEVER auto-regenerate (credit rule saved to memory).
- **Manual `leccRegen()` + "regenerar" button** — regenerates a lesson only on explicit tap.
- **Custom lessons:** `leccCreateCustom` input on the Lecciones screen ("¿Qué quieres aprender?") builds a topic, generates a lesson, caches it (esLessonCache now carries `label`; React ES_LESSON_CACHE stores it; applyEsLessons rebuilds `window.__customTopics`), and lists it under "Mis lecciones" so it reopens for free after reload.
- Accent fix "Regenerando lección". BUILD 16.
**Reviewed (Approved): credit fix airtight, custom round-trip sound, slug safe ([a-z0-9-]), user label esc()'d.** Deferred minor: all-symbols custom input collapses to `custom-tema` (low stakes).
**Committed/Pushed:** YES — main 906464a, live on Pages.
**On-device (BUILD 16):** reopen ser vs estar (or any loaded lesson) → loads instantly, no regen; "regenerar" refreshes on tap; type a topic → "Crear lección" generates it and it appears under "Mis lecciones".

## 2026-07-02 — Lecciones buttons re-theme + reiniciar test (BUILD 17)
**Working on:** Lecciones screen polish + a retake control, per Gabby's on-device feedback that "Lección de hoy" and "Crear lección" were ugly, off-theme, badly placed (they used the big `.mode` home-card class).
**Files changed:** `veo-y-digo-source.html` (edited + re-baked into `pebble-app.html` via `scratchpad/rebake.py "lecc-today"`), `pebble-app.html` (PEBBLE_BUILD 16 → 17 + note).
**What changed:**
- Lecciones list header redesigned to the theme (Option B, approved): title + "done / total" count in a topbar, a gold→terracotta progress bar, a dark ink "Lección de hoy" CTA (Fraunces italic, sun icon, 3D shadow), an "o crea una lección tuya" divider, and a compact inline custom-topic input + olive outline "Crear" button. All wrapped in `#leccHome` so these controls hide when a lesson is open (previously they stayed visible above the lesson).
- `renderLecciones` now fills the count text + bar width; `openLeccion` hides `#leccHome`.
- New **"↺ Reiniciar test"** button in the lesson view (`leccResetTest`): clears `leccState.answers` and re-renders from the cached lesson, so the whole test resets for a retake. NO API call — respects the credit rule. (Brand-new questions remain the separate "regenerar" button.)
- CSS added for `.lecc-topbar/.lecc-count/.lecc-bar/.lecc-today/.lecc-or/.lecc-make-b/.lecc-test-actions/.lecc-reset`.
**Verify:** checkblock JS SYNTAX OK on renderLeccionView/renderLecciones/leccResetTest; rebake OK marker-present; rendered the real source list + a sample lesson view headless (both correct, see scratchpad/lecc-live.png, lecc-view.png).
**Committed:** local only — NOT pushed (awaiting Gabby's OK to deploy).
**Notes for next session:**
- On device: swipe-close webclip, reopen, Settings should read BUILD 17. Check the new CTA/bar/inline create on the Lecciones list, and "Reiniciar test" on a lesson resets all answers with no regeneration.
- Not in scope but noticed: the two bottom lesson buttons ("Hacer tarjetas de esta leccion", "Terminar") still use the off-theme `.mode` card style; easy follow-up to theme them to match the new reset button.
- Optional polish: shuffle option order on "Reiniciar test" so a retake isn't just position memory (left same-order for v1).

## 2026-07-02 — Lecciones lesson-view buttons themed (BUILD 18)
**Working on:** Follow-up from the previous entry: themed the two remaining off-theme lesson buttons.
**Files changed:** `veo-y-digo-source.html` (re-baked, marker "lecc-finish"), `pebble-app.html` (BUILD 17 → 18).
**What changed:** "Terminar" → solid olive primary CTA (`.lecc-finish`, Fraunces italic, 3D shadow). "Hacer tarjetas de esta leccion" → "Hacer tarjetas" olive outline (`.lecc-makecards`), now paired in a flex row beside "Reiniciar test". Removed the last `.mode`/`.mode primary` cards from the lesson view.
**Verify:** checkblock renderLeccionView JS SYNTAX OK; rebake OK marker-present; headless sample-lesson render shows the three themed buttons correct (scratchpad/lecc-view2.png).
**Committed:** local only — NOT pushed.
**Notes for next session:** BUILD 18 on device check. Optional: shuffle options on Reiniciar test.

## 2026-07-02 — Lecciones: Test nuevo (fresh questions) + rename Repetir test (BUILD 19)
**Working on:** Gabby wants two retake modes: redo the same test, AND generate a whole new set of questions after passing (so she isn't retested on answers she already knows).
**Files changed:** `veo-y-digo-source.html` (re-baked, marker "leccGenTest"), `pebble-app.html` (BUILD 18 → 19).
**What changed:**
- Renamed "Reiniciar test" → **"Repetir test"** (same questions, retake, free, no API — function still `leccResetTest`).
- New **"Test nuevo"** button (`leccNewTest` + `leccGenTest`): explicit-tap call to claude-sonnet-4-6 that regenerates ONLY the practice+quiz (not the whole lesson), tells the model to avoid already-seen questions, swaps them into `leccState.lesson`, clears answers, persists via `esLessonCache` postMessage, re-renders. max_tokens 1500 (cheaper than the 2000 full-lesson gen). Loading + error states inline.
- Layout: [Repetir test][Test nuevo] row (gold Test nuevo stands out), then full-width "Hacer tarjetas", then olive "Terminar".
**Credit rule:** compliant — generation only on explicit user tap, questions-only (smaller call), no auto-regen. This is the user-requested paid path, distinct from the free Repetir test.
**Verify:** checkblock OK on renderLeccionView / leccNewTest / leccGenTest; rebake OK marker-present; headless sample-lesson render shows the four themed buttons correct (scratchpad/lecc-view3.png).
**Committed:** local only — NOT pushed.
**Notes for next session:** BUILD 19 device check: "Test nuevo" should show "Creando un test nuevo…" then load different questions; "Repetir test" resets same ones. Both need a valid API key for Test nuevo (Repetir works offline). Optional: a tiny "usa IA" hint under Test nuevo; shuffle options on Repetir.
