# Create a deck by subject, with "generate more" (item 4)

Date: 2026-07-09. Approved by Gabby ("yeah"). Flashcard batch item 4 of 4. Builds into `FlashEditor` in pebble-app.html (React-side only, no Veo re-bake).

## What

A new "mazo nuevo por tema" section in the editor: type a subject (English or Spanish, e.g. "beach" / "la playa"), pick a starting size (5 / 10 / 15 / 20), tap "crear mazo". Claude generates a themed deck with a Spanish name (e.g. "La playa") full of Spanish-word + English-translation cards. The deck becomes a normal esFlash deck: studyable in the Veo Tarjetas screen, editable via the list (item 2's "editar lista"). On any deck created this way, a "generar 5 más" button adds 5 more related words, skipping duplicates.

## Behavior

### Create deck
- Key check: no `data.settings.apiKey` -> flash "agrega tu clave en ajustes", no call.
- Empty subject -> flash "escribe un tema", no call.
- `aiBusy = 'create'`; button shows "…" and disables during the call.
- Prompt Claude (`aiCall`, claude-sonnet-4-6, device key) for a JSON OBJECT: `{"name":"<short Spanish deck name>","cards":[{"es":"<Spanish word/phrase>","en":"<English>"}]}` with the chosen count of common, useful Latin American Spanish words for the subject. Parse with the existing `parseJ(raw,'{','}')`.
- Validate: `name` is a non-empty string; `cards` is a non-empty array; keep only card items with a string `es`. If invalid -> flash "no pude crear el mazo", no deck created.
- Create: `id = 'deck-' + slug(name) + '-' + Date.now()`; dispatch `ES_FLASH_NEW_SET { id, label:name, date, themed:true, subject:<the subject the user typed> }`; then `ES_FLASH_ADD_CARD` per card (`{kind:'word', es, en}`). Switch the editor to the new deck (`setDeckId(id)`), clear the subject input, flash "mazo creado".

### Generate more (5)
- Shown only when the currently-selected deck has a `subject` (AI-created deck).
- Key check as above.
- `aiBusy = 'more'`.
- Prompt Claude for `{"cards":[{"es","en"}]}` with 5 MORE words for `deck.subject` (fall back to `deck.label` if subject missing), explicitly avoiding the deck's existing `es` values. Parse, validate cards, `ES_FLASH_ADD_CARD` each (reducer dedups by `es`). Flash "añadidas" (or how many landed).

## Reducer change

Extend `ES_FLASH_NEW_SET` to persist an optional `subject`: `{ ..., themed: !!action.themed, subject: action.subject || null }`. Additive; themed decks pass through `mergeConvoSets` untouched, so `subject` survives reloads. No other reducer change (`ES_FLASH_ADD_CARD` already dedups).

## Credit rule

Both create and generate-more are AI calls only on the explicit tap. Generated cards persist as normal deck cards, reused for free. No auto-generation.

## UI

- A glass-card "mazo nuevo por tema" near the top of the editor body (above the add-card box): a subject text input, a size `<select>` (5/10/15/20, default 10), and a "crear mazo" button (primary; disabled while aiBusy or subject empty).
- "generar 5 más" button in the deck header row (near the card count), rendered only when `deck.subject` is set; disabled while aiBusy.

## Out of scope

Items 1-3 (done). Editing built-in decks. Changing how decks render/sync (existing esFlash -> Veo sync already carries new decks). Regenerating a whole deck (only additive "5 more").

## Verify

checkbabel (React-side, no re-bake). Browser check with a STUBBED fetch (no real spend): no-key -> flash, 0 fetches; create with a canned `{name,cards}` -> new deck appears selected with the right cards; "generar 5 más" only shows on the subject deck and appends without dupes; each action is exactly one fetch. BUILD bump. Clean any test data + key from the localhost origin afterward.
