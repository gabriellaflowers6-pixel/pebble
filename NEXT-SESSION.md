# Pebble — next-session prompt

Paste this to start the next session.

---

## >>> READ FIRST <<<

Read `WORKLOG.md` (newest entries at the bottom) and the memory note `project_pebble_spanish_app.md`. Everything below is current as of 2026-06-29.

## State: BUILD 10, all pushed to origin/main + live on GitHub Pages

Live link: `https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html`

There is a **BUILD number** shown at the top of Settings (`PEBBLE_BUILD` / `PEBBLE_BUILD_NOTE` consts in `pebble-app.html`). It is the cache-confirmation tool: if Settings shows the latest BUILD, the phone is on fresh code. **Bump it on every user-visible change.** Currently **BUILD 10**.

**Shipped this session (BUILD 1-10), all on main + Pages:**
1. API key is device-local (no more resetting) — removed apiKey from the URL hash (getHashCreds/updateHashCreds); the frozen home-screen URL no longer overwrites the pasted key.
2-3. Keyboard: chat composer is a `contenteditable` (`.pebble-ce`, no iOS form bar/autofill); keyboard-aware shrink (`--app-h`, html.kb-chat) is chat-only so Atajos/Journal are normal; `.phone-frame` is `position:fixed` on mobile to kill the gap.
4. Flashcard editor — `FlashEditor` component, opened by "Administrar tarjetas" in the Veo Tarjetas section (posts `openFlashEditor`). List/add/edit/delete, dedup.
5. Slower Spanish voice (speakSpanish + Veo convo voice rate 0.95 → 0.85).
6. Spanish corrections — reply JSON now returns `correction{fixed,en,changed}`; SpanishChatBubble user branch shows it + `explicar` (separate cached call) + `＋ guardar`.
7. Flashcard "de tus chats" suggestions — sendSpanish pushes reply words to `data.esFlash.recent`.
8. Heart quotes + fun facts on the picks page (NotebookPage); scrollable "saved" section with remove. Reducer: SAVE_PICK dedups + author, added REMOVE_SAVE.
9. Modo Escucha fix — wrong word-order gives "Ver respuesta y seguir" (escRevealOrder), no longer traps; fixed finish 🎉. (Veo source, re-baked.)
10. Flashcard Phase 2 AI — `sugerir palabras` + `organizar` (categorizes → per-category "make a deck" splits into themed decks). Migration made themed-safe (mergeConvoSets/MERGE_ALL/needsMerge skip `themed` decks).

## DO THIS FIRST: on-device confirmation (Gabby, iPhone)

Nothing this session was confirmed end-to-end on her phone. Have her:
1. Open the link, Settings → confirm it says **BUILD 10** (if not, it's a CACHE problem — there is NO service worker; consider adding a network-first SW so the PWA always updates).
2. Make sure her API key is pasted in Settings (device-local now; needs a fresh, non-revoked key from console.anthropic.com).
3. Spot-check: Spanish message → correction shows; flashcard editor → ✨ organizar splits into themed decks; heart a quote; the keyboard sits above the chat with no gap; voice is slower.

## How to work on Pebble (important)

- Two huge files: `pebble-app.html` (~15MB) and `veo-y-digo-source.html` (~11MB) with base64 blobs. **NEVER read them whole.** Grep/sed/python with targeted anchors; edit via python string-replace with `assert count==1`. Verify with a local server (`python3 -m http.server PORT`) + Chrome + the javascript_tool (programmatic `.focus()` won't fire focus events in an automation tab — dispatch synthetic FocusEvent/InputEvent).
- The Veo Spanish app is base64'd into `window.VEO_DIGO_B64`. Edit `veo-y-digo-source.html`, then RE-BAKE (base64 → regex-replace the assignment) and verify the bake round-trips. React-side changes (pebble-app.html only) do NOT need a re-bake.
- `@babel/standalone` PINNED to 7.23.10 — never change.
- Key device-local; never bake it into source (it was public + auto-revoked before). Durable fix = a Netlify-function proxy so no key lives client-side.
- **git index keeps corrupting** mid-session (an external `git ls-files --recurse-submodules` watcher on the folder, e.g. an open editor, collides). Symptom: `git ls-files` → 0, everything shows deleted. Fix: `rm -f .git/index.lock; git reset --mixed HEAD` (rebuilds index from HEAD, working tree untouched), then recommit. Working files are never lost.
- Never push without asking (private repo, but ask). Commit liberally.

## Remaining roadmap (older, NOT from this session — pick with Gabby)

- **Mic button** — 🎤 doesn't work (iOS SpeechRecognition; iframe `allow="microphone"` + webkitSpeechRecognition quirks).
- **Translator button** — quick EN↔ES panel (Header corner), uses the key.
- **Recommendations** — AI suggestions; ask scope first.
- **Oz Ch. 4-8 comprehension questions** — author into `ozQ`.
- **Phone-voice decision** — device SpeechSynthesis (free) vs cloud TTS (paid, best). Mónica Enhanced = iOS Settings download, not code.
- **Netlify-function key proxy** — so the key is never client-side / public.

Specs/plans this session: `docs/superpowers/specs/2026-06-29-flashcard-editor-design.md`, `docs/superpowers/plans/2026-06-29-flashcard-editor-phase1.md`, `docs/superpowers/specs/2026-06-29-spanish-corrections-design.md`.
