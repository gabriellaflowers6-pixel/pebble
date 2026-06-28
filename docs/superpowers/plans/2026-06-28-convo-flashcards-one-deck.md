# Convo Flashcards: One Rolling Deck — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collapse per-conversation Spanish flashcard sets into a single permanent "Conversación" deck, and merge existing sets into it on load.

**Architecture:** All edits are React-side in `pebble-app.html` (the reducer + the Spanish chat component). A pure helper `mergeConvoSets()` does the dedup; a new reducer action `ES_FLASH_MERGE_ALL` applies it; `saveSpanishCard` writes to a fixed deck id; a reactive effect migrates legacy multi-set state. The Veo iframe (`veo-y-digo-source.html`) is unchanged — it renders whatever sets it receives — so **no base64 re-bake is needed.**

**Tech Stack:** Single-file React (via `@babel/standalone` 7.23.10, pinned) in `pebble-app.html`. No build, no test runner. Verification = a standalone Node logic check for the pure helper + a headless Chrome "app loads with zero JS errors" smoke + manual phone-style checks.

## Global Constraints

- **Editable source is `pebble-app.html` directly.** It is the app (not generated). Do NOT edit the base64 `window.VEO_DIGO_B64`.
- **Do NOT touch `veo-y-digo-source.html` or re-bake.** This task is entirely React-side.
- `@babel/standalone` stays pinned at `7.23.10` — do not change the CDN tag.
- Deck identity is fixed: `id = 'convo-all'`, `label = 'Conversación'` (with the accented ó).
- Card dedup key everywhere: `(kind || 'word') + ':' + es.toLowerCase()`.
- No em dashes / no emojis in any code comments or copy (project rule). The save toast keeps its existing `✓` which is already in the codebase and is fine to retain.
- Never push or deploy without asking Gabby. Commit locally and liberally.

---

### Task 1: Pure merge helper + reducer action

**Files:**
- Modify: `pebble-app.html` — insert constants + helper immediately before `function dataReducer(state, action) {` (currently line 1133); add a new `case` inside the reducer's switch (near the existing `ES_FLASH_ADD_CARD` case, ~line 1352).
- Test: `/private/tmp/claude-502/-Users-gabriellakalvaitis-flowers/0e28c8f1-e789-4d0e-b991-b420567a2c8d/scratchpad/merge-test.js` (standalone Node check of the helper logic)

**Interfaces:**
- Produces (used by Tasks 2 and 3):
  - `const CONVO_DECK_ID = 'convo-all'`
  - `const CONVO_DECK_LABEL = 'Conversación'`
  - `convoCardKey(card) -> string` — `(card.kind || 'word') + ':' + (card.es || '').toLowerCase()`
  - `mergeConvoSets(sets) -> [{ id, label, date, cards }]` — one set, cards deduped by `convoCardKey`, first occurrence wins.
  - Reducer action `{ type: 'ES_FLASH_MERGE_ALL' }` — idempotent.

- [ ] **Step 1: Write the failing logic test**

Create `…/scratchpad/merge-test.js` (paste the helper under test so it runs in plain Node):

```js
const CONVO_DECK_ID = 'convo-all';
const CONVO_DECK_LABEL = 'Conversación';
const convoCardKey = (c) => (c.kind || 'word') + ':' + (c.es || '').toLowerCase();
function mergeConvoSets(sets) {
  const cards = []; const seen = new Set();
  (sets || []).forEach(s => (s.cards || []).forEach(c => {
    const k = convoCardKey(c);
    if (seen.has(k)) return;
    seen.add(k); cards.push(c);
  }));
  return [{ id: CONVO_DECK_ID, label: CONVO_DECK_LABEL, date: '2026-06-28', cards }];
}

// --- assertions ---
const sets = [
  { id: 'es1', label: 'Convo A', cards: [ {kind:'word', es:'Hola', en:'hi'}, {kind:'phrase', es:'Buenos días', en:'good morning'} ] },
  { id: 'es2', label: 'Convo B', cards: [ {kind:'word', es:'hola', en:'hi again'}, {kind:'word', es:'gato', en:'cat'} ] },
];
const out = mergeConvoSets(sets);
const a = (cond, msg) => { if (!cond) { console.error('FAIL: ' + msg); process.exit(1); } };
a(out.length === 1, 'collapses to one set');
a(out[0].id === 'convo-all', 'fixed id');
a(out[0].label === 'Conversación', 'fixed label');
a(out[0].cards.length === 3, 'dedup across sets (Hola/hola collapse), got ' + out[0].cards.length);
a(out[0].cards[0].es === 'Hola', 'first occurrence wins (keeps Hola, en=hi)');
a(out[0].cards[0].en === 'hi', 'first occurrence keeps original en');
a(mergeConvoSets([]).length === 1 && mergeConvoSets([]) [0].cards.length === 0, 'empty input yields empty deck');
console.log('ALL PASS');
```

- [ ] **Step 2: Run it to confirm the asserts are exercised**

Run: `node "/private/tmp/claude-502/-Users-gabriellakalvaitis-flowers/0e28c8f1-e789-4d0e-b991-b420567a2c8d/scratchpad/merge-test.js"`
Expected: `ALL PASS` (this validates the helper you are about to paste into the app is correct).

- [ ] **Step 3: Add the constants + helper to `pebble-app.html`**

Insert immediately above `function dataReducer(state, action) {` (line ~1133):

```js
const CONVO_DECK_ID = 'convo-all';
const CONVO_DECK_LABEL = 'Conversación';
const convoCardKey = (c) => (c.kind || 'word') + ':' + (c.es || '').toLowerCase();
function mergeConvoSets(sets) {
  const cards = []; const seen = new Set();
  (sets || []).forEach(s => (s.cards || []).forEach(c => {
    const k = convoCardKey(c);
    if (seen.has(k)) return;
    seen.add(k); cards.push(c);
  }));
  return [{ id: CONVO_DECK_ID, label: CONVO_DECK_LABEL, date: new Date().toISOString().slice(0, 10), cards }];
}
```

- [ ] **Step 4: Add the reducer case**

Inside `dataReducer`'s switch, directly after the closing `}` of the `case 'ES_FLASH_ADD_CARD':` block (~line 1360), add:

```js
    case 'ES_FLASH_MERGE_ALL': {
      const sets = (state.esFlash?.sets) || [];
      // idempotent: nothing to do if empty or already a single convo-all deck
      if (sets.length === 0) return state;
      if (sets.length === 1 && sets[0].id === CONVO_DECK_ID) return state;
      return { ...state, esFlash: { sets: mergeConvoSets(sets) } };
    }
```

- [ ] **Step 5: Verify the app still loads with zero JS errors (headless smoke)**

```bash
T="/private/tmp/claude-502/-Users-gabriellakalvaitis-flowers/0e28c8f1-e789-4d0e-b991-b420567a2c8d/scratchpad/smoke"
mkdir -p "$T"
# inject a JS-error counter right after <head>, then dump the DOM
perl -0pe 's/<head>/<head><script>window.__pe=[];window.addEventListener("error",function(e){if(e\&\&e.error)window.__pe.push(String(e.error))});<\/script>/' "$HOME/Desktop/my projects/pebble/pebble-app.html" > "$T/pebble-app.html"
printf '%s' '<script>setTimeout(function(){document.title="PEBBLECHECK ERRS("+window.__pe.length+") "+window.__pe.join("|")},10000)</script>' >> "$T/pebble-app.html"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --virtual-time-budget=13000 --dump-dom "file://$T/pebble-app.html" 2>/dev/null | grep -o 'PEBBLECHECK ERRS([0-9]*)[^<"]*' | head -1
```
Expected: `PEBBLECHECK ERRS(0)` (no JS exceptions; the new top-level code parses and runs).

- [ ] **Step 6: Commit**

```bash
cd "$HOME/Desktop/my projects/pebble"
git add pebble-app.html
git commit -m "feat(es-flash): add mergeConvoSets helper + ES_FLASH_MERGE_ALL reducer action"
```

---

### Task 2: Save into the single rolling deck

**Files:**
- Modify: `pebble-app.html` — `saveSpanishCard` (~line 2923) and `enterSpanish` (~line 2888, the per-session reset at lines 2892-2894).

**Interfaces:**
- Consumes (from Task 1): `CONVO_DECK_ID`, `CONVO_DECK_LABEL`, `convoCardKey`.
- Relies on existing reducer actions: `ES_FLASH_NEW_SET` (idempotent on id) and `ES_FLASH_ADD_CARD` (dedups by `kind:es` within the set).

- [ ] **Step 1: Replace `saveSpanishCard` body**

Replace the whole function (currently lines ~2923-2938) with:

```js
  // Save a tapped word / sentence into the single rolling Conversación deck.
  const saveSpanishCard = (kind, es, en) => {
    const e = (es || '').trim(); if (!e) return;
    const card = { kind, es: e, en: (en || '').trim() };
    const key = convoCardKey(card);
    if (esCardsRef.current.some(c => convoCardKey(c) === key)) {
      setFlashToast('ya guardada');
    } else {
      esCardsRef.current.push(card);
      // ensure the one rolling deck exists (NEW_SET is a no-op if it already does), then add the card
      dispatch({ type: 'ES_FLASH_NEW_SET', id: CONVO_DECK_ID, label: CONVO_DECK_LABEL, date: new Date().toISOString().slice(0, 10) });
      dispatch({ type: 'ES_FLASH_ADD_CARD', setId: CONVO_DECK_ID, card });
      setFlashToast((kind === 'word' ? 'palabra' : 'frase') + ' guardada ✓ (' + esCardsRef.current.length + ')');
    }
    setTimeout(() => setFlashToast(''), 1800);
  };
```

(`esCardsRef.current.length` now reflects the whole deck because Task 2 Step 2 seeds it from the persisted deck. `esSessionRef` is no longer referenced here.)

- [ ] **Step 2: Seed the dedup cache from the deck in `enterSpanish`**

In `enterSpanish`, replace the two lines that create a per-session set and clear the cache (currently lines ~2892-2894):

```js
    // fresh chat = new session = new flashcard set (created lazily on first save)
    esSessionRef.current = { id: 'es' + Date.now(), label: 'Conversación · ' + new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), date: new Date().toISOString().slice(0, 10), created: false };
    esCardsRef.current = [];
```

with:

```js
    // rolling deck: seed the dedup cache from the persisted Conversación deck so saves dedupe across all sessions
    const convoDeck = (data.esFlash?.sets || []).find(s => s.id === CONVO_DECK_ID);
    esCardsRef.current = convoDeck ? convoDeck.cards.slice() : [];
```

- [ ] **Step 3: Run the headless smoke again**

Run the exact block from Task 1 Step 5.
Expected: `PEBBLECHECK ERRS(0)`.

- [ ] **Step 4: Manual behavior check (record result in the commit / WORKLOG)**

Open the app, enter Conversación, save a word. Re-tap the same word: toast shows `ya guardada` and the count does not increase. This confirms the fixed-deck write path and the seeded cache. (Full cross-session and Tarjetas-display verification happens after Task 3.)

- [ ] **Step 5: Commit**

```bash
cd "$HOME/Desktop/my projects/pebble"
git add pebble-app.html
git commit -m "feat(es-flash): saveSpanishCard writes to the single Conversación deck; seed dedup cache from it"
```

---

### Task 3: Migrate existing per-conversation decks on load

**Files:**
- Modify: `pebble-app.html` — add one `useEffect` inside the Spanish chat component (the component that declares `esCardsRef`/`esSessionRef` at lines ~2608-2609). Place it next to the other top-level effects in that component, e.g. just after the `useEffect` that registers the `openSpanishChat` message listener (~line 2945).

**Interfaces:**
- Consumes (from Task 1): `CONVO_DECK_ID`, reducer action `ES_FLASH_MERGE_ALL`.
- Consumes existing: `data` (state) and `dispatch` from `useContext(DataCtx)`.

- [ ] **Step 1: Add the reactive migration effect**

Insert:

```js
  // One-time migration: fold any legacy per-conversation decks into the single rolling deck.
  // Runs reactively so it also fires after async LOAD_DATA brings stored sets in. Idempotent in the reducer.
  useEffect(() => {
    const sets = data.esFlash?.sets || [];
    const needsMerge = sets.length > 1 || sets.some(s => s.id !== CONVO_DECK_ID);
    if (needsMerge) dispatch({ type: 'ES_FLASH_MERGE_ALL' });
  }, [data.esFlash]);
```

Rationale: after a merge, `sets` becomes `[{ id: 'convo-all', ... }]`, so `needsMerge` is `false` and the reducer's idempotency guard returns the same state object — no re-render loop. When the app first loads stored data with multiple legacy sets, this fires once and collapses them. The existing `postSets` effect (depends on `data.esFlash`) then re-pushes the single deck to the Veo iframe automatically.

- [ ] **Step 2: Run the headless smoke**

Run the exact block from Task 1 Step 5.
Expected: `PEBBLECHECK ERRS(0)`.

- [ ] **Step 3: Headless migration assertion (seeded legacy state)**

This proves the migration collapses real multi-set data. It injects two legacy sets into Pebble's stored state before the app boots, then checks the deck count after load.

```bash
T="/private/tmp/claude-502/-Users-gabriellakalvaitis-flowers/0e28c8f1-e789-4d0e-b991-b420567a2c8d/scratchpad/migrate"
mkdir -p "$T"
# Seed localStorage with two legacy convo decks, capture the post-merge deck count into the title.
perl -0pe 's/<head>/<head><script>
try{var d=JSON.parse(localStorage.getItem("pebble_data")||"{}");
d.esFlash={sets:[
 {id:"es100",label:"Convo A",date:"2026-06-26",cards:[{kind:"word",es:"Hola",en:"hi"},{kind:"phrase",es:"Buenos dias",en:"morning"}]},
 {id:"es200",label:"Convo B",date:"2026-06-27",cards:[{kind:"word",es:"hola",en:"dup"},{kind:"word",es:"gato",en:"cat"}]}
]};
localStorage.setItem("pebble_data",JSON.stringify(d));}catch(e){}
<\/script>/' "$HOME/Desktop/my projects/pebble/pebble-app.html" > "$T/pebble-app.html"
printf '%s' '<script>setTimeout(function(){try{var d=JSON.parse(localStorage.getItem("pebble_data")||"{}");var s=(d.esFlash&&d.esFlash.sets)||[];document.title="MIGCHECK SETS("+s.length+") CARDS("+((s[0]&&s[0].cards.length)||0)+") ID("+((s[0]&&s[0].id)||"-")+")"}catch(e){document.title="MIGCHECK ERR"}},11000)</script>' >> "$T/pebble-app.html"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --virtual-time-budget=13000 --dump-dom "file://$T/pebble-app.html" 2>/dev/null | grep -o 'MIGCHECK [^<"]*' | head -1
```
Expected: `MIGCHECK SETS(1) CARDS(3) ID(convo-all)` — the two legacy decks (4 cards, with `Hola`/`hola` deduped) collapsed into one `convo-all` deck of 3 cards.

NOTE: if the app persists under a different storage key than `pebble_data`, this check prints `MIGCHECK SETS(0)...`. In that case, grep the real key first: `grep -oE "storage\\.(get|set)\\(['\"][a-z_]+" "$HOME/Desktop/my projects/pebble/pebble-app.html" | head` and substitute it in both `perl` and the title script. (The migration logic itself is key-agnostic; only this test harness needs the real key.)

- [ ] **Step 4: Commit**

```bash
cd "$HOME/Desktop/my projects/pebble"
git add pebble-app.html
git commit -m "feat(es-flash): migrate legacy per-convo decks into the single Conversación deck on load"
```

---

### Task 4: Real-app verification + WORKLOG

**Files:**
- Modify: `WORKLOG.md`

- [ ] **Step 1: Manual end-to-end check on a phone-width view**

Serve and open at 375px (the project preview convention):
```bash
cd "$HOME/Desktop/my projects/pebble" && python3 -m http.server 8765
```
Then in a 375px browser/iframe: enter Conversación in two separate chat sessions, save a word in each, open Tarjetas in the embedded Veo app. Confirm:
1. There is a single `Conversación` deck button (not one per chat).
2. Both saved words appear inside it.
3. Pre-existing decks from before this change are gone, their cards now inside the single deck.

- [ ] **Step 2: Write the WORKLOG entry**

Append to `WORKLOG.md` using the project template (`## 2026-06-28 — convo flashcards one deck`, Working on / Files changed / Committed / Notes). State that the change is React-side only, no re-bake, committed locally, NOT pushed.

- [ ] **Step 3: Commit**

```bash
cd "$HOME/Desktop/my projects/pebble"
git add WORKLOG.md
git commit -m "docs: WORKLOG — convo flashcards collapsed into one rolling Conversación deck"
```

---

## Self-Review

**Spec coverage:**
- Single fixed deck → Task 1 (constants) + Task 2 (write path). ✓
- Global dedup → falls out of one set; `convoCardKey` + reducer dedup, seeded cache in Task 2. ✓
- Migrate existing decks → Task 1 (`ES_FLASH_MERGE_ALL`) + Task 3 (reactive dispatch). ✓
- Veo side unchanged / no re-bake → stated in Global Constraints; nothing in tasks touches `veo-y-digo-source.html`. ✓
- Toast counter reflects deck total → Task 2 Step 1 (count from seeded `esCardsRef`). ✓

**Placeholder scan:** No TBD/TODO; all code blocks are complete and copy-paste ready. ✓

**Type/name consistency:** `CONVO_DECK_ID` / `CONVO_DECK_LABEL` / `convoCardKey` / `mergeConvoSets` / `ES_FLASH_MERGE_ALL` used identically in Tasks 1-3. Card shape `{kind, es, en}` consistent with the existing reducer's dedup key. ✓

**Known residue:** `esSessionRef` (declared line ~2609) becomes unused after Task 2. Left in place to keep the diff minimal and avoid touching unrelated ref wiring; harmless. Remove later if desired.
