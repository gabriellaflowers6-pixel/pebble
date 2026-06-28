# Pebble — Spanish app: next-session prompt

Paste this to start the next session.

---

We're building out the **Veo & Digo** Spanish-learning app embedded inside **Pebble** (`Desktop/my projects/pebble/pebble-app.html`). Read `pebble/WORKLOG.md` and the memory note `project_pebble_spanish_app.md` first. Key facts so you don't relearn them the hard way:

**How the embed works / how to edit the Spanish app**
- Editable source: `pebble/veo-y-digo-source.html` (~5.5MB). Edit THAT, never the base64.
- It's base64'd into `window.VEO_DIGO_B64` in `pebble-app.html` (a plain `<script>`, not the Babel one) and shown via an iframe (async blob decode).
- Re-bake after editing: `b64 = base64(source, utf-8)`, then regex-replace `window.VEO_DIGO_B64="[^"]*";` in `pebble-app.html`. (See the scratchpad python helpers from last session for the exact pattern.)
- Files are huge — grep/sed/python, don't Read them whole.

**Do not break these**
- `@babel/standalone` is PINNED to `7.23.10`. Unpinning = blank app (the floating CDN compiles to ESM imports). Leave it.
- pebble-app.html is ~15MB now (baked audio). Loads fine; if it grows a lot, split audio into a separate fetched bank.
- Verify any change by injecting a tiny error-capture `<script>` into `<head>` of a /tmp copy, headless `--dump-dom`, and reading `document.title` for `phoneFrame=true ERRS(0)`. Headless `--screenshot` of the top page is unreliable for width — render the Veo app inside a 375px iframe to preview layout.

**AI is live** — Anthropic `sk-ant` key is baked into `DEFAULT_DATA.settings.apiKey` + `window.PEBBLE_API_KEY` fallback; `EspanolPage` postMessages it to the iframe as `window.__claudeKey`. Model `claude-sonnet-4-6`. Browser-direct headers: `x-api-key`, `anthropic-version: 2023-06-01`, `anthropic-dangerous-direct-browser-access: true`.

**Audio** — Kokoro, local + free (Google TTS still 403s, billing off). Pre-baked clips in `FC_AUDIO`, voice `em_alex @0.85`, via `fcPlay()`. Generate with `/opt/homebrew/bin/python3.11` + `kokoro_onnx` (model at `~/.cache/hyperframes/tts`). Conversación live voice = local server `pebble/kokoro-tts-server.py` (Dora/`ef_dora`, port 7070) — start it for the nice voice; app falls back to device voice otherwise.

**Done:** embed + Español page, Atajos (gerund hack) + audio, polished jar, Study→Español link, Oz Modo Escucha (all 8 chapters audio + listen/order/meaning; comprehension Qs for Ch.1–3), Diario autocorrect, Conversación (live chat w/ Dora + subtitles). All committed, NOT pushed.

**Pick up here (roadmap, in priority order):**

**NEW — phone-first priorities (Gabby, 2026-06-28):** Pebble is used MOSTLY ON HER PHONE. These three are now top of the list.
- **A. Voice must work on the phone without the Mac.** The nice Dora voice currently needs the local Kokoro server (`kokoro-tts-server.py`, 127.0.0.1:7070) running on the Mac. It dies when the terminal/session ends and the phone can't reach 127.0.0.1 anyway (and https page → http localhost is mixed-content blocked). So on the phone there is effectively NO Dora. Fix: pick a voice path that needs no running Mac — (a) device `SpeechSynthesis` Spanish voice (free, offline, iOS voices like Mónica/Paulina are decent), or (b) a cloud TTS API called browser-direct (best quality, costs per call, works anywhere). DECISION NEEDED from Gabby. Until then the app already falls back to the device voice.
- **B. Merge Conversación (Dora chat) into the main "talk to Pebble" chat.** Instead of a separate Veo `#convo` screen, add a button/toggle in Pebble's own chat that switches it into live Spanish-conversation mode. One chat, a mode switch.
- **C. Fix the microphone (speak + type both work).** The 🎤 button doesn't work. Goal: speak to the AI, it understands and replies (voice+subtitles), AND typing still works. Likely cause: the iframe embedding the Veo app is missing `allow="microphone"` (and possibly `autoplay`) permission delegation, so `SpeechRecognition` is blocked. Also handle iOS Safari `webkitSpeechRecognition` quirks. Investigate the iframe `allow=` attr in `EspanolPage` first.

**Original roadmap (still open):**
1. **Translator button** — a button in Pebble's top corner (Header, next to settings/jar) that opens a quick EN↔ES translator panel. Uses the baked key. Self-contained.
2. **Recommendations** — AI suggestions in the Spanish app. ASK Gabby the scope first: next story to read / words to drill / a daily "try this".
3. **Oz Ch.4–8 comprehension questions** — author into `ozQ` (the engine already handles them, currently skips when absent). Ch.7 is ~104 pages; consider whether to author all or sample. Sentences via the extract snippet in `generate_oz1_audio.py`.

Never push without asking. Commit liberally (private repo).
