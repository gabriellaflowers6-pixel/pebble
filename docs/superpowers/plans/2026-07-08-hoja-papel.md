# Hoja de Trabajo "Modo Papel" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a paper-style worksheet mode per category in the Veo app's Hoja de Trabajo (word key on top, all questions listed, tap-to-fill), with AI-generated extra questions persisted in Pebble.

**Architecture:** Pebble (parent React app, `pebble-app.html`) is the source of truth and persistence (`data.wsExtra`), the Veo iframe (`veo-y-digo-source.html`) is the display surface — same postMessage pattern as `esLessons`. The Veo source is base64-baked into `pebble-app.html`; every Veo edit ends with a re-bake.

**Tech Stack:** Plain JS + template literals in the Veo source; React (Babel-transformed JSX) + reducer in pebble-app.html. No test framework — verification is the syntax gates (`scratchpad/checkblock.py`, `scratchpad/checkbabel.js`, `scratchpad/rebake.py`) plus functional browser checks with the exact JS snippets given per task.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-08-hoja-papel-design.md`.
- NEVER Read/load `pebble-app.html` (~15MB) or `veo-y-digo-source.html` (~11MB) whole. All edits via python string-replace with `assert src.count(old) == 1`, atomic tmp+rename (see any `python3 - <<'EOF'` edit block below — copy that pattern).
- `@babel/standalone` stays pinned at 7.23.10. Never touch the `window.VEO_DIGO_B64` line by hand — only via `python3 scratchpad/rebake.py "<marker>"`.
- CREDIT RULE: AI generation only on explicit user tap; generated questions cached in Pebble and never regenerated automatically.
- No em dashes/emojis in code comments or generated copy beyond what's specified.
- No `git push` — commits stay local; Gabby OKs any deploy.
- Model for generation: `claude-sonnet-4-6`, headers exactly matching `leccGenerate` (`x-api-key`, `anthropic-version: 2023-06-01`, `anthropic-dangerous-direct-browser-access: true`).
- `leccParseJson` slices the outer `{...}` — AI responses MUST be a JSON OBJECT (`{"exercises":[...]}`), never a bare array.
- Line numbers below are from 2026-07-08 and WILL drift — always grep the given anchor first.

---

### Task 1: Pebble store for generated worksheet questions (`data.wsExtra`)

**Files:**
- Modify: `pebble-app.html` (anchors: `esLessons: {},` in DEFAULT_DATA ~1112; `case 'ES_LESSON_SAVE'` ~1440; `const postLessons` ~5957; `if (d.type === 'esLessonCache')` ~5965)

**Interfaces:**
- Produces (used by Task 3):
  - Parent -> iframe message `{ type: 'wsExtraData', extra: { [catId]: Exercise[] } }`, posted on iframe load and whenever `data.wsExtra` changes.
  - Iframe -> parent message `{ type: 'wsExtra', catId: string, exercises: Exercise[] }` -> reducer `WS_EXTRA_ADD` appends with dedup.
  - `Exercise = { before, blank, after, english, options: string[], answer, why }` (same shape as `wsCategories[].exercises` entries).

- [ ] **Step 1: Add `wsExtra` to DEFAULT_DATA**

```bash
cd ~/dev/pebble && python3 - <<'EOF'
import io, os
p = 'pebble-app.html'
src = io.open(p, encoding='utf-8').read()
old = "  esLessons: {},\n  memory: { pending: [] },"
new = "  esLessons: {},\n  wsExtra: {},\n  memory: { pending: [] },"
assert src.count(old) == 1, src.count(old)
src = src.replace(old, new)
tmp = p + '.tmp'; io.open(tmp,'w',encoding='utf-8').write(src); os.replace(tmp, p)
print('OK')
EOF
```

- [ ] **Step 2: Add the `WS_EXTRA_ADD` reducer case** (insert after the full `ES_LESSON_SAVE` case block; grep `case 'ES_LESSON_SAVE'` and use its closing lines as the anchor)

```bash
cd ~/dev/pebble && python3 - <<'EOF'
import io, os
p = 'pebble-app.html'
src = io.open(p, encoding='utf-8').read()
old = """    case 'ES_LESSON_SAVE': {
      const cur = state.esLessons[action.topicId] || { status: 'new', lesson: null, score: null };
      return { ...state, esLessons: { ...state.esLessons, [action.topicId]: { ...cur, saved: !!action.saved } } };
    }
"""
new = old + """
    case 'WS_EXTRA_ADD': {
      const all = state.wsExtra || {};
      const cur = all[action.catId] || [];
      const key = ex => (ex.before || '') + '|' + (ex.after || '');
      const seen = {}; cur.forEach(ex => { seen[key(ex)] = true; });
      const add = (action.exercises || []).filter(ex => ex && typeof ex.after === 'string' && Array.isArray(ex.options) && ex.answer && !seen[key(ex)]);
      if (!add.length) return state;
      return { ...state, wsExtra: { ...all, [action.catId]: [...cur, ...add] } };
    }
"""
assert src.count(old) == 1, src.count(old)
src = src.replace(old, new)
tmp = p + '.tmp'; io.open(tmp,'w',encoding='utf-8').write(src); os.replace(tmp, p)
print('OK')
EOF
```

- [ ] **Step 3: Post `wsExtraData` into the iframe** (anchor: the `postLessons` effect block)

```bash
cd ~/dev/pebble && python3 - <<'EOF'
import io, os
p = 'pebble-app.html'
src = io.open(p, encoding='utf-8').read()
old = "  React.useEffect(() => { postLessons(); }, [data.esLessons, url, postLessons]);"
new = old + """
  // Push cached AI-generated worksheet questions into the embedded app (paper mode)
  const postWsExtra = React.useCallback(() => {
    try { if (frameRef.current && frameRef.current.contentWindow) frameRef.current.contentWindow.postMessage({ type: 'wsExtraData', extra: data.wsExtra || {} }, '*'); } catch (e) {}
  }, [data.wsExtra]);
  React.useEffect(() => { postWsExtra(); }, [data.wsExtra, url, postWsExtra]);"""
assert src.count(old) == 1, src.count(old)
src = src.replace(old, new)
tmp = p + '.tmp'; io.open(tmp,'w',encoding='utf-8').write(src); os.replace(tmp, p)
print('OK')
EOF
```

- [ ] **Step 4: Handle the `wsExtra` message from the iframe** (anchor: the `esLessonSave` dispatch line inside `onMsg`)

```bash
cd ~/dev/pebble && python3 - <<'EOF'
import io, os
p = 'pebble-app.html'
src = io.open(p, encoding='utf-8').read()
old = "      else if (d.type === 'esLessonSave') dispatch({ type: 'ES_LESSON_SAVE', topicId: d.topicId, saved: d.saved });"
new = old + """
      else if (d.type === 'wsExtra' && d.catId && Array.isArray(d.exercises)) dispatch({ type: 'WS_EXTRA_ADD', catId: d.catId, exercises: d.exercises });"""
assert src.count(old) == 1, src.count(old)
src = src.replace(old, new)
tmp = p + '.tmp'; io.open(tmp,'w',encoding='utf-8').write(src); os.replace(tmp, p)
print('OK')
EOF
```

- [ ] **Step 5: Syntax gate**

Run: `cd ~/dev/pebble && node scratchpad/checkbabel.js pebble-app.html "WS_EXTRA_ADD"`
Expected: `BABEL SYNTAX OK`

- [ ] **Step 6: Functional check (browser).** Serve locally (`python3 -m http.server 8123` in `~/dev/pebble`), open `http://localhost:8123/pebble-app.html`, then in the console:

```js
// simulate the iframe reporting generated questions
window.postMessage({ type:'wsExtra', catId:'tu', exercises:[{before:'',blank:'Te',after:' veo pronto.',english:'I see ___ soon.',options:['Tú','Te','Tu','Ti'],answer:'Te',why:'test'}] }, '*');
setTimeout(() => {
  const d = JSON.parse(localStorage.getItem('pebble-data'));
  console.log('WSEXTRA CHECK', d.wsExtra && d.wsExtra.tu && d.wsExtra.tu.length === 1 ? 'PASS' : 'FAIL', d.wsExtra);
  // dedup: same sentence again must not duplicate
  window.postMessage({ type:'wsExtra', catId:'tu', exercises:[{before:'',blank:'Te',after:' veo pronto.',english:'x',options:['Te'],answer:'Te',why:''}] }, '*');
  setTimeout(() => { const d2 = JSON.parse(localStorage.getItem('pebble-data')); console.log('DEDUP CHECK', d2.wsExtra.tu.length === 1 ? 'PASS' : 'FAIL'); }, 500);
}, 500);
```

Expected: `WSEXTRA CHECK PASS` and `DEDUP CHECK PASS`, no console errors. Then clean up: `localStorage.removeItem('pebble-data')` is NOT safe (wipes her data) — instead remove just the test entry: `const d=JSON.parse(localStorage.getItem('pebble-data')); delete d.wsExtra.tu; localStorage.setItem('pebble-data', JSON.stringify(d));` (only if testing against a browser profile with real data; a fresh headless profile needs no cleanup).

- [ ] **Step 7: Commit**

```bash
cd ~/dev/pebble && git add pebble-app.html && git commit -m "feat(ws-papel): wsExtra store + postMessage plumbing for generated worksheet questions"
```

---

### Task 2: Paper worksheet screen in the Veo app (static questions)

**Files:**
- Modify: `veo-y-digo-source.html` (anchors: `const screens = [` ~4815; `<section class="screen" id="wsRef">` ~735; `.lecc-reset {` end of lecc CSS ~500; `function openWsCategory(){` ~5766)
- Then re-bake into `pebble-app.html`.

**Interfaces:**
- Consumes: `wsCategories` (global array, `{id,label,desc,color,exercises[]}`), `wsRefs` (map catId -> {title, body}), `esc()` (HTML escaper, handles `&<>"` but NOT single quotes), `show(screenId)`, `openWsRef(catId)`, `openWsCategory()`.
- Produces (used by Task 3): globals `wspState` (`{catIdx, answers, open, why, genMsg}`), `wspRender()`, `wspExercises(cat)` (base + `window.__wsExtra[cat.id]`), screen id `'wsPaper'`, placeholder `function wspGenExtra()` (stub in this task).

- [ ] **Step 1: Register the screen.** Python-replace in `veo-y-digo-source.html`:

Old (count==1): `const screens = ['home','flashHome','storyHome','reader','phrase','test','worksheet','wsHome','wsRef','diario','constructor','atajos','escucha','lecciones'];`
New: same list with `'wsPaper'` appended after `'wsRef'`: `...,'wsHome','wsRef','wsPaper','diario',...`

- [ ] **Step 2: Add the section markup.** Insert after the closing `</section>` of `#wsRef` (anchor on the `wsRefBody` div line plus its `</section>`):

Old (count==1):
```html
  <div id="wsRefBody" style="padding:0 20px 60px;font-family:'DM Mono',monospace;font-size:.88rem;line-height:1.8;color:#2a1f15"></div>
</section>
```
New: same plus:
```html

  <!-- ========== WORKSHEET PAPER MODE (modo papel) ========== -->
  <section class="screen" id="wsPaper">
    <div class="reader-nav">
      <button onclick="openWsCategory()">← Categorías</button>
      <span id="wspTitle" style="font-family:'DM Mono',monospace;font-size:.85rem;color:var(--muted)"></span>
      <span></span>
    </div>
    <div id="wspBody" style="padding:0 16px 60px;width:100%;max-width:560px"></div>
  </section>
```

- [ ] **Step 3: Add the CSS.** Insert after the `.lecc-reset { ... }` rule line (grep `.lecc-reset`):

```css
  .wsp-key { background:#fff8ec; border:1.5px solid rgba(42,33,24,0.12); border-radius:12px; padding:12px 14px; margin:10px 0 16px; font-family:'DM Mono',monospace; font-size:0.8rem; line-height:1.7; color:var(--ink); }
  .wsp-key b { color:var(--terracotta); }
  .wsp-q { margin:0 0 16px; font-family:'Fraunces',serif; font-size:1.02rem; line-height:1.6; color:var(--ink); overflow-wrap:break-word; }
  .wsp-num { font-family:'DM Mono',monospace; font-size:0.78rem; color:var(--olive); margin-right:6px; }
  .wsp-blank { display:inline-block; min-width:52px; border-bottom:2px solid rgba(42,33,24,0.4); text-align:center; cursor:pointer; font-weight:700; }
  .wsp-blank.right { color:#3c6e2f; border-color:#5f7a43; }
  .wsp-blank.wrong { color:#c75c3a; border-color:#c75c3a; text-decoration:line-through; }
  .wsp-fix { color:#3c6e2f; font-weight:700; margin-left:6px; }
  .wsp-en { display:block; font-family:'DM Mono',monospace; font-size:0.72rem; color:var(--muted); margin-top:2px; }
  .wsp-opts { display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 4px; }
  .wsp-opts button { padding:8px 16px; border:1.5px solid rgba(42,33,24,0.2); border-radius:999px; background:var(--paper); font-family:'DM Mono',monospace; font-size:0.85rem; cursor:pointer; }
  .wsp-why-b { background:none; border:none; font-family:'DM Mono',monospace; font-size:0.72rem; color:var(--olive); text-decoration:underline; cursor:pointer; padding:2px 0; }
  .wsp-why { font-family:'DM Mono',monospace; font-size:0.78rem; background:#f0ece4; border-radius:8px; padding:10px; margin:6px 0; color:#3a3020; line-height:1.6; }
  .wsp-score { text-align:center; font-family:'Fraunces',serif; font-size:1.1rem; font-weight:700; margin:18px 0 8px; }
  .wsp-actions { display:flex; gap:8px; margin:10px 0 30px; }
  .wsp-actions button { flex:1; }
  .wsp-gen { font-family:'DM Mono',monospace; font-size:0.8rem; border:1.5px solid var(--gold); background:transparent; color:#8a6a1a; border-radius:12px; padding:11px; cursor:pointer; }
  .wsp-rep { font-family:'DM Mono',monospace; font-size:0.8rem; border:1.5px solid var(--terracotta); background:transparent; color:var(--terracotta); border-radius:12px; padding:11px; cursor:pointer; }
  .wsp-divider { font-family:'DM Mono',monospace; font-size:0.66rem; text-transform:uppercase; letter-spacing:0.12em; color:#8a7a62; margin:18px 0 8px; }
  .wsp-msg { font-family:'DM Mono',monospace; font-size:0.75rem; color:#c75c3a; text-align:center; margin:6px 0; }
```

- [ ] **Step 4: Add the JS.** Insert immediately BEFORE `function startWsCategory(idx){` (grep it; count==1):

```js
/* ---- Hoja de trabajo: modo papel ---- */
let wspState = null; // { catIdx, answers:{i:chosen}, open:i|null, why:{i:bool}, genMsg }
window.__wsExtra = window.__wsExtra || {};

function wspExercises(cat){
  const extra = (window.__wsExtra && window.__wsExtra[cat.id]) || [];
  return cat.exercises.concat(extra);
}
function wspKeyHtml(cat){
  const words = [];
  cat.exercises.forEach(ex => (ex.options||[]).forEach(o => { const w = o.toLowerCase(); if (words.indexOf(w) === -1) words.push(w); }));
  const descParts = cat.desc.split('·').map(s => s.trim());
  const rows = words.map((w,i) => '<b>' + esc(w) + '</b>' + (descParts[i] ? ' = ' + esc(descParts[i]) : '')).join('<br>');
  const guia = wsRefs[cat.id] ? '<div style="margin-top:8px"><button class="wsp-why-b" onclick="openWsRef(\'' + cat.id + '\')">ver guía completa 📖</button></div>' : '';
  return '<div class="wsp-key">' + rows + guia + '</div>';
}
function openWsPaper(idx){
  wspState = { catIdx: idx, answers: {}, open: null, why: {}, genMsg: '' };
  document.getElementById('wspTitle').textContent = wsCategories[idx].label;
  show('wsPaper');
  wspRender();
}
function wspRender(){
  const cat = wsCategories[wspState.catIdx];
  const exs = wspExercises(cat);
  const baseCount = cat.exercises.length;
  let html = wspKeyHtml(cat);
  exs.forEach((ex, i) => {
    if (i === baseCount) html += '<div class="wsp-divider">Preguntas nuevas ✦</div>';
    const chosen = wspState.answers[i];
    let blank;
    if (chosen == null) blank = '<span class="wsp-blank" onclick="wspOpen(' + i + ')">&nbsp;</span>';
    else if (chosen === ex.answer) blank = '<span class="wsp-blank right">' + esc(chosen) + '</span>';
    else blank = '<span class="wsp-blank wrong">' + esc(chosen) + '</span><span class="wsp-fix">' + esc(ex.answer) + '</span>';
    html += '<div class="wsp-q"><span class="wsp-num">' + (i+1) + '.</span>' + esc(ex.before||'') + blank + esc(ex.after||'')
      + '<span class="wsp-en">' + esc(ex.english||'') + '</span>';
    if (wspState.open === i) html += '<div class="wsp-opts">' + ex.options.map((o,k) => '<button onclick="wspPick(' + i + ',' + k + ')">' + esc(o) + '</button>').join('') + '</div>';
    if (chosen != null) {
      html += '<button class="wsp-why-b" onclick="wspWhy(' + i + ')">' + (wspState.why[i] ? 'ocultar' : '¿por qué?') + '</button>';
      if (wspState.why[i]) html += '<div class="wsp-why">' + esc(ex.why||'') + '</div>';
    }
    html += '</div>';
  });
  const answered = Object.keys(wspState.answers).length;
  if (exs.length && answered === exs.length) {
    const right = exs.reduce((n,ex,i) => n + (wspState.answers[i] === ex.answer ? 1 : 0), 0);
    html += '<div class="wsp-score">' + right + ' / ' + exs.length + ' correctas</div>';
  }
  html += '<div class="wsp-actions"><button class="wsp-rep" onclick="wspRepeat()">↺ Repetir</button><button class="wsp-gen" id="wspGenBtn" onclick="wspGenExtra()">✦ Más preguntas</button></div>';
  if (wspState.genMsg) html += '<div class="wsp-msg">' + esc(wspState.genMsg) + '</div>';
  document.getElementById('wspBody').innerHTML = html;
}
function wspOpen(i){ wspState.open = (wspState.open === i ? null : i); wspRender(); }
function wspPick(i, k){
  const cat = wsCategories[wspState.catIdx];
  const ex = wspExercises(cat)[i];
  if (!ex || !ex.options[k] || wspState.answers[i] != null) return;
  wspState.answers[i] = ex.options[k];
  wspState.open = null;
  wspRender();
}
function wspWhy(i){ wspState.why[i] = !wspState.why[i]; wspRender(); }
function wspRepeat(){ wspState.answers = {}; wspState.open = null; wspState.why = {}; wspState.genMsg = ''; wspRender(); }
function wspGenExtra(){ /* implemented in Task 3 */ wspState.genMsg = 'Disponible pronto.'; wspRender(); }
```

Note: option picks pass the option INDEX (`wspPick(i,k)`), never the word in a quoted string — avoids all escaping issues with accented words. Answered questions are locked (no re-pick) until Repetir.

- [ ] **Step 5: Add the entry button on the category picker.** Python-replace inside `openWsCategory` (anchor is the `wsRefs[cat.id] ?` template line, count==1). Insert BEFORE the 📖 conditional line:

```js
      <button onclick="openWsPaper(${i})" style="padding:0 14px;background:${cat.color}18;border:2px solid ${cat.color}44;border-radius:12px;cursor:pointer;font-size:1.1rem;flex-shrink:0" title="Hoja (modo papel)">📄</button>
```

- [ ] **Step 6: Gates + re-bake**

Run: `cd ~/dev/pebble && python3 scratchpad/checkblock.py veo-y-digo-source.html wspRender` (or the script's documented invocation; expect `JS SYNTAX OK`), then `python3 scratchpad/rebake.py "wspRender"`.
Expected: `re-bake OK marker-present`.
Then: `node scratchpad/checkbabel.js pebble-app.html "PEBBLE_BUILD"` -> `BABEL SYNTAX OK`.

- [ ] **Step 7: Functional check (browser).** Serve `veo-y-digo-source.html` directly (`http://localhost:8123/veo-y-digo-source.html`), console:

```js
openWsPaper(1); // Tú / Te / Tu category
console.log('SCREEN', document.getElementById('wsPaper').classList.contains('active') || getComputedStyle(document.getElementById('wsPaper')).display !== 'none' ? 'SHOWN' : 'HIDDEN');
console.log('QUESTIONS', document.querySelectorAll('#wspBody .wsp-q').length); // expect 8 (tu category size)
wspOpen(0); console.log('OPTS', document.querySelectorAll('#wspBody .wsp-opts button').length); // expect 4
wspPick(0, 1); console.log('FILLED', document.querySelector('#wspBody .wsp-blank').textContent.trim() !== '');
```

Expected: SHOWN, QUESTIONS 8, OPTS 4, FILLED true, no console errors. Also visually screenshot at 375px width and confirm the key box, numbered list, and buttons render inside the viewport.

- [ ] **Step 8: Commit**

```bash
cd ~/dev/pebble && git add veo-y-digo-source.html pebble-app.html && git commit -m "feat(ws-papel): paper worksheet screen — word key, numbered tap-to-fill list, score, repetir"
```

---

### Task 3: AI-generated extra questions + persistence round-trip (BUILD 21)

**Files:**
- Modify: `veo-y-digo-source.html` (anchors: `window.addEventListener('message', function(e){ if (e && e.data && e.data.type === 'esLessonsData')` ~5364; `function wspGenExtra(){ /* implemented in Task 3 */` from Task 2)
- Modify: `pebble-app.html` (`const PEBBLE_BUILD = 20;` -> 21 + note)
- Re-bake.

**Interfaces:**
- Consumes: Task 1's messages (`wsExtraData` in, `wsExtra` out), Task 2's `wspState`/`wspRender`/`wspExercises`, existing `leccParseJson(text)` (strips fences, slices outer `{...}` — object only), `window.__claudeKey`.
- Produces: working `wspGenExtra()`; `window.__wsExtra` kept in sync with Pebble.

- [ ] **Step 1: Receive `wsExtraData` in the Veo app.** Python-insert after the `esLessonsData` listener line:

```js
window.addEventListener('message', function(e){ if (e && e.data && e.data.type === 'wsExtraData' && e.data.extra && typeof e.data.extra === 'object') { window.__wsExtra = e.data.extra; try { if (typeof currentScreen !== 'undefined' && currentScreen === 'wsPaper' && wspState) wspRender(); } catch(err){} } });
```

- [ ] **Step 2: Replace the `wspGenExtra` stub** (python-replace the whole stub line from Task 2, count==1):

```js
async function wspGenExtra(){
  const cat = wsCategories[wspState.catIdx];
  if (!window.__claudeKey) { wspState.genMsg = 'Agrega tu clave de API en ajustes para generar preguntas.'; wspRender(); return; }
  const btn = document.getElementById('wspGenBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Creando preguntas…'; }
  const exs = wspExercises(cat);
  const existing = exs.map(ex => (ex.before||'') + '___' + (ex.after||'')).join(' | ');
  const prompt = 'You create Spanish fill-in-the-blank exercises for an English speaker (CEFR A1 to B1). Category: "' + cat.label + '" (' + cat.desc + '). '
    + 'Each exercise drills choosing between these words: ' + JSON.stringify(cat.exercises[0].options) + ' (match capitalization to the position in the sentence). '
    + 'Return ONLY valid JSON, no markdown, exactly this shape: {"exercises":[{"before":"text before the blank, may be empty","after":"text after the blank, starts with a space if needed","english":"English translation using ___ for the blank","options":["4 choice words"],"answer":"the correct option, exactly one of options","why":"one or two clear English sentences explaining why"}]} '
    + 'Give 6 exercises. Everyday A1-B1 vocabulary. Do NOT reuse these existing sentences: ' + existing;
  try {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type':'application/json', 'x-api-key': window.__claudeKey, 'anthropic-version':'2023-06-01', 'anthropic-dangerous-direct-browser-access':'true' },
      body: JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 1500, messages: [{ role:'user', content: prompt }] })
    });
    if (!res.ok) throw new Error('api-' + res.status);
    const j = await res.json();
    const text = (j && j.content && j.content[0] && j.content[0].text) || '';
    const obj = leccParseJson(text);
    const good = ((obj && obj.exercises) || []).filter(x => x && typeof x.after === 'string' && Array.isArray(x.options) && x.options.length >= 2 && typeof x.answer === 'string' && x.options.indexOf(x.answer) !== -1)
      .map(x => ({ before: x.before || '', blank: x.answer, after: x.after, english: x.english || '', options: x.options, answer: x.answer, why: x.why || '' }));
    if (!good.length) throw new Error('bad-shape');
    window.__wsExtra[cat.id] = ((window.__wsExtra[cat.id]) || []).concat(good);
    try { window.parent.postMessage({ type:'wsExtra', catId: cat.id, exercises: good }, '*'); } catch(e){}
    wspState.genMsg = '';
  } catch(e){
    wspState.genMsg = 'No se pudo generar. Revisa tu clave o intenta de nuevo.';
  }
  wspRender();
}
```

(`wspRender()` rebuilds the button, so no manual re-enable is needed.)

- [ ] **Step 3: Bump BUILD 20 -> 21.** Python-replace in `pebble-app.html`: `const PEBBLE_BUILD = 20;` -> `= 21;` and set `PEBBLE_BUILD_NOTE` to `'hoja de trabajo: modo papel + preguntas nuevas con IA'`.

- [ ] **Step 4: Gates + re-bake**

Run checkblock on `wspGenExtra`, then `python3 scratchpad/rebake.py "wspGenExtra"` -> `re-bake OK marker-present`, then `node scratchpad/checkbabel.js pebble-app.html "PEBBLE_BUILD"` -> `BABEL SYNTAX OK`.

- [ ] **Step 5: Functional check (browser, no key = graceful path).** Serve `veo-y-digo-source.html`, console:

```js
window.__claudeKey = '';
openWsPaper(1); wspGenExtra();
setTimeout(() => console.log('NOKEY MSG', document.querySelector('.wsp-msg') ? document.querySelector('.wsp-msg').textContent : 'MISSING'), 300);
// simulate parent pushing cached extras
window.postMessage({ type:'wsExtraData', extra: { tu: [{before:'',blank:'Ti',after:' compré esto a ___.',english:'x',options:['Tú','Te','Tu','Ti'],answer:'Ti',why:'w'}] } }, '*');
setTimeout(() => console.log('EXTRA ROWS', document.querySelectorAll('#wspBody .wsp-q').length, 'DIVIDER', !!document.querySelector('.wsp-divider')), 500);
```

Expected: NOKEY MSG shows the key hint; EXTRA ROWS 9 with DIVIDER true. No console errors.

- [ ] **Step 6: Full round-trip check on `pebble-app.html`** (localhost): open Español page -> Hoja de Trabajo -> tap 📄 on a category -> paper sheet renders; in console simulate `window.postMessage({type:'wsExtra',...},'*')` at the TOP window and confirm it lands in `localStorage['pebble-data'].wsExtra` AND, after the postWsExtra effect fires, the iframe shows the extra question (repeat Task 1 Step 6's snippet if needed).

- [ ] **Step 7: Commit + WORKLOG entry**

```bash
cd ~/dev/pebble && git add veo-y-digo-source.html pebble-app.html && git commit -m "feat(ws-papel): Más preguntas AI generation + wsExtra persistence round-trip (BUILD 21)"
```

Append a WORKLOG.md entry (what shipped, commits, verification results, NOT pushed — awaiting Gabby's OK + on-device test) and commit it.

---

## On-device test plan (Gabby, after push OK)

Settings shows BUILD 21. Español -> Hoja de Trabajo -> 📄 on Tú/Te/Tu: key box on top, 8 numbered questions, tap a blank -> 4 chips -> pick -> green/red + ¿por qué?; finish all -> score; ↺ Repetir clears; ✦ Más preguntas (with key set) -> ~6 new questions under "Preguntas nuevas"; close the app fully, reopen, return to the sheet -> the generated questions are still there without any API call.
