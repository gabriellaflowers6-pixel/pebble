# Bidirectional AI translate in the add box (item 3)

Date: 2026-07-09. Approved by Gabby ("sounds great"). Flashcard batch item 3 of 4. Builds into the existing `FlashEditor` add box in pebble-app.html.

## What

Add a "traducir" button beside the existing "añadir" button in the FlashEditor add card. The user types in either box (español or english); tapping traducir uses Claude to fill the OTHER box. The translation lands in the normal editable input so the user reviews/tweaks it, then taps añadir to save (review step, per Gabby's choice).

## Behavior

- Direction:
  - if the english box has text -> translate english -> spanish, fill the español box.
  - else if the español box has text -> translate español -> english, fill the english box.
  - else (both empty) -> flash "escribe algo primero", no call.
  - (If both are filled, english drives: translate english -> spanish.)
- Needs `data.settings.apiKey`; if missing, flash "agrega tu clave en ajustes", no call.
- Uses the existing `aiCall(prompt, maxTok)` helper (claude-sonnet-4-6, device key, browser-direct headers). max_tokens ~200.
- Prompt returns ONLY the translation; strip wrapping quotes/whitespace before filling.
- Loading: reuse the `aiBusy` state ('translate'); button shows "…" and is disabled while busy; also disabled when both boxes are empty.
- Error: try/catch/finally; flash "no pude traducir" on failure; always clear aiBusy.

## Credit rule

One AI call per explicit traducir tap. No auto-translate, no caching (one-off translations). Consistent with the app's credit discipline (explicit taps only).

## UI

Replace the single "añadir" button row with a flex row: [↔ traducir] (olive outline) + [añadir] (primary, unchanged, still disabled until the español box has text). añadir keeps its existing behavior; after an english->spanish translate, español is filled so añadir enables.

## Out of scope

Items 2 (done) and 4. The AI suggest/organize buttons. Any change to how cards render or persist.

## Verify

Syntax gate (checkbabel), rebake not needed (React-side only, no Veo change). Browser check with a STUBBED fetch (no real API spend): type English -> traducir -> español fills; clear, type Spanish -> traducir -> english fills; empty -> flash, no fetch; no-key -> flash, no fetch. BUILD bump.
