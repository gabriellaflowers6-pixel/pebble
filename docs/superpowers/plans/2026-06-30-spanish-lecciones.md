# Spanish "Lecciones" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a structured Spanish lessons feature ("Lecciones") to Pebble: a road-to-fluency checklist, ~10-minute AI-generated lessons per topic that teach grammar and sentence structure plus Duolingo-style practice, hear-aloud and save-to-flashcard on every word and sentence, and a "teach me X" command in the Spanish chat.

**Architecture:** The lesson topic list is a fixed constant baked into the embedded Veo app (`veo-y-digo-source.html`). Lesson content is generated on demand by Claude (reusing the iframe's existing `window.__claudeKey` + `/v1/messages` call), and progress and cached lessons are persisted on the React side in `data.esLessons` (the iframe runs from a blob URL with no durable storage, so React is the source of truth). React posts lesson state into the iframe the same way it already posts `esFlashSets`; the iframe posts cache, progress, and save-card updates back out.

**Tech Stack:** Single-file app. `pebble-app.html` (React via Babel standalone, pinned 7.23.10) hosts the embedded `veo-y-digo-source.html` (vanilla JS) in a blob-URL iframe. Claude API called browser-direct. No build system, no test framework.

## Global Constraints

- No em dashes anywhere in code, comments, UI copy, or commits. Use commas, periods, or restructure.
- No emojis in generated content; no "it's not X, it's Y" phrasing. Natural language.
- `@babel/standalone` stays pinned to `7.23.10`. Do not change.
- API key is device-local (`data.settings.apiKey`, posted to the iframe as `window.__claudeKey`). NEVER bake a key into source.
- Any edit to `veo-y-digo-source.html` MUST be re-baked into `window.VEO_DIGO_B64` in `pebble-app.html` with the round-trip check (see Re-bake procedure). React-side edits in `pebble-app.html` need no re-bake.
- Bump `PEBBLE_BUILD` (const in `pebble-app.html`, currently 12) once, at the final task, for the whole feature.
- Never push or deploy without Gabby's approval.
- If `git ls-files` returns 0 / everything shows deleted (index corruption from the file watcher): `rm -f .git/index.lock; git reset --mixed HEAD`, then recommit. Never `git checkout -f`, `reset --hard`, or `push --force`.

## Testing approach (this project has no unit-test framework)

"Test" in each task means:
1. **Syntax check** the script block you edited with `node --check` (extract the block first; the helper script in Task 0 does this).
2. For Veo-source tasks, **re-bake** and confirm the round-trip passes (decoded bytes equal source, and a unique marker string from your edit is present in the payload).
3. **Browser smoke**: serve locally (`python3 -m http.server 8765`) and load `http://localhost:8765/pebble-app.html` in Chrome; open the named screen and confirm the described behavior and a clean console.

Local-only and read-only until the final on-device step. Nothing deploys.

## postMessage protocol (shared by all tasks)

React (`EspanolPage`) to iframe:
- `{ type: 'esLessonsData', lessons }` where `lessons` is `data.esLessons` (see data model). Posted on iframe load and whenever `data.esLessons` changes, mirroring the existing `esFlashSets` post.

Iframe to React (handled by a listener added in Task 1):
- `{ type: 'esLessonCache', topicId, lesson }` store a generated lesson.
- `{ type: 'esLessonProgress', topicId, status, score }` update progress.
- `{ type: 'saveEsCard', card: { es, en, kind } }` add a card to the Lecciones flashcard deck.

## Data model (React side, `data.esLessons`)

```
data.esLessons = {
  [topicId]: {
    status: 'new' | 'in-progress' | 'done',
    lesson: LessonObject | null,
    score: number | null            // last mini-quiz score, 0..1
  }
}
```

`LessonObject` (the JSON the AI returns and we cache):
```
{
  teach:    string,                              // plain-English rule + sentence structure
  examples: [ { es: string, en: string } ],      // 2-3 example sentences
  pattern:  string,                              // conjugation table / formula, newline-separated
  practice: [ { q: string, options: string[], answer: string, why: string } ],
  quiz:     [ { q: string, options: string[], answer: string, why: string } ]
}
```

The Lecciones flashcard deck reuses the existing `data.esFlash.sets` structure: a themed set with `id: 'lecciones'`, `label: 'Lecciones'`, `themed: true`.

## Topic spine (constant `LECCIONES`, defined in Task 2)

```js
const LECCIONES = [
  { phase: 'Fundamentos', topics: [
    { id:'pronunciacion', label:'Pronunciación y acentos' },
    { id:'genero',        label:'Género y artículos' },
    { id:'concordancia',  label:'Concordancia de adjetivos' },
    { id:'pronombres',    label:'Pronombres de sujeto' },
    { id:'ser-estar',     label:'Ser vs estar' },
    { id:'preguntas',     label:'Preguntas (qué, quién, dónde...)' },
    { id:'negacion',      label:'Negación (no, nada, nunca...)' },
  ]},
  { phase: 'Presente', topics: [
    { id:'presente-reg',  label:'Presente regular (-ar/-er/-ir)' },
    { id:'cambio-radical',label:'Verbos con cambio radical' },
    { id:'irregulares',   label:'Irregulares comunes (tener, ir, hacer...)' },
    { id:'reflexivos',    label:'Verbos reflexivos' },
    { id:'progresivo',    label:'Presente progresivo (estar + -ando)' },
    { id:'gustar',        label:'Gustar y verbos como gustar' },
  ]},
  { phase: 'Pronombres y conectores', topics: [
    { id:'od',            label:'Objeto directo (lo, la, los, las)' },
    { id:'oi',            label:'Objeto indirecto (me, te, le, nos, les)' },
    { id:'dobles',        label:'Doble pronombre (se lo, me lo)' },
    { id:'posesivos',     label:'Posesivos y demostrativos' },
    { id:'por-para',      label:'Por vs para' },
    { id:'preposiciones', label:'Preposiciones comunes (al, del...)' },
  ]},
  { phase: 'Pasado', topics: [
    { id:'preterito',     label:'Pretérito (regular e irregular)' },
    { id:'imperfecto',    label:'Imperfecto' },
    { id:'pret-vs-imp',   label:'Pretérito vs imperfecto' },
    { id:'pres-perfecto', label:'Presente perfecto (he/has...)' },
  ]},
  { phase: 'Futuro y modos', topics: [
    { id:'ir-a',          label:'Ir a + infinitivo (futuro próximo)' },
    { id:'futuro',        label:'Futuro simple' },
    { id:'condicional',   label:'Condicional' },
    { id:'imperativo',    label:'Imperativo (mandatos)' },
    { id:'subjuntivo',    label:'Presente de subjuntivo' },
    { id:'subj-imp',      label:'Imperfecto de subjuntivo' },
    { id:'si-clausulas',  label:'Cláusulas con si' },
  ]},
  { phase: 'Pulido', topics: [
    { id:'se-pasivo',     label:'Se pasivo e impersonal' },
    { id:'relativos',     label:'Cláusulas relativas (que, quien...)' },
    { id:'comparativos',  label:'Comparativos y superlativos' },
    { id:'conectores',    label:'Conectores del discurso' },
  ]},
];
```

---

### Task 0: Re-bake and syntax-check helper scripts

**Files:**
- Create: `scratchpad/rebake.py` (working helper, not committed to the app; lives in the session scratchpad)
- Create: `scratchpad/checkblock.py`

**Interfaces:**
- Produces: a reusable `rebake.py` that re-encodes `veo-y-digo-source.html` into `window.VEO_DIGO_B64` and verifies the round-trip; a `checkblock.py` that extracts the JS block containing a marker and writes it to a temp file for `node --check`.

- [ ] **Step 1: Write `rebake.py`**

```python
# scratchpad/rebake.py  (run from the pebble project dir)
import base64, re, sys
marker = sys.argv[1] if len(sys.argv) > 1 else None
src = open('veo-y-digo-source.html','rb').read()
b64 = base64.b64encode(src).decode('ascii')
app = open('pebble-app.html','r',encoding='utf-8').read()
pat = re.compile(r'window\.VEO_DIGO_B64="[^"]*";')
assert len(pat.findall(app)) == 1, "expected exactly 1 VEO_DIGO_B64 assignment"
app2 = pat.sub('window.VEO_DIGO_B64="'+b64+'";', app, count=1)
emb = re.search(r'window\.VEO_DIGO_B64="([^"]*)";', app2).group(1)
dec = base64.b64decode(emb)
assert dec == src, "ROUND-TRIP FAILED"
if marker:
    assert marker.encode('utf-8') in dec, "marker not found in payload: "+marker
open('pebble-app.html','w',encoding='utf-8').write(app2)
print("re-bake OK", "marker-present" if marker else "", "| src bytes", len(src))
```

- [ ] **Step 2: Write `checkblock.py`**

```python
# scratchpad/checkblock.py FILE MARKER  (extracts the <script> block containing MARKER, node-checks it)
import sys, subprocess
fn, marker = sys.argv[1], sys.argv[2]
src = open(fn, encoding='utf-8').read()
pos = src.find(marker); assert pos != -1, "marker not found: "+marker
start = src.rfind('<script', 0, pos); start = src.find('>', start)+1
end = src.find('</script>', pos)
open('scratchpad/_block.js','w').write(src[start:end])
print(subprocess.run(['node','--check','scratchpad/_block.js'],capture_output=True,text=True).stderr or "JS SYNTAX OK")
```

- [ ] **Step 3: Verify the helpers run against current code**

Run: `python3 scratchpad/checkblock.py veo-y-digo-source.html "function renderCard"`
Expected: `JS SYNTAX OK`

Run: `python3 scratchpad/rebake.py`
Expected: `re-bake OK  | src bytes <n>` (no marker needed here; this confirms current round-trip)

- [ ] **Step 4: Commit (no app change yet, helpers only)**

These live in scratchpad and are gitignored; nothing to commit. Proceed to Task 1.

---

### Task 1: React data layer for lessons (`data.esLessons`) + iframe message bridge

**Files:**
- Modify: `pebble-app.html` (DEFAULT_DATA, the reducer, `EspanolPage`)

**Interfaces:**
- Produces: reducer actions `ES_LESSON_CACHE` ({topicId, lesson}) and `ES_LESSON_PROGRESS` ({topicId, status, score}); `data.esLessons` default `{}`; `EspanolPage` posts `{type:'esLessonsData', lessons}` to the iframe and listens for `esLessonCache`, `esLessonProgress`, and `saveEsCard` messages, dispatching the matching actions. `saveEsCard` adds to the `lecciones` deck via the existing `ES_FLASH_NEW_SET` + `ES_FLASH_ADD_CARD` actions.

- [ ] **Step 1: Add `esLessons` to DEFAULT_DATA**

Find `DEFAULT_DATA` in `pebble-app.html` (search `DEFAULT_DATA = {`). Add a top-level key alongside `esFlash`:

```js
esLessons: {},
```

- [ ] **Step 2: Add reducer cases**

Find the reducer (search `case 'ES_FLASH_ADD_CARD'`). Add, next to the other ES_ cases:

```js
case 'ES_LESSON_CACHE': {
  const cur = state.esLessons[action.topicId] || { status: 'new', lesson: null, score: null };
  return { ...state, esLessons: { ...state.esLessons, [action.topicId]: { ...cur, lesson: action.lesson } } };
}
case 'ES_LESSON_PROGRESS': {
  const cur = state.esLessons[action.topicId] || { status: 'new', lesson: null, score: null };
  return { ...state, esLessons: { ...state.esLessons, [action.topicId]: { ...cur, status: action.status, score: (action.score != null ? action.score : cur.score) } } };
}
```

- [ ] **Step 3: Post lesson state into the iframe (mirror `postSets`)**

In `EspanolPage` (around line 5910, after `postSets`), add:

```js
const postLessons = React.useCallback(() => {
  try { if (frameRef.current && frameRef.current.contentWindow) frameRef.current.contentWindow.postMessage({ type: 'esLessonsData', lessons: data.esLessons || {} }, '*'); } catch (e) {}
}, [data.esLessons]);
React.useEffect(() => { postLessons(); }, [data.esLessons, url, postLessons]);
```

And in the iframe `onLoad` (line ~5928) add `postLessons();` next to `postKey(); postSets();`.

- [ ] **Step 4: Listen for iframe messages and dispatch**

In `EspanolPage`, add (it has `dispatch` via context; if not, pull it from `React.useContext(DataCtx)`):

```js
const { data, dispatch } = React.useContext(DataCtx);  // replace the existing data-only destructure
React.useEffect(() => {
  const onMsg = (e) => {
    const d = e && e.data; if (!d) return;
    if (d.type === 'esLessonCache')    dispatch({ type: 'ES_LESSON_CACHE', topicId: d.topicId, lesson: d.lesson });
    else if (d.type === 'esLessonProgress') dispatch({ type: 'ES_LESSON_PROGRESS', topicId: d.topicId, status: d.status, score: d.score });
    else if (d.type === 'saveEsCard' && d.card && d.card.es) {
      dispatch({ type: 'ES_FLASH_NEW_SET', id: 'lecciones', label: 'Lecciones', date: new Date().toISOString().slice(0,10), themed: true });
      dispatch({ type: 'ES_FLASH_ADD_CARD', setId: 'lecciones', card: { kind: d.card.kind || 'word', es: d.card.es, en: d.card.en || '' } });
    }
  };
  window.addEventListener('message', onMsg);
  return () => window.removeEventListener('message', onMsg);
}, [dispatch]);
```

Confirm `ES_FLASH_NEW_SET` accepts a `themed` flag (it does as of BUILD 10; if its signature differs, pass the flag the same way the FlashEditor's `organizar`/split does).

- [ ] **Step 5: Syntax check**

Run: `python3 scratchpad/checkblock.py pebble-app.html "function EspanolPage"`
Expected: `JS SYNTAX OK`

- [ ] **Step 6: Browser smoke**

Serve and load `pebble-app.html`; open Español. Console clean, iframe loads. In the console run:
`document.querySelector('iframe').contentWindow.postMessage` exists. (Full lesson UI comes later; here we only confirm no errors and the page still works.)

- [ ] **Step 7: Commit**

```bash
git add pebble-app.html
git commit -m "feat(lecciones): React data layer + iframe message bridge for lesson state"
```

---

### Task 2: Lecciones screen scaffold (topic spine + checklist UI + nav)

**Files:**
- Modify: `veo-y-digo-source.html` (the `screens` array, add the screen markup, the home nav entry, the `LECCIONES` constant, a render function, an `esLessonsData` handler)

**Interfaces:**
- Consumes: `show(id)` (line 6001), the `screens` array (line 4733), the existing `.book`/`.mode`/nav styling classes.
- Produces: global `LECCIONES` constant; `window.__esLessons` cache populated from `esLessonsData`; `renderLecciones()` that draws the phased checklist with check marks and a progress bar; `openLeccion(topicId)` (stub here, implemented Task 4); `leccionDeHoy()` that opens the first non-done topic; screen id `'lecciones'`.

- [ ] **Step 1: Register the screen id**

Edit the `screens` array (line 4733) to append `'lecciones'`:

```js
const screens = ['home','flashHome','storyHome','reader','phrase','test','worksheet','wsHome','wsRef','diario','constructor','atajos','escucha','lecciones'];
```

- [ ] **Step 2: Add the `LECCIONES` constant**

Immediately after the `screens` array, paste the full `LECCIONES` constant from the "Topic spine" section above.

- [ ] **Step 3: Add the screen markup**

Find the home screen markup (the element with `id="home"`). Find a sibling screen div (for example `id="diario"`) to copy the wrapper structure. Add a new screen div after the last screen div:

```html
<div class="book screen" id="lecciones">
  <button class="nav-btn back" onclick="show('home')">← inicio</button>
  <h2 class="screen-title">Lecciones</h2>
  <div class="progress" id="leccProgress"></div>
  <button class="mode primary" onclick="leccionDeHoy()">Lección de hoy</button>
  <div id="leccList"></div>
</div>
```

Match the exact class names used by the neighbouring screen you copied (the names above are illustrative; use the real ones from the `diario`/`home` screens so styling is consistent).

- [ ] **Step 4: Add a home entry point**

In the `home` screen markup, find where the other section buttons live (Tarjetas, Oz, Diario, Atajos) and add, in the same button style:

```html
<button class="mode" onclick="show('lecciones'); renderLecciones();">Lecciones</button>
```

- [ ] **Step 5: Add the lessons cache handler (mirror `esFlashSets`)**

Near `applyEsFlashSets` (line 5216), add:

```js
window.__esLessons = {};
function applyEsLessons(l){ try { if (l && typeof l === 'object') { window.__esLessons = l; if (typeof currentScreen !== 'undefined' && currentScreen === 'lecciones') renderLecciones(); } } catch(e){} }
window.addEventListener('message', function(e){ if (e && e.data && e.data.type === 'esLessonsData') applyEsLessons(e.data.lessons); });
```

- [ ] **Step 6: Add `renderLecciones`, `leccionDeHoy`, and an `openLeccion` stub**

Add near the other render functions (for example after `renderCard`):

```js
function leccStatus(id){ return (window.__esLessons[id] && window.__esLessons[id].status) || 'new'; }
function renderLecciones(){
  const list = document.getElementById('leccList');
  let total = 0, done = 0, html = '';
  LECCIONES.forEach(group => {
    html += '<div class="lecc-phase">'+group.phase+'</div>';
    group.topics.forEach(t => {
      total++; const st = leccStatus(t.id); if (st === 'done') done++;
      const mark = st === 'done' ? '✓' : (st === 'in-progress' ? '·' : '');
      html += '<button class="lecc-row" onclick="openLeccion(\''+t.id+'\')"><span class="lecc-mark">'+mark+'</span> '+t.label+'</button>';
    });
  });
  list.innerHTML = html;
  document.getElementById('leccProgress').textContent = done + ' / ' + total + ' completadas';
}
function leccionDeHoy(){
  for (const g of LECCIONES) for (const t of g.topics) if (leccStatus(t.id) !== 'done') { openLeccion(t.id); return; }
  openLeccion(LECCIONES[0].topics[0].id);
}
function openLeccion(topicId){ show('lecciones'); /* full view added in Task 4 */ }
```

- [ ] **Step 7: Add minimal styles for the new classes**

In the Veo `<style>` block (near the `.mode` / `.book` rules), add:

```css
.lecc-phase { font-family:'DM Mono',monospace; font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--olive); margin:16px 0 6px; }
.lecc-row { display:block; width:100%; text-align:left; background:var(--paper); border:1px solid rgba(42,33,24,0.08); border-radius:12px; padding:11px 14px; margin:6px 0; font-size:0.95rem; color:var(--ink); cursor:pointer; }
.lecc-mark { display:inline-block; width:1.1em; color:var(--terracotta); font-weight:700; }
```

- [ ] **Step 8: Syntax check, re-bake, browser smoke**

Run: `python3 scratchpad/checkblock.py veo-y-digo-source.html "function renderLecciones"` (expect `JS SYNTAX OK`)
Run: `python3 scratchpad/rebake.py "function renderLecciones"` (expect `re-bake OK marker-present`)
Browser: Español home shows a "Lecciones" button; tapping it shows the phased checklist with "0 / N completadas" and a "Lección de hoy" button. Console clean.

- [ ] **Step 9: Commit**

```bash
git add veo-y-digo-source.html pebble-app.html
git commit -m "feat(lecciones): screen scaffold, topic spine, checklist UI, nav entry"
```

---

### Task 3: Lesson generator (Claude call + cache)

**Files:**
- Modify: `veo-y-digo-source.html` (add `leccParseJson`, `leccGenerate`, lesson loading state)

**Interfaces:**
- Consumes: `window.__claudeKey`, the existing `fetch('https://api.anthropic.com/v1/messages', ...)` header pattern from `convoCall` (line 5957), `window.__esLessons`.
- Produces: `async leccGenerate(topic)` that returns a `LessonObject`, posts `{type:'esLessonCache', topicId, lesson}` to the parent, and updates `window.__esLessons[topicId].lesson`; `leccParseJson(text)` that strips code fences and parses JSON.

- [ ] **Step 1: Add a JSON parse helper (fence-strip + salvage)**

```js
function leccParseJson(text){
  let t = (text || '').trim();
  t = t.replace(/^```(?:json)?/i,'').replace(/```$/,'').trim();
  const a = t.indexOf('{'), b = t.lastIndexOf('}');
  if (a !== -1 && b !== -1) t = t.slice(a, b+1);
  return JSON.parse(t);
}
```

- [ ] **Step 2: Add the generator**

```js
async function leccGenerate(topic){
  if (!window.__claudeKey) throw new Error('no-key');
  const prompt =
    'You are a Spanish teacher for an English speaker (CEFR A1 to B1). Create a short lesson on: "'
    + topic.label + '". Return ONLY valid JSON, no prose, with this exact shape:\n'
    + '{"teach":"2-4 sentence plain-English explanation of the rule AND the sentence structure",'
    + '"examples":[{"es":"Spanish sentence","en":"English"}],'
    + '"pattern":"the conjugation table or formula, lines separated by \\n",'
    + '"practice":[{"q":"question text (may be English with a Spanish blank)","options":["a","b","c","d"],"answer":"the correct option exactly","why":"one-sentence why in English"}],'
    + '"quiz":[{"q":"...","options":["..."],"answer":"...","why":"..."}]}\n'
    + 'Give 2 or 3 examples, 6 practice items, 4 quiz items. Keep it tight for a 10-minute lesson. No markdown.';
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type':'application/json', 'x-api-key': window.__claudeKey, 'anthropic-version':'2023-06-01', 'anthropic-dangerous-direct-browser-access':'true' },
    body: JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 2000, messages: [{ role:'user', content: prompt }] })
  });
  const j = await res.json();
  const text = (j && j.content && j.content[0] && j.content[0].text) || '';
  const lesson = leccParseJson(text);
  window.__esLessons[topic.id] = window.__esLessons[topic.id] || { status:'new', lesson:null, score:null };
  window.__esLessons[topic.id].lesson = lesson;
  try { window.parent.postMessage({ type:'esLessonCache', topicId: topic.id, lesson: lesson }, '*'); } catch(e){}
  return lesson;
}
function leccTopicById(id){ for (const g of LECCIONES) for (const t of g.topics) if (t.id === id) return t; return null; }
```

- [ ] **Step 3: Syntax check, re-bake**

Run: `python3 scratchpad/checkblock.py veo-y-digo-source.html "async function leccGenerate"` (expect `JS SYNTAX OK`)
Run: `python3 scratchpad/rebake.py "async function leccGenerate"` (expect `re-bake OK marker-present`)

- [ ] **Step 4: Browser smoke (with a key)**

Serve, load, open Settings and paste a working API key. In the console:
```js
const f = document.querySelector('iframe').contentWindow;
f.leccGenerate({id:'futuro', label:'Futuro simple'}).then(l => console.log(l));
```
Expected: an object with `teach`, `examples`, `pattern`, `practice` (6), `quiz` (4). Confirm the parent received `esLessonCache` (check `data.esLessons.futuro.lesson` is set, for example via the app's stored state).

- [ ] **Step 5: Commit**

```bash
git add veo-y-digo-source.html pebble-app.html
git commit -m "feat(lecciones): Claude lesson generator + JSON parse + cache postMessage"
```

---

### Task 4: Lesson view (teach, pattern, practice, mini-quiz, completion)

**Files:**
- Modify: `veo-y-digo-source.html` (replace the `openLeccion` stub, add quiz state + handlers, add a lesson-view container to the `lecciones` screen)

**Interfaces:**
- Consumes: `leccGenerate`, `leccTopicById`, `window.__esLessons`, `leccParseJson`.
- Produces: full `openLeccion(topicId)` that loads-or-generates the lesson and renders it; `leccAnswer(section, i, opt)` that checks an answer and reveals the why; `leccFinishQuiz()` that computes the score, posts `esLessonProgress` with `status:'done'` when the score passes (>= 0.6), and returns to the checklist.

- [ ] **Step 1: Add a lesson-view container to the screen markup**

Inside `<div id="lecciones">`, after `<div id="leccList"></div>`, add a sibling that the view toggles between list and lesson:

```html
<div id="leccView" style="display:none"></div>
```

- [ ] **Step 2: Replace the `openLeccion` stub with the loader + renderer**

```js
let leccState = null; // { topic, lesson, answers:{} }
async function openLeccion(topicId){
  show('lecciones');
  const topic = leccTopicById(topicId); if (!topic) return;
  document.getElementById('leccList').style.display = 'none';
  document.getElementById('leccProgress').style.display = 'none';
  const view = document.getElementById('leccView');
  view.style.display = 'block';
  view.innerHTML = '<p class="lecc-loading">Cargando lección…</p>';
  let lesson = (window.__esLessons[topicId] && window.__esLessons[topicId].lesson) || null;
  if (!lesson) {
    if (!window.__claudeKey) { view.innerHTML = '<p class="lecc-loading">Agrega tu clave de API en ajustes para generar esta lección.</p><button class="mode" onclick="leccBackToList()">← volver</button>'; return; }
    try { lesson = await leccGenerate(topic); }
    catch(e){ view.innerHTML = '<p class="lecc-loading">No se pudo generar la lección. Intenta de nuevo.</p><button class="mode" onclick="leccBackToList()">← volver</button>'; return; }
  }
  leccState = { topic, lesson, answers:{} };
  try { window.parent.postMessage({ type:'esLessonProgress', topicId, status:'in-progress', score:null }, '*'); } catch(e){}
  renderLeccionView();
}
function leccBackToList(){
  document.getElementById('leccView').style.display = 'none';
  document.getElementById('leccList').style.display = 'block';
  document.getElementById('leccProgress').style.display = 'block';
  renderLecciones();
}
function esc(s){ return (''+s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function renderLeccionView(){
  const { topic, lesson } = leccState;
  const view = document.getElementById('leccView');
  let html = '<button class="nav-btn back" onclick="leccBackToList()">← lista</button>';
  html += '<h3 class="lecc-h">'+esc(topic.label)+'</h3>';
  html += '<p class="lecc-teach">'+esc(lesson.teach)+'</p>';
  html += '<div class="lecc-examples">' + (lesson.examples||[]).map((ex,i) =>
      '<div class="lecc-ex"><span class="lecc-es">'+esc(ex.es)+'</span> <button class="lecc-mini" onclick="leccHear('+i+')">oír</button> <button class="lecc-mini" onclick="leccSaveEx('+i+')">guardar</button><br><span class="lecc-en">'+esc(ex.en)+'</span></div>'
    ).join('') + '</div>';
  html += '<pre class="lecc-pattern">'+esc(lesson.pattern)+'</pre>';
  html += '<div class="lecc-h2">Practica</div>';
  html += (lesson.practice||[]).map((q,i) => leccQuestionHtml('practice', q, i)).join('');
  html += '<div class="lecc-h2">Mini examen</div>';
  html += (lesson.quiz||[]).map((q,i) => leccQuestionHtml('quiz', q, i)).join('');
  html += '<button class="mode primary" id="leccFinishBtn" onclick="leccFinishQuiz()">Terminar</button>';
  view.innerHTML = html;
}
function leccQuestionHtml(section, q, i){
  const opts = (q.options||[]).map(o => '<button class="lecc-opt" onclick="leccAnswer(\''+section+'\','+i+',this)" data-opt="'+esc(o)+'">'+esc(o)+'</button>').join('');
  return '<div class="lecc-q" data-section="'+section+'" data-i="'+i+'"><div class="lecc-qtext">'+esc(q.q)+'</div>'+opts+'<div class="lecc-why" style="display:none"></div></div>';
}
function leccAnswer(section, i, btn){
  const q = leccState.lesson[section][i];
  const card = btn.closest('.lecc-q');
  const correct = btn.getAttribute('data-opt') === q.answer;
  leccState.answers[section+'-'+i] = correct;
  card.querySelectorAll('.lecc-opt').forEach(b => { b.disabled = true; if (b.getAttribute('data-opt') === q.answer) b.classList.add('right'); });
  if (!correct) btn.classList.add('wrong');
  const why = card.querySelector('.lecc-why');
  why.textContent = (correct ? 'Correcto. ' : 'La respuesta es "'+q.answer+'". ') + (q.why||'');
  why.style.display = 'block';
}
function leccFinishQuiz(){
  const quiz = leccState.lesson.quiz || [];
  let got = 0; quiz.forEach((q,i) => { if (leccState.answers['quiz-'+i]) got++; });
  const score = quiz.length ? got/quiz.length : 0;
  const status = score >= 0.6 ? 'done' : 'in-progress';
  try { window.parent.postMessage({ type:'esLessonProgress', topicId: leccState.topic.id, status, score }, '*'); } catch(e){}
  if (window.__esLessons[leccState.topic.id]) { window.__esLessons[leccState.topic.id].status = status; window.__esLessons[leccState.topic.id].score = score; }
  const view = document.getElementById('leccView');
  const msg = document.createElement('p'); msg.className = 'lecc-loading';
  msg.textContent = status === 'done' ? ('Lección completa. '+got+' / '+quiz.length) : ('Sigue practicando: '+got+' / '+quiz.length+'. Necesitas 60%.');
  view.appendChild(msg);
  setTimeout(leccBackToList, 1400);
}
```

- [ ] **Step 3: Add lesson-view styles**

```css
.lecc-loading { color:var(--olive); font-size:0.9rem; margin:18px 0; }
.lecc-h { font-family:'Fraunces',serif; font-size:1.3rem; margin:8px 0; color:var(--ink); }
.lecc-h2 { font-family:'DM Mono',monospace; font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--olive); margin:18px 0 6px; }
.lecc-teach { font-size:0.98rem; line-height:1.5; color:var(--ink); margin:8px 0; }
.lecc-ex { margin:8px 0; padding:8px 10px; background:var(--paper); border-radius:10px; }
.lecc-es { font-weight:600; } .lecc-en { color:var(--olive); font-size:0.88rem; }
.lecc-mini { font-size:0.72rem; padding:2px 8px; border:1px solid rgba(42,33,24,0.15); border-radius:999px; background:transparent; cursor:pointer; margin-left:4px; }
.lecc-pattern { white-space:pre-wrap; font-family:'DM Mono',monospace; font-size:0.82rem; background:#fff8ec; border:1px solid rgba(42,33,24,0.08); border-radius:10px; padding:10px; margin:8px 0; }
.lecc-q { margin:12px 0; } .lecc-qtext { font-size:0.95rem; margin-bottom:6px; }
.lecc-opt { display:block; width:100%; text-align:left; margin:4px 0; padding:9px 12px; border:1px solid rgba(42,33,24,0.12); border-radius:10px; background:var(--paper); cursor:pointer; }
.lecc-opt.right { background:#d8e8cf; border-color:#5f7a43; } .lecc-opt.wrong { background:#f3d2cc; border-color:#c75c3a; }
.lecc-why { font-size:0.85rem; color:var(--olive); margin-top:6px; }
```

(Note: `leccHear` and `leccSaveEx` are defined in Task 5; they will be no-ops until then. If running Task 4 standalone in the browser, the "oír"/"guardar" buttons will log a ReferenceError when clicked. That is expected and resolved by Task 5.)

- [ ] **Step 4: Syntax check, re-bake, browser smoke**

Run: `python3 scratchpad/checkblock.py veo-y-digo-source.html "function renderLeccionView"` (expect `JS SYNTAX OK`)
Run: `python3 scratchpad/rebake.py "function renderLeccionView"` (expect `re-bake OK marker-present`)
Browser (with key): Lecciones, tap a topic, wait for generation, confirm teach text, examples, pattern, 6 practice + 4 quiz questions render. Answer questions: correct shows green + why, wrong shows red + correct answer. Tap Terminar: a score message appears and after ~1.4s you return to the checklist with the topic marked (· or ✓). Reopen the same topic: it loads instantly from cache (no regeneration).

- [ ] **Step 5: Commit**

```bash
git add veo-y-digo-source.html pebble-app.html
git commit -m "feat(lecciones): full lesson view with practice, mini-quiz, and completion tracking"
```

---

### Task 5: Hear and save on lesson words and sentences

**Files:**
- Modify: `veo-y-digo-source.html` (add `leccHear`, `leccSaveEx`; add per-word save in examples is optional, sentence-level is required)

**Interfaces:**
- Consumes: `leccState`, the existing `fcSpeak` (line 6109, SpeechSynthesis es, rate 0.85).
- Produces: `leccHear(i)` that speaks `leccState.lesson.examples[i].es`; `leccSaveEx(i)` that posts `{type:'saveEsCard', card:{es, en, kind:'sentence'}}` to the parent and shows a brief confirmation.

- [ ] **Step 1: Add `leccHear` and `leccSaveEx`**

```js
function leccHear(i){ const ex = leccState && leccState.lesson.examples[i]; if (ex && typeof fcSpeak === 'function') fcSpeak(ex.es); }
function leccSaveEx(i){
  const ex = leccState && leccState.lesson.examples[i]; if (!ex) return;
  try { window.parent.postMessage({ type:'saveEsCard', card:{ es: ex.es, en: ex.en || '', kind:'sentence' } }, '*'); } catch(e){}
  const btns = document.querySelectorAll('.lecc-ex'); if (btns[i]) { const tag = document.createElement('span'); tag.className='lecc-saved'; tag.textContent=' guardada'; btns[i].appendChild(tag); setTimeout(()=>{ try{ tag.remove(); }catch(e){} }, 1500); }
}
```

- [ ] **Step 2: Confirm `fcSpeak` is in scope**

`fcSpeak` (line 6109) uses `SpeechSynthesis` with `es-US`/`convoVoice` at rate 0.85. It is a top-level function in the same script, so it is callable from `leccHear`. No change needed; if a future refactor scopes it, fall back to a local `new SpeechSynthesisUtterance(ex.es)` with `lang='es-MX'`, `rate=0.85`.

- [ ] **Step 3: Add `.lecc-saved` style**

```css
.lecc-saved { color:#5f7a43; font-size:0.78rem; }
```

- [ ] **Step 4: Syntax check, re-bake, browser smoke**

Run: `python3 scratchpad/checkblock.py veo-y-digo-source.html "function leccSaveEx"` (expect `JS SYNTAX OK`)
Run: `python3 scratchpad/rebake.py "function leccSaveEx"` (expect `re-bake OK marker-present`)
Browser (with key): open a lesson, tap "oír" on an example (hear the Spanish voice), tap "guardar" (see " guardada"). Then go to Español, Tarjetas: confirm a "Lecciones" deck exists with the saved sentence. Reload the app and confirm the deck persists (it is in `data.esFlash`).

- [ ] **Step 5: Commit**

```bash
git add veo-y-digo-source.html pebble-app.html
git commit -m "feat(lecciones): hear-aloud and save-to-flashcard on lesson examples"
```

---

### Task 6: "teach me X" command in the Spanish chat

**Files:**
- Modify: `pebble-app.html` (`ChatBar`, the Spanish send path `sendSpanish`)

**Interfaces:**
- Consumes: the existing chat `aiCall` helper and `spanishMode`/`esMsgs` state, `data.settings.apiKey`.
- Produces: when a Spanish-chat message matches `/^(teach me|ens[eé]ñame)\b/i`, the reply is a teaching message: a short explanation plus 2-3 examples, rendered in an assistant bubble, instead of the normal conversational reply.

- [ ] **Step 1: Detect the teach intent in `sendSpanish`**

Find `sendSpanish` (search `const sendSpanish`). At the top, after computing `userText`, add:

```js
const teachMatch = userText.match(/^(?:teach me|ens[eé]ñame)\s+(.*)/i);
if (teachMatch) { return teachSpanish(teachMatch[1].trim(), userText); }
```

- [ ] **Step 2: Add `teachSpanish`**

```js
const teachSpanish = async (topic, userText) => {
  const next = [...esMsgs, { role: 'user', es: userText }];
  setEsMsgs(next); setSending(true);
  if (!data.settings?.apiKey) {
    setEsMsgs(prev => [...prev, { role:'assistant', sentences:[{ es:'Agrega tu clave de API en ajustes para aprender.', en:'Add your API key in settings to learn.', words:[] }] }]);
    setSending(false); return;
  }
  const prompt = 'Teach an English speaker this Spanish topic: "' + topic + '". Reply with a short plain-English explanation (2-3 sentences) of the rule and sentence structure, then 2-3 example sentences. Return ONLY JSON: {"teach":"...","examples":[{"es":"...","en":"..."}]}. No markdown.';
  try {
    const text = await aiCall(prompt);
    const data2 = parseJ(text);
    const sentences = [{ es: data2.teach, en: '', words: [] }].concat((data2.examples||[]).map(ex => ({ es: ex.es, en: ex.en, words: [] })));
    setEsMsgs(prev => [...prev, { role:'assistant', sentences, teach:true }]);
    speakSpanish(sentences.map(s => s.es).join(' '));
  } catch(e) {
    setEsMsgs(prev => [...prev, { role:'assistant', sentences:[{ es:'No pude generar la explicación. Intenta de nuevo.', en:'', words:[] }] }]);
  }
  setSending(false);
};
```

Confirm `aiCall` and `parseJ` exist on the chat side (they were added in the BUILD 10 FlashEditor work; if `aiCall` is scoped to `FlashEditor`, lift it to a shared helper or inline the same `fetch` the FlashEditor uses).

- [ ] **Step 3: Syntax check**

Run: `python3 scratchpad/checkblock.py pebble-app.html "function ChatBar"` (expect `JS SYNTAX OK`)

- [ ] **Step 4: Browser smoke (with key)**

Serve, open the Spanish chat, type `teach me the future tense`. Expected: an assistant bubble with a short English explanation and 2-3 Spanish examples, and the existing per-sentence hear/save controls in `SpanishChatBubble` work on them. A normal Spanish message (no "teach me") still behaves as before.

- [ ] **Step 5: Commit**

```bash
git add pebble-app.html
git commit -m "feat(lecciones): 'teach me X' command in Spanish chat"
```

---

### Task 7: Build bump, full re-bake verify, and on-device handoff

**Files:**
- Modify: `pebble-app.html` (`PEBBLE_BUILD`)

- [ ] **Step 1: Bump the build**

In `pebble-app.html`, set `const PEBBLE_BUILD = 13;`.

- [ ] **Step 2: Final re-bake and verify**

Run: `python3 scratchpad/rebake.py "function renderLeccionView"`
Expected: `re-bake OK marker-present`.
Run: `python3 scratchpad/checkblock.py pebble-app.html "function ChatBar"` and `... "function EspanolPage"` (expect `JS SYNTAX OK` for both).

- [ ] **Step 3: Full browser pass**

Serve and run through: Español, Lecciones, Lección de hoy, complete a lesson (practice + quiz), check it off; reopen from cache; hear + save an example; confirm the Lecciones deck in Tarjetas; "teach me X" in chat. Console clean throughout.

- [ ] **Step 4: Update WORKLOG and memory, commit**

Add a WORKLOG entry (BUILD 13, the Lecciones feature, files touched, re-bake done, tested locally, on-device pending). Update the memory note `project_pebble_spanish_app.md` BUILD stamp to 13 and add a one-line Lecciones summary.

```bash
git add pebble-app.html veo-y-digo-source.html WORKLOG.md
git commit -m "feat(lecciones): Spanish lessons feature complete (BUILD 13)"
```

- [ ] **Step 5: On-device handoff (do not push without asking)**

Tell Gabby: confirm Settings shows BUILD 13, then walk the Lecciones flow on her phone. Ask before pushing to Pages.

## Self-Review

**Spec coverage:** new Lecciones screen (Task 2), road-to-fluency checklist with phases and check marks (Task 2), Lección de hoy daily entry (Task 2), ~10-min lesson with teach + pattern + MC practice + mini-quiz (Tasks 3, 4), completion checks the topic off (Task 4), hear + save on words/sentences (Task 5), Lecciones flashcard deck (Tasks 1, 5), hybrid AI generation + device cache (Tasks 1, 3), "teach me X" in chat (Task 6), no-key/offline fallback (Tasks 3, 4), audio via existing voice (Task 5), data model `data.esLessons` (Task 1). All spec sections map to a task.

**Out-of-scope items** (typed answers, build-the-sentence tiles, streaks, spaced repetition, mic speaking) are intentionally not in any task, per the spec.

**Type/name consistency:** message types (`esLessonsData`, `esLessonCache`, `esLessonProgress`, `saveEsCard`) match between Task 1 (React handlers) and Tasks 2-5 (iframe senders). Reducer actions (`ES_LESSON_CACHE`, `ES_LESSON_PROGRESS`) match between Task 1 definition and their dispatch. `LessonObject` fields (`teach`, `examples`, `pattern`, `practice`, `quiz`) match between the generator (Task 3), the renderer (Task 4), and the data model. `leccGenerate`, `leccTopicById`, `leccParseJson`, `openLeccion`, `renderLecciones`, `leccState`, `fcSpeak` names are consistent across tasks.

**Known dependency to verify during execution:** whether `aiCall`/`parseJ` (Task 6) and the `themed` flag on `ES_FLASH_NEW_SET` (Task 1) are reusable as-is from the BUILD 10 work, or need lifting/inlining. Flagged inline in those tasks.
