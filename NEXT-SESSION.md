# Pebble: next-session prompt

Paste this to start the next session.

---

## >>> READ FIRST <<<

Read `WORKLOG.md` (newest entries at the bottom) and the memory note `project_pebble_spanish_app.md`. Current as of 2026-07-01.

## Repo location (IMPORTANT)

Pebble now lives at **`~/dev/pebble`** (moved off `Desktop/my projects/` on 2026-06-30 per CLAUDE.md rule #5, iCloud was evicting `.git` and killing repos). Work here, not on the Desktop. GitHub: `gabriellaflowers6-pixel/pebble`.

## State: BUILD 16, LIVE on main + GitHub Pages

Live link: `https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html`

`main` = `origin/main`. All work commits straight to `main` in rapid-iterate mode; the old `lecciones` branch is on origin as a backup.

BUILD number is at the top of Settings (`PEBBLE_BUILD` in `pebble-app.html`), the cache-confirmation tool (no service worker; iOS caches the webclip hard). Bump it on every user-visible change. Currently **BUILD 16**.

**CREDIT RULE (Gabby):** never auto-regenerate a cached lesson; each Claude generation costs money. Generate a topic once, cache forever, only regenerate on an explicit "regenerar" tap. Treat AI generations as expensive.

## Shipped and now live (BUILD 11-16)

- **BUILD 11**: keyboard gap fix: `.phone-frame` tracks `visualViewport.offsetTop` via `--kb-top` so the chat composer sits flush above the iOS keyboard.
- **BUILD 12**: flashcard flip-back spoiler fix: `renderCard` snaps the 3D card to the front without animating.
- **BUILD 13: Lecciones (new Spanish lessons feature).** `lecciones` screen: phased road-to-fluency checklist (`LECCIONES` const), "Lección de hoy", home nav. Each topic generates a ~10-min lesson via Claude (`leccGenerate`, claude-sonnet-4-6, cached to `data.esLessons` on the React side; `esLessonsData` in / `esLessonCache`+`esLessonProgress` out; res.ok + shape guard). Lesson = teach + pattern + multiple-choice practice (with "why") + mini-quiz (0.6 pass marks done). Hear + save on examples. "teach me X" / "enseñame X" in the Spanish chat (`teachSpanish`). Spec: `docs/superpowers/specs/2026-06-29-spanish-lecciones-design.md`; plan: `docs/superpowers/plans/2026-06-30-spanish-lecciones.md`.
- **BUILD 14: lesson formatting v2** (shape `_v:2`): pattern is a real horizontal TABLE (`patternTable{headers,rows}`); examples HIGHLIGHT the target word + TAG it (ser/estar); teach is a short intro + `tips[]` per line; the lesson LIST shows English (`en` on all 34 topics). Renderer has backward-compat fallbacks for old-shape lessons. Spec: `docs/superpowers/specs/2026-07-01-lecciones-formatting.md`.
- **BUILD 15: save + per-lesson decks.** Heart a lesson → "Guardadas" section (`ES_LESSON_SAVE`, `esLessonSave`, `saved` flag). "Hacer tarjetas de esta lección" → themed `Leccion: <topic>` deck from examples + highlighted words (`esMakeDeck`). Spec: `docs/superpowers/specs/2026-07-01-lecciones-save-and-decks.md`.
- **BUILD 16: no auto-regen + custom lessons.** Removed the `_v!==2` auto-regen (was silently re-creating already-loaded lessons = wasted credits). Added a manual "regenerar" button (`leccRegen`, regenerates only on tap). Added a custom-topic input ("¿Qué quieres aprender?" → `leccCreateCustom`) that generates a lesson for any typed topic and lists it under "Mis lecciones" (`window.__customTopics`; `esLessonCache` now carries `label`; React `ES_LESSON_CACHE` stores it; `applyEsLessons` rebuilds custom topics). Spec: `docs/superpowers/specs/2026-07-01-lecciones-no-autoregen-custom.md`.

## DO THIS FIRST: on-device confirmation (Gabby, iPhone)

All builds through 16 are verified statically + reviewed, but runtime is confirmed on Gabby's phone as she goes (she has been testing and giving feedback each round). Standing checks after any push:
1. Swipe-close the webclip, reopen, Settings → confirm the latest BUILD number (if lower, it is CACHE: no service worker; consider a network-first SW so the PWA always updates).
2. API key pasted in Settings (device-local; needs a fresh non-revoked key from console.anthropic.com).
3. Lecciones spot-check: lesson shows a real table + highlighted/labeled examples + tips-per-line + English on the list; reopening a loaded lesson is instant with NO regeneration; "regenerar" refreshes on tap; typing a custom topic → "Crear lección" generates + lists it under "Mis lecciones"; heart → "Guardadas"; "Hacer tarjetas de esta lección" → a "Leccion: X" deck in Tarjetas.

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
