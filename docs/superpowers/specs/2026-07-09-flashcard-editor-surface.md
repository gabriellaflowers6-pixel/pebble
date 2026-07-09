# Surface the flashcard editor from the study screen (item 2)

Date: 2026-07-09. Approved by Gabby ("lets do it"). Part of the flashcard batch (item 2 of 4).

## Problem

The flashcard editor (`FlashEditor` in pebble-app.html) already lists every card with Spanish + English, and supports add and delete. But it is only reachable from `Constructor -> Tarjetas tab -> Administrar tarjetas`, nowhere near the flashcard study screen. Gabby: "i dont see it." So it is a discoverability problem, not a missing feature.

## Change

Add an "✏️ editar lista" button on the flashcard study screen (`flashHome` in the Veo source), directly under the deck buttons (`#fcThemes`). Tapping it opens the existing editor, pre-selected to the deck currently being studied.

- The button shows ONLY for editable decks: the ones tracked in `window.__esFlashNames` (Conversación / lesson / themed decks that live in `data.esFlash`). Built-in picture decks (Naturaleza etc.) and story decks are not editable word lists, so the button stays hidden for them.
- No new editor is built. It reuses `FlashEditor`, so items 3 and 4 (English-only AI add, create-deck-by-subject) will layer onto the same component.

## Wiring

1. Veo source (`veo-y-digo-source.html`):
   - Add `<button id="fcEditList" onclick="fcOpenEditList()">✏️ editar lista</button>` (hidden by default) under `#fcThemes` in the `flashHome` section. Style to match (small olive outline).
   - `function fcOpenEditList(){ window.parent.postMessage({type:'openFlashEditor', deckLabel: fcDeckName}, '*'); }`.
   - In `loadDeck(kind,key)`, after `fcDeckName` is set and before `renderCard()`, toggle the button: `display = (window.__esFlashNames||[]).indexOf(fcDeckName) >= 0 ? 'inline-block' : 'none'`.
   - Re-bake into pebble-app.html.

2. Parent (`pebble-app.html`):
   - The `openFlashEditor` message handler already sets `flashEditorOpen`. Extend it to also capture `d.deckLabel` into a new `flashEditorDeckLabel` state and pass it to `FlashEditor` as a `deckLabel` prop.
   - `FlashEditor` gains a `deckLabel` prop and a `useEffect` (placed before the `if (!open) return null` early return, to respect hook rules): when `open && deckLabel`, find the `esFlash` set whose `label === deckLabel` and `setDeckId(s.id)`. No match (built-in deck) falls back to the current default (convo-all).

## Out of scope

Items 3 and 4. Changing the editor's contents/behavior. Editing built-in picture/story decks. No BUILD-visible copy beyond the one button.

## Verify

Syntax gates (inline node parse + checkbabel), rebake round-trip, and a browser check: on `flashHome`, the button is hidden for Naturaleza, visible for Conversación; tapping posts `openFlashEditor` with the right `deckLabel`; in the full app the editor opens pre-selected to that deck. BUILD bump.
