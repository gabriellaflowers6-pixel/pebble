# Flashcard Editor — Design Spec

Date: 2026-06-29
Status: Approved design, ready for implementation plan (Phase 1 first)

## Goal

Let the user manage the Spanish flashcard deck(s) from inside Pebble: see a list of cards, edit and delete them, add cards by hand (no duplicates), add cards suggested from recent Spanish chats, and (Phase 2) use AI to suggest new words and to categorize the deck and split categories into their own themed decks (Verbs, Body Parts, Hobbies, etc.).

## Context and constraints (existing code)

- Cards live in the **main app** state: `data.esFlash.sets` (a `useReducer` store in `pebble-app.html`). Card shape: `{ kind: 'word' | 'frase', es, en }`. Dedup uses `convoCardKey(card)`.
- Today there is **one rolling deck**: `CONVO_DECK_ID = 'convo-all'`, label `'Conversación'`. Created by `ES_FLASH_NEW_SET`; cards added by `ES_FLASH_ADD_CARD` (see `saveSpanishCard`, ~line 2946).
- A migration `useEffect` on `[data.esFlash]` folds any legacy per-conversation decks into `convo-all` via `ES_FLASH_MERGE_ALL` / `mergeConvoSets`. **This must not swallow new themed decks.**
- The Veo Spanish app (iframe, `veo-y-digo-source.html`) shows the deck in its **Tarjetas** section. Sync is **one-way**: main app posts `{ type: 'esFlashSets', sets }` (`pebble-app.html:5817`) → Veo `applyEsFlashSets` (`veo-y-digo-source.html:5228`) registers them as `themeDecks` for the Tarjetas picker. There is no edit path back from the iframe.
- API key is device-local in `data.settings.apiKey`; AI calls are browser-direct to Anthropic with the standard headers (`x-api-key`, `anthropic-version: 2023-06-01`, `anthropic-dangerous-direct-browser-access: true`), model `claude-sonnet-4-6` (or the model already used for Spanish chat).

## Approach (chosen: A)

The editor is a panel in the **main app** (that is where the data, reducers, API key, and chat history live). Entry point: a **"Manage cards"** button in the Veo Tarjetas section that posts a new message (`{ type: 'openFlashEditor' }`) to the parent; the main app opens the editor panel. Edits dispatch to the `esFlash` reducer; the existing sync effect re-posts `esFlashSets` so the Tarjetas view updates automatically.

Rejected: building the editor inside the Veo iframe with a new two-way sync — more moving parts and failure modes for no benefit, since the data already lives in the main app.

## Data model changes

- Support **multiple named decks** (already structural: `esFlash.sets` is an array of `{ id, label, date, cards, ... }`). `Conversación` stays the default catch-all.
- Add a `themed: true` flag to decks created by splitting. Update `mergeConvoSets` / the `ES_FLASH_MERGE_ALL` path to **only** merge legacy convo-style sets and **never** a `themed` deck.
- Add an optional per-card `cat` (category string) set by AI organize (Phase 2). Absent until organized.
- Add a capped **recent-chat-words buffer** for the "from your chats" suggestions: `data.esFlash.recent` = last 50 `{ es, en, kind }` pairs appended whenever a Spanish chat reply is parsed into words. Suggestions = `recent` minus cards already in the target deck (by `convoCardKey`).

## Reducer actions to add

- `ES_FLASH_DELETE_CARD { setId, cardKey }` — remove one card from a deck.
- `ES_FLASH_EDIT_CARD { setId, cardKey, es, en }` — update a card's text; re-derive its key; keep dedup (no-op if the edit collides with an existing card, surface "ya guardada").
- `ES_FLASH_MOVE_CARDS { fromSetId, toSetId, cardKeys }` — move cards between decks (used by split).
- `ES_FLASH_PUSH_RECENT { items }` — append to the capped `recent` buffer (deduped, max 50).
- `ES_FLASH_NEW_SET` already exists for creating decks (pass `themed: true` for themed decks).
- Optional deck management: `ES_FLASH_RENAME_SET`, `ES_FLASH_DELETE_SET`.

## UI — Phase 1 (editor core, ships first)

A scrollable panel in the main app:

- **Header:** deck switcher (dropdown; only shown once more than one deck exists) + card count.
- **List:** one row per card — Spanish (`es`) and English (`en`); tap a row to edit the text inline; 🗑 to delete. Editing re-keys and re-checks dedup.
- **Add your own:** two inputs (Spanish, English) + Add. Dedup check via `convoCardKey` against the target deck → show "ya guardada" if it already exists, otherwise add.
- **From your chats:** a section listing items from `data.esFlash.recent` not already in the deck; tap to add (deduped). 

No AI in Phase 1.

## UI — Phase 2 (AI)

- **Suggest words:** button → Claude prompt: "given these existing words `<deck es list>`, return N new useful related Spanish words as JSON `[{es,en,kind}]`". Parse with `stripJsonFences` + `try/catch`; render as tappable chips; tap adds (deduped). Disabled with a hint when no API key.
- **Organize:** button → Claude prompt: "given these cards `<list>`, assign each a short category (verb, noun, body part, hobby, food, feeling, ...). Return JSON mapping card→category." Set each card's `cat`; regroup the list under category headers. Each header group shows **"Make this its own deck"** → `ES_FLASH_NEW_SET({ themed: true, label: <category> })` + `ES_FLASH_MOVE_CARDS` of that group out of Conversación. The user chooses which groups to split; nothing splits automatically.

## Sync and persistence

- `esFlash` changes flow through the existing localStorage + Gist persistence (auto-save on `data` change).
- The existing effect posts `esFlashSets` to the Veo iframe when the deck changes, so Tarjetas reflects adds/edits/deletes/splits. Confirm the post effect's dependency includes `data.esFlash` (or fires on `data`); if not, extend it.

## Edge cases

- **Dedup scope:** within the target deck. Splitting **moves** cards (not copies), so a word is never duplicated across decks.
- **Migration safety (critical):** the convo-merge migration must skip `themed` decks; verify across a reload that a themed deck survives.
- **Malformed AI JSON:** `stripJsonFences` + `try/catch`; on failure, show a gentle error and change nothing.
- **No API key:** AI buttons disabled with "add your key in Settings" hint.
- **Empty deck / empty suggestion list:** show a friendly empty state.

## Testing (desktop, local http server)

- List renders the deck; add/edit/delete dispatch and re-render correctly; dedup shows "ya guardada".
- Deck switcher works; split creates a `themed` deck and moves the right cards out of Conversación.
- Reload: themed deck survives the merge migration (does not get folded back).
- Veo iframe receives updated `esFlashSets` after an edit (assert the post fired).
- Phase 2: verify the prompt/parse path with a representative payload; chips add deduped; organize groups and split work.

## Phasing

- **Phase 1:** editor core (list, edit, delete, manual add with dedup, from-your-chats suggestions, the recent buffer, the delete/edit/move/push-recent reducer actions, the Veo "Manage cards" entry + `openFlashEditor` bridge). No AI.
- **Phase 2:** AI suggest words + AI organize/split into themed decks, plus the `themed` flag and migration-skip.
