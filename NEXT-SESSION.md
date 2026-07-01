# Pebble — next-session prompt

Paste this to start the next session.

---

## >>> READ FIRST <<<

Read `WORKLOG.md` (newest entries at the bottom) and the memory note `project_pebble_spanish_app.md`. Current as of 2026-06-30.

## Repo location (IMPORTANT)

Pebble now lives at **`~/dev/pebble`** (moved off `Desktop/my projects/` on 2026-06-30 per CLAUDE.md rule #5, iCloud was evicting `.git` and killing repos). Work here, not on the Desktop. GitHub: `gabriellaflowers6-pixel/pebble`.

## State: BUILD 13, LIVE on main + GitHub Pages

Live link: `https://gabriellaflowers6-pixel.github.io/pebble/pebble-app.html`

`main` = `origin/main` = the Lecciones merge. The `lecciones` branch is merged and also kept on origin as a backup.

BUILD number is at the top of Settings (`PEBBLE_BUILD` in `pebble-app.html`), the cache-confirmation tool (no service worker; iOS caches the webclip hard). Bump it on every user-visible change. Currently **BUILD 13**.

## Shipped and now live (BUILD 11-13)

- **BUILD 11** — keyboard gap fix: `.phone-frame` tracks `visualViewport.offsetTop` via `--kb-top` so the chat composer sits flush above the iOS keyboard (the offsetTop translate that BUILD 2/3 predicted but never added).
- **BUILD 12** — flashcard flip-back spoiler fix: `renderCard` snaps the 3D card to the front without animating, so tapping next no longer flashes the new card's answer.
- **BUILD 13 — Lecciones (new Spanish lessons feature).** New `lecciones` screen in the Veo source: a phased road-to-fluency checklist (`LECCIONES` const), "Lección de hoy" button, home nav entry. Each topic generates a ~10-min lesson via Claude (`leccGenerate`, claude-sonnet-4-6, cached to `data.esLessons` on the React side, posted in via `esLessonsData` / out via `esLessonCache`+`esLessonProgress`; cache-poisoning guarded by res.ok + shape check). Lesson view = teach + pattern + multiple-choice practice (with "why") + mini-quiz (0.6 pass marks the topic done). Hear (`leccHear`/fcSpeak) + save (`leccSaveEx` → `saveEsCard` → themed `lecciones` flashcard deck) on each example. "teach me X" / "enseñame X" in the Spanish chat (`teachSpanish` in ChatBar; speaks only the examples). Spec: `docs/superpowers/specs/2026-06-29-spanish-lecciones-design.md`; plan: `docs/superpowers/plans/2026-06-30-spanish-lecciones.md`. Built subagent-driven, every task + the whole branch reviewed.

## DO THIS FIRST: on-device confirmation (Gabby, iPhone)

Runtime was never exercised in a browser (all verification was static + the AI paths need her device-local key). Have her:
1. Swipe-close the webclip, reopen, Settings → confirm **BUILD 13** (if lower, it is CACHE — no service worker; consider a network-first SW so the PWA always updates).
2. API key pasted in Settings (device-local; needs a fresh non-revoked key from console.anthropic.com).
3. Spot-check: keyboard sits flush above the chat (no gap); flashcard next has no answer-flash; **Lecciones** → tap a topic → lesson generates → mini-quiz 60%+ checks it off → reopen loads from cache → oír/guardar an example → it appears in Tarjetas "Lecciones" deck; chat "teach me the future tense" returns an explanation + examples.

## Lecciones follow-up polish (documented, non-blocking, from the final review)

- Home "Lecciones" `.mode` button has no `.icon` SVG like its siblings (renders without the icon column).
- `leccFinishQuiz` does not disable its button → a double-tap within 1400ms enqueues a duplicate timer + redundant `esLessonProgress` post (not data-corrupting). Fix: disable `#leccFinishBtn` at the top of the function.
- The iframe message listener does not validate `e.origin` (matches the existing esFlashSets pattern; device-local app).
- `teachSpanish` stores the English teach text in the first sentence's `es` slot, so its per-sentence hear/save treats English as Spanish (edge-case only; TTS already skips it).

## How to work on Pebble (important)

- Two huge files: `pebble-app.html` (~15MB) and `veo-y-digo-source.html` (~11MB) with base64 blobs. **NEVER read them whole.** Grep/sed/python with targeted anchors; edit via python string-replace with `assert count==1`.
- Build helpers live in `scratchpad/` (gitignored): `rebake.py` (re-encode Veo source → `window.VEO_DIGO_B64` + round-trip + marker check), `checkblock.py` (node --check a Veo plain-JS block), `checkbabel.js` (Babel-transform a React JSX block — node --check does NOT parse JSX). Verification model: no test framework; use these + on-device.
- The Veo Spanish app is base64'd into `window.VEO_DIGO_B64`. Edit `veo-y-digo-source.html`, then RE-BAKE (`python3 scratchpad/rebake.py "<marker>"`) and confirm round-trip. React-side edits (pebble-app.html only) do NOT need a re-bake — check with `node scratchpad/checkbabel.js pebble-app.html "<marker>"`.
- `@babel/standalone` PINNED to 7.23.10 — never change.
- Key is device-local; never bake it into source (it was public + auto-revoked before). Durable fix = a Netlify/serverless key proxy so no key lives client-side.
- **git index can corrupt** mid-session (external `git ls-files` watcher collides). Symptom: `git ls-files` → 0, everything shows deleted. Fix: `rm -f .git/index.lock; git reset --mixed HEAD`, then recommit. Working files are never lost. (Less likely now that the repo is at `~/dev`.)
- Never push to main / deploy without asking Gabby.

## Remaining roadmap (older, pick with Gabby)

- **Mic button** — 🎤 doesn't work (iOS SpeechRecognition; iframe `allow="microphone"` quirks).
- **Translator button** — quick EN↔ES panel (Header corner).
- **Recommendations** — AI suggestions; ask scope first.
- **Oz Ch. 4-8 comprehension questions** — author into `ozQ`.
- **Phone-voice decision** — device SpeechSynthesis (free) vs cloud TTS (paid). Mónica Enhanced = iOS Settings download, not code.
- **Serverless key proxy** — so the key is never client-side / public.
- **Lecciones v2** — typed-answer + build-the-sentence question types (research says typed recall beats multiple choice); cumulative spaced-repetition review + a daily streak.
