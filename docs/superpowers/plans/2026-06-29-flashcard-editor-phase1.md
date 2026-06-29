# Flashcard Editor — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Add an in-app editor for the Spanish flashcard deck — list, edit, delete, manual add (deduped), and add from recent-chat-word suggestions — reachable from the Veo Tarjetas section.

**Architecture:** All card data lives in the main app's `data.esFlash` reducer (`pebble-app.html`). Add reducer actions for delete/edit/move/push-recent, capture recent chat words into a buffer, build a `FlashEditor` React panel in the main app, and add a "Manage cards" button in the Veo iframe (`veo-y-digo-source.html`) that postMessages the parent to open the panel. The existing one-way `esFlashSets` sync re-pushes the deck to Tarjetas after edits.

**Tech Stack:** React 18 via `@babel/standalone@7.23.10` (pinned), single-file HTML. No bundler, no test runner.

## Global Constraints

- `@babel/standalone` is PINNED to `7.23.10` — never change it.
- Files are huge (`pebble-app.html` ~15MB, `veo-y-digo-source.html` ~11MB with base64 blobs). NEVER read them whole; edit via targeted python string-replace; never `Read`/`Edit` the whole file.
- After editing `veo-y-digo-source.html`, RE-BAKE it into `window.VEO_DIGO_B64` in `pebble-app.html` (base64, regex-replace the assignment), then verify the baked base64 round-trips to the source.
- Card shape: `{ kind: 'word' | 'frase', es, en }`. Dedup key: `convoCardKey(card)` (already defined ~line 1134).
- Deck: `CONVO_DECK_ID = 'convo-all'`, label `CONVO_DECK_LABEL = 'Conversación'`.
- No AI in Phase 1.
- Verification = `python3 -m http.server <port>` in the project dir + load `http://localhost:<port>/pebble-app.html` in Chrome, then assert via `javascript_tool`. Programmatic `.focus()` does NOT fire focus events in an unfocused automation tab — dispatch synthetic `FocusEvent`/`InputEvent` with `{bubbles:true}` instead.
- Bump `PEBBLE_BUILD` and update `PEBBLE_BUILD_NOTE` when the feature is user-visible.
- No em dashes / no AI-writing patterns in any user-facing copy.

---

### Task 1: Reducer actions + recent buffer

**Files:**
- Modify: `pebble-app.html` — `DEFAULT_DATA.esFlash` (~line 1111) to include `recent: []`; the `dataReducer` switch (add cases near the existing `ES_FLASH_*` cases ~1361-1380).

**Interfaces:**
- Produces actions consumed by Tasks 2-4:
  - `ES_FLASH_DELETE_CARD { setId, cardKey }`
  - `ES_FLASH_EDIT_CARD { setId, cardKey, es, en }`
  - `ES_FLASH_MOVE_CARDS { fromSetId, toSetId, cardKeys }`
  - `ES_FLASH_PUSH_RECENT { items: [{kind,es,en}] }`
- Relies on existing `convoCardKey(card)` in scope.

- [ ] **Step 1: Add `recent: []` to `DEFAULT_DATA.esFlash`.** Find the `esFlash:` default and ensure it reads `esFlash: { sets: [...], recent: [] }` (preserve existing keys).

- [ ] **Step 2: Add the four reducer cases** next to the existing `ES_FLASH_*` cases:

```js
case 'ES_FLASH_DELETE_CARD': {
  const sets = state.esFlash.sets.map(set =>
    set.id === action.setId
      ? { ...set, cards: set.cards.filter(c => convoCardKey(c) !== action.cardKey) }
      : set);
  return { ...state, esFlash: { ...state.esFlash, sets } };
}
case 'ES_FLASH_EDIT_CARD': {
  const sets = state.esFlash.sets.map(set => {
    if (set.id !== action.setId) return set;
    const cur = set.cards.find(c => convoCardKey(c) === action.cardKey);
    if (!cur) return set;
    const next = { ...cur, es: (action.es || '').trim(), en: (action.en || '').trim() };
    const nextKey = convoCardKey(next);
    const collides = set.cards.some(c => convoCardKey(c) !== action.cardKey && convoCardKey(c) === nextKey);
    if (!next.es || collides) return set; // no-op on empty or duplicate
    return { ...set, cards: set.cards.map(c => convoCardKey(c) === action.cardKey ? next : c) };
  });
  return { ...state, esFlash: { ...state.esFlash, sets } };
}
case 'ES_FLASH_MOVE_CARDS': {
  const moving = [];
  let sets = state.esFlash.sets.map(set => {
    if (set.id !== action.fromSetId) return set;
    const keep = [], take = [];
    set.cards.forEach(c => (action.cardKeys.indexOf(convoCardKey(c)) >= 0 ? take : keep).push(c));
    moving.push.apply(moving, take);
    return { ...set, cards: keep };
  });
  sets = sets.map(set => set.id === action.toSetId
    ? { ...set, cards: [...set.cards, ...moving.filter(m => !set.cards.some(c => convoCardKey(c) === convoCardKey(m)))] }
    : set);
  return { ...state, esFlash: { ...state.esFlash, sets } };
}
case 'ES_FLASH_PUSH_RECENT': {
  const cur = state.esFlash.recent || [];
  const seen = {}; cur.forEach(c => seen[convoCardKey(c)] = 1);
  const add = (action.items || []).filter(it => it && it.es && !seen[convoCardKey(it)]);
  const recent = [...add, ...cur].slice(0, 50);
  return { ...state, esFlash: { ...state.esFlash, recent } };
}
```

- [ ] **Step 3: Verify (browser).** Serve + load. In `javascript_tool`, confirm `window` mounts with no errors and (if a debug hook is exposed) the reducer is reachable. Minimum gate: app boots clean (`#root` has children, no thrown errors), and `data.esFlash.recent` exists (inspect via the React tree or a temporary `window.__d = data` hook if needed).

- [ ] **Step 4: Commit** `pebble-app.html` — "feat(es-flash): add delete/edit/move/push-recent reducer actions + recent buffer".

---

### Task 2: Capture recent chat words into the buffer

**Files:**
- Modify: `pebble-app.html` — wherever a Spanish chat reply is parsed into `{ sentences: [{ es, en, words:[{w,t}] }] }` (the `sendSpanish` / Spanish reply handler, near the other Spanish AI calls ~2799/2917). Also where words are saved (`saveSpanishCard` ~2946) is the model for the card shape.

**Interfaces:**
- Consumes: `ES_FLASH_PUSH_RECENT` from Task 1.
- Produces: a populated `data.esFlash.recent` for Task 3's "from your chats" section.

- [ ] **Step 1:** When a Spanish reply parses successfully, build `items` from each sentence's words and the sentence itself: `{ kind:'word', es:w.w, en:w.t }` for words and `{ kind:'frase', es:sentence.es, en:sentence.en }` for sentences, then `dispatch({ type:'ES_FLASH_PUSH_RECENT', items })`. Guard against missing fields.

- [ ] **Step 2: Verify (browser).** With a stubbed parsed reply (call the parse path or dispatch `ES_FLASH_PUSH_RECENT` directly via a temporary hook), confirm `data.esFlash.recent` fills and caps at 50, deduped by `convoCardKey`.

- [ ] **Step 3: Commit** — "feat(es-flash): buffer recent Spanish chat words for suggestions".

---

### Task 3: FlashEditor panel (list / edit / delete / manual add / from-chats)

**Files:**
- Modify: `pebble-app.html` — add a `FlashEditor` component before `App()` (near other page components); add `flashEditorOpen` state + render `<FlashEditor open={flashEditorOpen} onClose={...} />` inside the app shell (like `SettingsPanel`); add a listener for the `openFlashEditor` postMessage (alongside the existing `openSpanishChat` handler ~2963) that sets `flashEditorOpen = true`.

**Interfaces:**
- Consumes: `ES_FLASH_DELETE_CARD`, `ES_FLASH_EDIT_CARD`, `ES_FLASH_PUSH_RECENT`, `data.esFlash`, `convoCardKey`, `CONVO_DECK_ID`/`CONVO_DECK_LABEL`, `saveSpanishCard` pattern for adds.
- Produces: a working editor opened via `flashEditorOpen`.

- [ ] **Step 1:** Add the component. Core logic (style to match `SettingsPanel`'s glass-card look):

```jsx
function FlashEditor({ open, onClose }) {
  const { data, dispatch } = useContext(DataCtx);
  const [deckId, setDeckId] = useState(CONVO_DECK_ID);
  const [es, setEs] = useState(''); const [en, setEn] = useState('');
  const [toast, setToast] = useState('');
  if (!open) return null;
  const sets = (data.esFlash && data.esFlash.sets) || [];
  const deck = sets.find(s => s.id === deckId) || sets.find(s => s.id === CONVO_DECK_ID) || { id: CONVO_DECK_ID, label: CONVO_DECK_LABEL, cards: [] };
  const cards = deck.cards || [];
  const recent = (data.esFlash && data.esFlash.recent) || [];
  const inDeck = (c) => cards.some(x => convoCardKey(x) === convoCardKey(c));
  const flash = (m) => { setToast(m); setTimeout(() => setToast(''), 1600); };
  const add = () => {
    const card = { kind: 'word', es: es.trim(), en: en.trim() };
    if (!card.es) return;
    if (inDeck(card)) { flash('ya guardada'); return; }
    dispatch({ type: 'ES_FLASH_NEW_SET', id: deck.id, label: deck.label, date: new Date().toISOString().slice(0,10) });
    dispatch({ type: 'ES_FLASH_ADD_CARD', setId: deck.id, card });
    setEs(''); setEn(''); flash('añadida ✓');
  };
  const addSuggest = (c) => {
    if (inDeck(c)) { flash('ya guardada'); return; }
    dispatch({ type: 'ES_FLASH_ADD_CARD', setId: deck.id, card: { kind: c.kind || 'word', es: c.es, en: c.en } });
    flash('añadida ✓');
  };
  const suggestions = recent.filter(c => !inDeck(c)).slice(0, 20);
  return (
    <div className="absolute inset-0 z-50 flex flex-col" style={{ background: 'var(--bg)' }}>
      {/* header: title "tarjetas" + card count + close button (mirror SettingsPanel header) */}
      {/* deck switcher dropdown when sets.length > 1 */}
      {/* add form: two inputs bound to es/en + Add button calling add() */}
      {/* suggestions row: suggestions.map(c => <button onClick={()=>addSuggest(c)}>{c.es}</button>) */}
      {/* list: cards.map(c => row with es/en, edit (dispatch ES_FLASH_EDIT_CARD), delete (dispatch ES_FLASH_DELETE_CARD with convoCardKey(c))) */}
      {/* toast */}
    </div>
  );
}
```

Flesh out the JSX markup (header, deck switcher, inputs, suggestions, list rows, toast) using the same class names and inline-style patterns as `SettingsPanel` (lines ~5314+). Delete button dispatches `{ type:'ES_FLASH_DELETE_CARD', setId: deck.id, cardKey: convoCardKey(c) }`. Edit uses inline fields then `{ type:'ES_FLASH_EDIT_CARD', setId: deck.id, cardKey: convoCardKey(c), es, en }`.

- [ ] **Step 2:** Add `const [flashEditorOpen, setFlashEditorOpen] = useState(false)` in the component that owns the chat/postMessage handler; render `<FlashEditor open={flashEditorOpen} onClose={() => setFlashEditorOpen(false)} />`; in the `message` handler that checks `e.data.type === 'openSpanishChat'`, add a branch: `if (e.data.type === 'openFlashEditor') setFlashEditorOpen(true)`.

- [ ] **Step 3: Verify (browser).** Open the editor by dispatching the `openFlashEditor` message (`window.postMessage({type:'openFlashEditor'},'*')`) or toggling state via a temporary hook. Assert: list renders the deck cards; Add with a new word inserts it; Add with an existing word shows "ya guardada" and does not duplicate; delete removes a card; edit updates text; a suggestion chip adds and disappears from suggestions.

- [ ] **Step 4: Commit** — "feat(es-flash): FlashEditor panel (list/edit/delete/manual add/suggestions)".

---

### Task 4: Veo "Manage cards" button + bridge

**Files:**
- Modify: `veo-y-digo-source.html` — in the Tarjetas section UI (~line 471 / the cards panel ~724), add a button `Administrar tarjetas` with `onclick="manageFlashCards()"`; define `function manageFlashCards(){ try { window.parent.postMessage({ type:'openFlashEditor' }, '*'); } catch(e){} }`.
- Modify: `pebble-app.html` — re-bake `window.VEO_DIGO_B64` from the edited source.

**Interfaces:**
- Consumes: the `openFlashEditor` listener from Task 3.

- [ ] **Step 1:** Add the button + `manageFlashCards()` to the Veo source (python string-replace; verify the function and button exist, source still internally consistent).

- [ ] **Step 2:** Re-bake: base64-encode the source, regex-replace `window.VEO_DIGO_B64="[^"]*"` in `pebble-app.html`, assert exactly one replacement and that the baked base64 round-trips to the current source bytes.

- [ ] **Step 3: Verify (browser).** Load the app, open the Español page (Veo iframe), confirm the "Administrar tarjetas" button appears in Tarjetas and clicking it opens the FlashEditor in the main app (the iframe posts `openFlashEditor`, the parent opens the panel).

- [ ] **Step 4: Commit** — "feat(es-flash): Veo Tarjetas 'Manage cards' button opens the editor + re-bake".

---

### Task 5: Confirm Tarjetas reflects edits

**Files:**
- Inspect: `pebble-app.html` — the effect that posts `{ type:'esFlashSets', sets }` (~5817). Confirm its dependency array fires on `data.esFlash` changes; if it only depends on `apiKey`/mount, extend it to also run when `data.esFlash` changes.

- [ ] **Step 1:** Verify the post effect re-runs on `esFlash` change (read the effect deps). If not, add `data.esFlash` (or `data`) to its deps so adds/edits/deletes re-post to the iframe.

- [ ] **Step 2: Verify (browser).** After an edit in the FlashEditor, assert the iframe received a fresh `esFlashSets` (spy on `postMessage` or check the Veo side registered the updated deck).

- [ ] **Step 3: Commit** — "fix(es-flash): re-post deck to Tarjetas on every esFlash change" (only if a change was needed).

---

## Phase 1 done = editor reachable from Tarjetas; list/edit/delete/manual-add(deduped)/from-chats-suggestions all work; Tarjetas reflects changes. Phase 2 (AI suggest + AI organize/split into themed decks) is a separate plan.
