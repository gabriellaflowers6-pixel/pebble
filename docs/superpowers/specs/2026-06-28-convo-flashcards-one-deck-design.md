# Convo flashcards: one rolling deck

**Date:** 2026-06-28
**App:** Veo & Digo Spanish app embedded in Pebble (`pebble-app.html` React side + `veo-y-digo-source.html` Veo iframe)

## Problem

Every Spanish conversation creates its own flashcard set. Cards you save during a chat
land in a per-session deck (`Conversación · <date> <time>`), and each one shows as a
separate deck button in the Veo app's Tarjetas section. Gabby wants all saved
conversation cards in a single deck, not one per chat.

## Decision

One rolling deck. Every card saved from any conversation goes into a single permanent
deck. Existing per-conversation decks are merged into it (deduped). No on-demand
"combine" UI — the merge is automatic.

## Current behavior (reference)

- `saveSpanishCard(kind, es, en)` in `pebble-app.html` (~line 2923):
  - First save in a chat lazily creates `esSessionRef.current = { id: 'es'+Date.now(), label: 'Conversación · <date> <time>', date, created:false }`.
  - Dispatches `ES_FLASH_NEW_SET` once, then `ES_FLASH_ADD_CARD` per card.
  - `esCardsRef.current` is a per-session dedup cache driving the toast count.
- Reducer (`pebble-app.html` ~1347):
  - `ES_FLASH_NEW_SET` appends `{ id, label, date, cards: [] }` to `state.esFlash.sets` (skips if id exists).
  - `ES_FLASH_ADD_CARD` appends a card to a set, deduping by `kind + ':' + es.toLowerCase()` within that set.
- `state.esFlash.sets` is persisted in Pebble and postMessaged to the Veo iframe as
  `{ type: 'esFlashSets', sets }` (~line 5780).
- Veo side: `applyEsFlashSets(sets)` in `veo-y-digo-source.html` (~line 5228) registers
  each set as `themeDecks[label]` and rebuilds the Tarjetas deck buttons. Read-only;
  renders whatever it receives.

## New behavior

### 1. Single fixed deck
Define a constant deck identity:
- `id: 'convo-all'`
- `label: 'Conversación'`

`saveSpanishCard` no longer creates a per-session set. It ensures the `convo-all` deck
exists (dispatch `ES_FLASH_NEW_SET` with the fixed id/label if `state.esFlash.sets` has
no set with id `convo-all`), then dispatches `ES_FLASH_ADD_CARD` with `setId: 'convo-all'`.

The lazy `esSessionRef` session object is removed (or repurposed to just hold the fixed
id). No timestamped labels.

### 2. Global dedup
Because there is now one set, the reducer's existing within-set dedup
(`kind:es.toLowerCase()`) becomes global across all conversations. A word saved last week
won't re-add this week; the user sees the existing "ya guardada" toast. This is the
intended rolling-deck behavior and needs no reducer change.

### 3. Migration of existing decks
On load (one-time), fold every existing set's cards into the `convo-all` deck, deduped by
`kind:es.toLowerCase()`, then drop all other sets.

- Add reducer action `ES_FLASH_MERGE_ALL`:
  - Collect all cards from every set in `state.esFlash.sets`.
  - Dedup by `kind + ':' + es.toLowerCase()` (first occurrence wins).
  - Result state: `esFlash.sets = [{ id: 'convo-all', label: 'Conversación', date: <today or earliest>, cards: <deduped> }]`.
  - Idempotent: if the only set is already `convo-all`, return state unchanged (no churn,
    safe to dispatch on every mount).
- Dispatch it once when the Spanish component mounts (a `useEffect` with `[]` deps, or
  guarded by a check that more than one set exists / a non-`convo-all` set exists).

Cards have no per-set provenance to preserve, so a flat dedup is lossless for the user's
purposes (front/back study cards).

### 4. Veo side: no change
`applyEsFlashSets` already renders whatever sets it receives. After this change it
receives a single set and renders one "Conversación" deck button. The existing
`postSets` effect (`[data.esFlash]`) re-pushes automatically after the merge.

### 5. Toast counter
`setFlashToast('palabra guardada ✓ (N)')` currently uses `esCardsRef.current.length`
(this-session count). Change N to the `convo-all` deck's total card count after the add,
so it reflects the real deck size. Read it from the post-dispatch state (or compute from
the known deck length + 1 on a fresh add).

## Out of scope
- No on-demand multi-select "combine decks" UI.
- No renaming the deck from the UI.
- No change to how cards are studied/flipped in Tarjetas.
- No change to story/theme decks — only the conversation-sourced set is affected.

## Verification
Per the project's headless check (see `NEXT-SESSION.md`): re-bake `veo-y-digo-source.html`
into `window.VEO_DIGO_B64` only if the Veo source changed (it does NOT for this task —
all edits are React-side in `pebble-app.html`). Confirm in a 375px iframe preview that:
1. Saving two words across two separate conversations both land in one "Conversación" deck.
2. Re-saving an already-saved word shows "ya guardada" and does not duplicate.
3. On first load after the change, pre-existing per-convo decks have collapsed into one
   "Conversación" deck with the union of their cards.
