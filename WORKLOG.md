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
