# Pebble: next-session prompt

Paste this to start the next session.

---

## >>> READ FIRST <<<

Read `WORKLOG.md` (newest entries at the bottom) and the memory note `project_pebble_spanish_app.md`. Current as of 2026-07-09.

## Repo location (IMPORTANT)

Pebble now lives at **`~/dev/pebble`** (moved off `Desktop/my projects/` on 2026-06-30 per CLAUDE.md rule #5, iCloud was evicting `.git` and killing repos). Work here, not on the Desktop. GitHub: `gabriellaflowers6-pixel/pebble`.

## State: BUILD 25, LIVE on main + GitHub Pages

Live link: `https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html` (same URL every deploy; it does not change).

`main` = `origin/main`. All work commits straight to `main` in rapid-iterate mode; the old `lecciones` branch is on origin as a backup.

BUILD number is at the top of Settings (`PEBBLE_BUILD` in `pebble-app.html`), the cache-confirmation tool (no service worker; iOS caches the webclip hard). Bump it on every user-visible change. Currently **BUILD 25**.

**CREDIT RULE (Gabby):** never auto-regenerate cached AI content; each Claude generation costs money. Generate once, cache, only regenerate on an explicit tap. Applies to lessons, worksheet "Más preguntas", and the new flashcard AI (translate / create-deck / generar-más). Treat AI generations as expensive.

## Shipped and now live (BUILD 11-25)

- **BUILD 11-16 (Lecciones + keyboard/flashcard fixes):** keyboard gap fix (`--kb-top`), flashcard flip-back spoiler fix, and the whole **Lecciones** Spanish-lessons feature (checklist, `leccGenerate` AI lessons cached to `data.esLessons`, v2 formatting with real tables + highlighted examples, heart-to-save "Guardadas", per-lesson `Leccion: X` decks via `esMakeDeck`, no-auto-regen + manual "regenerar" + custom "Mis lecciones" topics). Specs in `docs/superpowers/specs/2026-06-29-*` and `2026-07-01-*`.
- **BUILD 17-19 (Lecciones polish):** themed the Lecciones list/CTA + lesson-view buttons; "Repetir test" (same questions, free) + "Test nuevo" (fresh questions via AI, explicit tap).
- **BUILD 20:** iOS text-size fix, `html { -webkit-text-size-adjust:100% }` in the Veo source; Safari was font-boosting iframe text so words spilled past edges. If spill recurs, next lever = overflow guards on `.lecc-table` / lesson view.
- **BUILD 21: Hoja de Trabajo "modo papel".** Second worksheet mode per category: a 📄 button opens a paper page (word key on top, numbered tap-to-fill questions, score, Repetir) + "✦ Más preguntas" (AI generates ~6 more on explicit tap, cached in `data.wsExtra` via `wsExtra`/`wsExtraData` postMessage). Built subagent-driven; specs/plan `docs/superpowers/{specs,plans}/2026-07-08-hoja-papel*`.
- **BUILD 22: flashcard audio fix.** `sayCard` spoke `c.word` which is ENGLISH for conversation cards (Spanish is in `c.front`); now prefers `c.front`. Picture cards unaffected.
- **BUILD 23: editar lista.** Surfaced the existing `FlashEditor` from the flashHome study screen, an "editar lista" button (shows only for editable esFlash decks in `window.__esFlashNames`), posts `{openFlashEditor, deckLabel}`, parent pre-selects the matching deck.
- **BUILD 24: AI translate in add box.** "↔ traducir" button in `FlashEditor`'s add card: type either box, `translate()` fills the other (EN->ES if english filled, else ES->EN), review then añadir. `aiCall`, explicit tap, key-gated.
- **BUILD 25: create deck by subject.** "mazo nuevo por tema" (subject + size 5/10/15/20 -> `createDeck` AI builds a themed deck with a Spanish name + es/en cards; `ES_FLASH_NEW_SET` now stores `subject`) + "✨ generar 5 más" on subject decks (`generateMore`, reducer dedups). All flashcard management lives in `FlashEditor` (pebble-app.html). Specs `docs/superpowers/specs/2026-07-09-flashcard-*`.

All BUILD 20-25 verified in-browser (Chrome MCP, stubbed fetch for AI paths so no spend) and LIVE. Known-minor deferred: "+N añadidas" toast can overcount under machine-speed double-tap (button is disabled during the call, so real usage is fine; reducer guarantees no duplicate cards).

## DO THIS FIRST: on-device confirmation (Gabby, iPhone)

All builds through 25 are verified statically/in-browser + reviewed, but runtime is confirmed on Gabby's phone as she goes (she tests + gives feedback each round). Standing checks after any push:
1. Swipe-close the webclip, reopen, Settings → confirm the latest BUILD number (if lower, it is CACHE: no service worker; consider a network-first SW so the PWA always updates).
2. API key pasted in Settings (device-local; needs a fresh non-revoked key from console.anthropic.com). Gabby paid the account 2026-07-09 so AI works again.
3. Flashcards spot-check (BUILD 22-25): conversation-card 🔊 says the SPANISH; Tarjetas → "editar lista" opens the editor on the current deck; "↔ traducir" fills the other box; "mazo nuevo por tema" (e.g. "beach") creates "La playa" with es/en cards; "✨ generar 5 más" appends on a subject deck.
4. Worksheet spot-check (BUILD 21): Hoja de Trabajo → 📄 on a category → paper page + "✦ Más preguntas".
5. Lecciones spot-check: lesson shows a real table + highlighted/labeled examples + tips-per-line + English on the list; reopening a loaded lesson is instant with NO regeneration; "regenerar" / "Test nuevo" refresh on tap; custom topic → "Crear lección" → "Mis lecciones"; heart → "Guardadas".

## Lecciones follow-up polish (documented, non-blocking)

- Home "Lecciones" `.mode` button has no `.icon` SVG like its siblings (renders without the icon column).
- The iframe message listener does not validate `e.origin` (matches the existing esFlashSets pattern; device-local app).
- `teachSpanish` (chat) stores the English teach text in the first sentence's `es` slot, so its per-sentence hear/save treats English as Spanish (TTS already skips it; edge-case only). The chat "teach me X" path did NOT get the v2 formatting (table/highlight) or the credit-conscious caching; it is a separate lighter path.
- Custom-topic slug: an all-symbols input (e.g. "!!!") collapses to `custom-tema` and could overwrite a prior such entry (low stakes).
- Considered but NOT done: a "regenerar todas al formato nuevo" bulk upgrade (rejected on credit grounds; upgrades are one-at-a-time via the manual button).

## How to work on Pebble (important)

- Two huge files: `pebble-app.html` (~15MB) and `veo-y-digo-source.html` (~11MB) with base64 blobs. **NEVER read them whole.** Grep/sed/python with targeted anchors; edit via python string-replace with `assert count==1`.
- Build helpers live in `scratchpad/` (gitignored): `rebake.py` (re-encode Veo source → `window.VEO_DIGO_B64` + round-trip + marker check), `checkblock.py` (node --check a Veo plain-JS block), `checkbabel.js` (Babel-transform a React JSX block: node --check does NOT parse JSX). Verification model: no test framework; use these + on-device.
- The Veo Spanish app is base64'd into `window.VEO_DIGO_B64`. Edit `veo-y-digo-source.html`, then RE-BAKE (`python3 scratchpad/rebake.py "<marker>"`) and confirm round-trip. React-side edits (pebble-app.html only) do NOT need a re-bake: check with `node scratchpad/checkbabel.js pebble-app.html "<marker>"`.
- `@babel/standalone` PINNED to 7.23.10: never change.
- Key is device-local; never bake it into source (it was public + auto-revoked before). Durable fix = a Netlify/serverless key proxy so no key lives client-side.
- **git index can corrupt** mid-session (external `git ls-files` watcher collides). Symptom: `git ls-files` → 0, everything shows deleted. Fix: `rm -f .git/index.lock; git reset --mixed HEAD`, then recommit. Working files are never lost. (Less likely now that the repo is at `~/dev`.)
- Never push to main / deploy without asking Gabby.

## Remaining roadmap (older, pick with Gabby)

- **Mic button**: doesn't work (iOS SpeechRecognition; iframe `allow="microphone"` quirks).
- **Translator button**: quick EN↔ES panel (Header corner).
- **Recommendations**: AI suggestions; ask scope first.
- **Oz Ch. 4-8 comprehension questions**: author into `ozQ`.
- **Phone-voice decision**: device SpeechSynthesis (free) vs cloud TTS (paid). Mónica Enhanced = iOS Settings download, not code.
- **Serverless key proxy**: so the key is never client-side / public.
- **Lecciones v2**: typed-answer + build-the-sentence question types (research says typed recall beats multiple choice); cumulative spaced-repetition review + a daily streak.
