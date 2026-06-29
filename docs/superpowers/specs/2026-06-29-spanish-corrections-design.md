# Spanish Chat Corrections + Explain — Design Spec

Date: 2026-06-29
Status: Approved design, ready for implementation plan

## Goal

In the Spanish chat, under each message the user writes in Spanish, show a "más natural" version of what they wrote (always), with an "explicar" button that breaks down what was off or different (grammar/word usage, e.g. estar vs ser, pronoun use), and a "guardar" button that saves the natural phrase as a flashcard. The correction is produced by the same AI call that writes Pebble's reply (no extra cost); the explanation is a second call only when the user taps "explicar".

## Context and constraints (existing code, `pebble-app.html`)

- Spanish chat lives in the main app: `spanishMode` state, `esMsgs` (the Spanish message list), `sendSpanish(userText)` (sends the user message + calls the AI), `SpanishChatBubble` (~line 2563) renders Spanish messages, `speakSpanish` for TTS.
- The Spanish reply is requested with a system prompt (`ES_SYSTEM`) and the model returns JSON shaped `{ sentences: [{ es, en, words: [{ w, t }] }] }`, parsed with `stripJsonFences` + `JSON.parse`.
- Flashcards: `saveSpanishCard(kind, es, en)` (~2946) dispatches `ES_FLASH_ADD_CARD` to the `convo-all` deck, deduped by `convoCardKey`, toast "ya guardada" / "guardada". The FlashEditor + reducer actions already exist.
- API key: `data.settings.apiKey`, browser-direct Anthropic calls with standard headers; model already used for Spanish replies.
- No em dashes / no AI-writing patterns in user-facing copy.

## Data flow

1. **Correction (folded into the reply):** extend `ES_SYSTEM` and the reply JSON to also return a `correction` object for the user's message:
   `{ "correction": { "fixed": "<the most natural Spanish way to say what the user wrote>", "en": "<English of fixed>", "changed": <true if it differs from what the user wrote, else false> } }`
   The reply JSON becomes `{ sentences: [...], correction: {...} }`. Parse both; if `correction` is missing/malformed, skip it (reply still shows).
2. **Attach to the user message:** when `sendSpanish` adds the user's message to `esMsgs`, store the returned `correction` on that message object (`{ role:'user', es, correction }`). This persists with the chat.
3. **Explain (on tap):** a second AI call with a focused prompt (below) returning a short English breakdown; cache it on the message (`message.explanation`) so it is fetched once.
4. **Save (on tap):** `saveSpanishCard('frase', correction.fixed, correction.en)` — reuses dedup + toast.

## Prompts

- **Reply prompt addition (to `ES_SYSTEM`):** "Also return a `correction` object: `fixed` = the most natural Spanish way to say what the user just wrote (keep their meaning), `en` = its English, `changed` = true only if it differs from what they wrote. If they wrote in English or nonsense, set `changed` false and `fixed` to their text."
- **Explain prompt (separate call):** "The learner wrote: '<user es>'. A more natural version is: '<fixed>'. In 1-3 short, friendly English sentences, explain the key difference(s) — focus on grammar/word choice (verb choice like estar vs ser, pronouns, gender, word order). Be concrete and encouraging. Plain text, no markdown."

## UI

- In `SpanishChatBubble` (or the user-message branch of the `esMsgs` render), when a user message has a `correction`:
  - Show a compact correction line under the bubble: if `changed`, label it "más natural:" + `fixed` (+ `en` muted); if not changed, a subtle "✓ suena bien" with the `fixed`/`en` still available.
  - Buttons row: **explicar** (loads `explanation` on tap, shows a small spinner, then expands the text inline; cached after first load) and **＋ guardar** (calls `saveSpanishCard`, shows the existing toast).
  - Style to match the existing Spanish bubble look (muted small text, pill buttons).
- No API key → buttons disabled with a hint (mirror existing behavior); the folded correction simply will not be present.

## Persistence

- `correction` and (once fetched) `explanation` live on the user message inside `esMsgs`. `esMsgs` persists with the chat data (same as the rest of `data.chat` / the Spanish conversation store), so corrections survive scroll and reload.

## Edge cases

- `changed === false` (already natural): show the "✓ suena bien" affirmation, still allow save/explain (explain can say "already natural").
- Malformed/missing `correction` in the reply JSON: skip silently, reply still renders.
- Explain call fails (network/no key): show a gentle inline "no pude explicar ahora".
- Save dedup: reuse `convoCardKey`; "ya guardada" if present.
- Non-Spanish input: `changed:false`, no correction shown (or a gentle nudge — keep simple: just no correction line).

## Testing (desktop, local http server)

- Mock a Spanish reply payload containing `correction` and assert the correction line renders under the user message with the right `fixed`/`en` and `changed` styling.
- Tap "explicar": a second call fires and the explanation expands; second tap does not re-fetch (cached).
- Tap "guardar": a card is added (deduped), "ya guardada" on repeat.
- Missing `correction`: reply still renders, no correction line, no error.
- Reload: a stored correction/explanation persists on the message.

## Out of scope (separate features)

- Saving the explanation itself as a "fact/quote" (that is the facts/quotes feature).
- Corrections in the Veo iframe's own inputs (Diario, etc.) — this is the main-app Spanish chat only.
